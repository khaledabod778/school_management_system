"""
واجهة الجداول الدراسية - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta
from datetime import date, time

from app.database.models.users import TeacherSubjectSection
from app.database.session import session_scope
from app.database.models import (
    Grade, Section, Subject, WeeklySchedule,
    MonthlyExamSchedule, FinalExamSchedule, AcademicYear
)
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.services.permission_service import PermissionService
from app.services.schedules_factory import SchedulesFactory
from app.views.widgets.custom_widgets import (
    GradientButton, QDateEditEN, QSpinBoxEN
)
from app.views.widgets.dialogs import ModernDialog
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class SchedulesPage(QWidget):
    """صفحة الجداول الدراسية - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, schedule_type: str = "weekly", 
                 permission_service: Optional[PermissionService] = None, 
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.schedule_type = schedule_type
        self.permission_service = permission_service
        
        # ✅ تخزين البيانات قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        
        self.days = ["السبت", "الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس"]
        self.days_english = ["saturday", "sunday", "monday", "tuesday", "wednesday", "thursday"]
        self.periods = ["الحصة 1", "الحصة 2", "الحصة 3", "الحصة 4", "الحصة 5", "الحصة 6", "الحصة 7"]
        
        # ✅ منع التحميل المزدوج
        self._is_loading = False
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل أولي
        QTimer.singleShot(100, self.load_data)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)
        
        titles = {
            'weekly': 'الجدول المدرسي الأسبوعي',
            'monthly_exam': 'جداول الامتحانات الشهرية',
            'final_exam': 'جداول الامتحانات النهائية',
        }
        
        title = QLabel(titles.get(self.schedule_type, 'الجداول'))
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #0F172A;")
        main_layout.addWidget(title)
        
        # بطاقة الفلاتر
        filter_card = QFrame()
        filter_card.setObjectName("filterCard")
        filter_card.setStyleSheet("""
            QFrame#filterCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setSpacing(10)
        
        filter_layout.addWidget(QLabel("الصف:"))
        self.grade_combo = QComboBox()
        self.grade_combo.setMinimumWidth(150)
        self.grade_combo.currentIndexChanged.connect(self._on_grade_changed)
        filter_layout.addWidget(self.grade_combo)
        
        filter_layout.addWidget(QLabel("الشعبة:"))
        self.section_combo = QComboBox()
        self.section_combo.setMinimumWidth(100)
        self.section_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.section_combo)
        
        # فلاتر إضافية
        if self.schedule_type in ['weekly', 'monthly_exam', 'final_exam']:
            filter_layout.addWidget(QLabel("الفصل:"))
            self.term_combo = QComboBox()
            self.term_combo.addItems(["الأول", "الثاني"])
            self.term_combo.currentIndexChanged.connect(self._on_filter_changed)
            filter_layout.addWidget(self.term_combo)
        
        if self.schedule_type == 'monthly_exam':
            filter_layout.addWidget(QLabel("الشهر:"))
            self.month_combo = QComboBox()
            self.month_combo.addItems(["الأول", "الثاني", "الثالث"])
            self.month_combo.currentIndexChanged.connect(self._on_filter_changed)
            filter_layout.addWidget(self.month_combo)
        
        filter_layout.addStretch()
        
        edit_btn = GradientButton("تعديل الجدول", "fa5s.edit")
        edit_btn.clicked.connect(self.edit_schedule)
        filter_layout.addWidget(edit_btn)

        print_btn = GradientButton("طباعة", "fa5s.print")
        print_btn.setObjectName("successButton")
        print_btn.clicked.connect(self.print_schedule)
        filter_layout.addWidget(print_btn)        
        
        main_layout.addWidget(filter_card)
        
        # بطاقة الجدول
        table_card = QFrame()
        table_card.setObjectName("tableCard")
        table_card.setStyleSheet("""
            QFrame#tableCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        card_layout = QVBoxLayout(table_card)
        
        self._setup_table_by_type()
        card_layout.addWidget(self.schedule_table)
        
        main_layout.addWidget(table_card)
    
    def _setup_table_by_type(self):
        """إعداد الجدول حسب النوع."""
        self.schedule_table = QTableWidget()
        
        if self.schedule_type == 'weekly':
            self.schedule_table.setColumnCount(len(self.days) + 1)
            self.schedule_table.setHorizontalHeaderLabels(["الحصة"] + self.days)
            self.schedule_table.setRowCount(len(self.periods))
            for row, period in enumerate(self.periods):
                self.schedule_table.setItem(row, 0, QTableWidgetItem(period))
                self.schedule_table.setRowHeight(row, 35)
            self.schedule_table.setColumnWidth(0, 100)
            for col in range(1, len(self.days) + 1):
                self.schedule_table.setColumnWidth(col, 150)
        
        elif self.schedule_type == 'monthly_exam':
            self.schedule_table.setColumnCount(4)
            self.schedule_table.setHorizontalHeaderLabels(["المادة", "اليوم", "التاريخ", "الحصة"])
            self.schedule_table.setColumnWidth(0, 200)
            self.schedule_table.setColumnWidth(1, 150)
            self.schedule_table.setColumnWidth(2, 150)
            self.schedule_table.setColumnWidth(3, 100)
        
        elif self.schedule_type == 'final_exam':
            self.schedule_table.setColumnCount(5)
            self.schedule_table.setHorizontalHeaderLabels([
                "المادة", "اليوم", "التاريخ", "وقت البداية", "وقت النهاية"
            ])
            self.schedule_table.setColumnWidth(0, 200)
            self.schedule_table.setColumnWidth(1, 150)
            self.schedule_table.setColumnWidth(2, 150)
            self.schedule_table.setColumnWidth(3, 150)
            self.schedule_table.setColumnWidth(4, 150)
        
        self.schedule_table.horizontalHeader().setStretchLastSection(True)
        self.schedule_table.verticalHeader().setVisible(False)
        self.schedule_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.schedule_table.setAlternatingRowColors(True)
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_data(self):
        """تحميل الصفوف - Local أو Remote."""
        self.loading_overlay.show_loading("جاري تحميل الصفوف...")

        def _fetch_data():
            if SchedulesFactory.is_remote():
                from app.services.student_factory import StudentFactory
                service = StudentFactory.get_service()
                return service.list_grades()
            with session_scope() as session:
                grades = session.execute(
                    select(Grade).order_by(Grade.grade_name)
                ).scalars().all()
                return [
                    {'id': g.id, 'name': g.grade_name or ''}
                    for g in grades
                ]

        def _on_result(data):
            try:
                self.grade_combo.blockSignals(True)
                self.grade_combo.clear()
                for grade in data:
                    self.grade_combo.addItem(
                        grade.get('name', grade.get('grade_name', '')),
                        grade['id']
                    )
                self.grade_combo.blockSignals(False)
                if data:
                    self._on_grade_changed()
            except Exception as e:
                print(f"خطأ: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            print(f"فشل تحميل الصفوف: {error_msg}")

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
        
    def _on_grade_changed(self):
        """عند تغيير الصف."""
        grade_id = self.grade_combo.currentData()
        if grade_id:
            self._load_sections(grade_id)
    
    def _on_filter_changed(self):
        """عند تغيير أي فلتر آخر."""
        self.load_schedule()
    
    def _load_sections(self, grade_id: int):
        """تحميل الشعب - Local أو Remote."""
        self.loading_overlay.show_loading("جاري تحميل الشعب...")

        def _fetch_data():
            if SchedulesFactory.is_remote():
                from app.services.student_factory import StudentFactory
                service = StudentFactory.get_service()
                sections = service.list_sections(grade_id=grade_id)
                return [
                    {'id': s['id'], 'name': s.get('name', '')}
                    for s in sections
                ]
            with session_scope() as session:
                sections = session.execute(
                    select(Section)
                    .where(Section.grade_id == grade_id)
                    .order_by(Section.section_name)
                ).scalars().all()
                return [
                    {'id': s.id, 'name': s.section_name or ''}
                    for s in sections
                ]

        def _on_result(data):
            try:
                self.section_combo.blockSignals(True)
                self.section_combo.clear()
                for section in data:
                    self.section_combo.addItem(
                        section['name'], section['id']
                    )
                self.section_combo.blockSignals(False)
                self.load_schedule()
            except Exception as e:
                print(f"خطأ: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            print(f"فشل تحميل الشعب: {error_msg}")

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)

    def load_schedule(self):
        """تحميل الجدول - Local أو Remote."""
        grade_id = self.grade_combo.currentData()
        section_id = self.section_combo.currentData()

        if not grade_id:
            return
        if self._is_loading:
            return

        self._is_loading = True
        self.loading_overlay.show_loading("جاري تحميل الجدول...")

        schedule_type = self.schedule_type
        term = (
            self.term_combo.currentIndex() + 1
            if hasattr(self, 'term_combo') else 1
        )
        month = (
            self.month_combo.currentIndex() + 1
            if hasattr(self, 'month_combo') else 1
        )
        academic_year_id = self.academic_year_id

        def _fetch_data():
            if SchedulesFactory.is_remote():
                service = SchedulesFactory.get_service()
                if schedule_type == 'weekly':
                    if not section_id:
                        return {'type': 'weekly', 'data': []}
                    result = service.get_weekly(
                        section_id=section_id,
                        academic_year_id=academic_year_id,
                        term=term,
                    )
                    return {
                        'type': 'weekly',
                        'data': result.get('schedules', []),
                    }
                elif schedule_type == 'monthly_exam':
                    if not section_id:
                        return {'type': 'monthly', 'data': []}
                    return {
                        'type': 'monthly',
                        'data': service.get_monthly_exam(
                            section_id=section_id,
                            academic_year_id=academic_year_id,
                            term=term,
                            month=month,
                        ),
                    }
                else:
                    return {
                        'type': 'final',
                        'data': service.get_final_exam(
                            grade_id=grade_id,
                            academic_year_id=academic_year_id,
                            term=term,
                        ),
                    }

            # Local (الكود القديم)
            with session_scope() as session:
                if schedule_type == 'weekly':
                    if not section_id:
                        return {'type': 'weekly', 'data': []}
                    schedules = session.execute(
                        select(WeeklySchedule, Subject)
                        .join(Subject, WeeklySchedule.subject_id == Subject.id)
                        .where(
                            WeeklySchedule.section_id == section_id,
                            WeeklySchedule.academic_year_id == academic_year_id,
                            WeeklySchedule.term == term
                        )
                    ).all()
                    return {
                        'type': 'weekly',
                        'data': [
                            {
                                'day_of_week': s.day_of_week,
                                'period_number': s.period_number,
                                'subject_name': sub.subject_name or '',
                            }
                            for s, sub in schedules
                        ]
                    }
                elif schedule_type == 'monthly_exam':
                    if not section_id:
                        return {'type': 'monthly', 'data': []}
                    schedules = session.execute(
                        select(MonthlyExamSchedule, Subject)
                        .join(Subject, MonthlyExamSchedule.subject_id == Subject.id)
                        .where(
                            MonthlyExamSchedule.section_id == section_id,
                            MonthlyExamSchedule.academic_year_id == academic_year_id,
                            MonthlyExamSchedule.term == term,
                            MonthlyExamSchedule.month == month
                        )
                        .order_by(MonthlyExamSchedule.exam_date)
                    ).all()
                    return {
                        'type': 'monthly',
                        'data': [
                            {
                                'subject_name': sub.subject_name or '',
                                'day_name': s.day_name or '',
                                'exam_date_str': (
                                    s.exam_date.strftime("%Y/%m/%d")
                                    if s.exam_date else ''
                                ),
                                'period_number': s.period_number or 0,
                            }
                            for s, sub in schedules
                        ]
                    }
                else:
                    schedules = session.execute(
                        select(FinalExamSchedule, Subject)
                        .join(Subject, FinalExamSchedule.subject_id == Subject.id)
                        .where(
                            FinalExamSchedule.grade_id == grade_id,
                            FinalExamSchedule.academic_year_id == academic_year_id,
                            FinalExamSchedule.term == term
                        )
                        .order_by(FinalExamSchedule.exam_date)
                    ).all()
                    return {
                        'type': 'final',
                        'data': [
                            {
                                'subject_name': sub.subject_name or '',
                                'day_name': s.day_name or '',
                                'exam_date_str': (
                                    s.exam_date.strftime("%Y/%m/%d")
                                    if s.exam_date else ''
                                ),
                                'start_time_str': (
                                    s.start_time.strftime("%H:%M")
                                    if s.start_time else ''
                                ),
                                'end_time_str': (
                                    s.end_time.strftime("%H:%M")
                                    if s.end_time else ''
                                ),
                            }
                            for s, sub in schedules
                        ]
                    }

        def _on_result(data):
            try:
                if data['type'] == 'weekly':
                    self._display_weekly(data['data'])
                elif data['type'] == 'monthly':
                    self._display_monthly(data['data'])
                else:
                    self._display_final(data['data'])
            except Exception as e:
                print(f"خطأ في تحديث الواجهة: {str(e)}")
            finally:
                self._is_loading = False
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self._is_loading = False
            self.loading_overlay.hide_loading()
            print(f"فشل تحميل الجدول: {error_msg}")

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)

    # ============================================================
    # ✅ عرض الجداول
    # ============================================================
    
    def _display_weekly(self, data: List[Dict]):
        """عرض الجدول الأسبوعي."""
        # مسح الخلايا
        for row in range(len(self.periods)):
            for col in range(1, len(self.days) + 1):
                self.schedule_table.setItem(row, col, QTableWidgetItem(""))
        
        day_map = {d: i + 1 for i, d in enumerate(self.days_english)}
        
        for item in data:
            col = day_map.get(item['day_of_week'], 0)
            row = item['period_number'] - 1
            if 0 <= row < len(self.periods) and 0 < col <= len(self.days):
                table_item = QTableWidgetItem(item['subject_name'])
                table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table_item.setBackground(QColor('#EEF2FF'))
                table_item.setForeground(QColor('#0D47A1'))
                self.schedule_table.setItem(row, col, table_item)
    
    def _display_monthly(self, data: List[Dict]):
        """عرض جدول الامتحانات الشهرية."""
        self.schedule_table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            self.schedule_table.setItem(row, 0, QTableWidgetItem(item['subject_name']))
            self.schedule_table.setItem(row, 1, QTableWidgetItem(item['day_name']))
            self.schedule_table.setItem(row, 2, QTableWidgetItem(item['exam_date_str']))
            self.schedule_table.setItem(
                row, 3, QTableWidgetItem(f"الحصة {item['period_number']}")
            )
            self.schedule_table.setRowHeight(row, 40)
    
    def _display_final(self, data: List[Dict]):
        """عرض جدول الامتحانات النهائية."""
        self.schedule_table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            self.schedule_table.setItem(row, 0, QTableWidgetItem(item['subject_name']))
            self.schedule_table.setItem(row, 1, QTableWidgetItem(item['day_name']))
            self.schedule_table.setItem(row, 2, QTableWidgetItem(item['exam_date_str']))
            self.schedule_table.setItem(row, 3, QTableWidgetItem(item['start_time_str']))
            self.schedule_table.setItem(row, 4, QTableWidgetItem(item['end_time_str']))
            self.schedule_table.setRowHeight(row, 40)
    
    # ============================================================
    # ✅ التعديل
    # ============================================================
    
    def edit_schedule(self):
        """فتح نافذة التعديل."""
        if self.permission_service and not self.permission_service.can_edit("الجداول الدراسية"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للتعديل في الجداول الدراسية"
            )
            return

        grade_id = self.grade_combo.currentData()
        section_id = self.section_combo.currentData()
        
        if not grade_id:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار الصف")
            return
        
        # ✅ استخدام academic_year_id بدلاً من الكائن
        if self.schedule_type == 'weekly':
            if not section_id:
                QMessageBox.warning(self, "تنبيه", "يرجى اختيار الشعبة")
                return
            dialog = WeeklyScheduleDialog(
                self.academic_year_id, grade_id, section_id, parent=self
            )
        elif self.schedule_type == 'monthly_exam':
            if not section_id:
                QMessageBox.warning(self, "تنبيه", "يرجى اختيار الشعبة")
                return
            dialog = MonthlyExamScheduleDialog(
                self.academic_year_id, grade_id, section_id, parent=self
            )
        elif self.schedule_type == 'final_exam':
            dialog = FinalExamScheduleDialog(
                self.academic_year_id, grade_id, parent=self
            )
        else:
            return
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_schedule()
            QMessageBox.information(self, "نجاح", "تم حفظ الجدول بنجاح")

    def print_schedule(self):
        """طباعة الجدول."""
        if self.permission_service and not self.permission_service.can_print("الجداول الدراسية"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للطباعة في الجداول الدراسية"
            )
            return

        QMessageBox.information(
            self, "طباعة",
            "سيتم تنفيذ الطباعة في مرحلة التقارير"
        )
    
    # ============================================================
    # ✅ الأحداث
    # ============================================================
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())
    
    def refresh(self):
        self.load_data()


# ============================================================
# ✅ الحوارات (مع dicts + إصلاح N+1)
# ============================================================

class WeeklyScheduleDialog(ModernDialog):
    """نافذة تعديل الجدول الأسبوعي."""
    
    def __init__(self, academic_year_id: int, grade_id: int, 
                 section_id: int, parent=None):
        super().__init__(
            "تعديل الجدول الأسبوعي",
            "fa5s.calendar-week",
            parent,
            width=880,
            height=600
        )
        # ✅ IDs فقط
        self.academic_year_id = academic_year_id
        self.grade_id = grade_id
        self.section_id = section_id
        
        self.days_english = ["saturday", "sunday", "monday", "tuesday", "wednesday", "thursday"]
        self.days_arabic = ["السبت", "الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس"]
        
        # ✅ dicts
        self.subjects_data: List[Dict] = []
        self.existing_schedules: Dict = {}  # {(day, period): subject_id}
        
        self.setup_ui()
        
        # ✅ تحميل أولي
        QTimer.singleShot(50, self.load_all)
    
    def setup_ui(self):
        term_layout = QHBoxLayout()
        label = QLabel("الفصل الدراسي:")
        label.setStyleSheet("color: #475569; font-weight: 600; font-size: 12px;")
        term_layout.addWidget(label)

        self.term_combo = QComboBox()
        self.term_combo.addItems(["الأول", "الثاني"])
        self.term_combo.currentIndexChanged.connect(self.load_all)
        term_layout.addWidget(self.term_combo)
        term_layout.addStretch()
        self.add_layout(term_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.days_arabic) + 1)
        self.table.setHorizontalHeaderLabels(["الحصة"] + self.days_arabic)
        self.table.setRowCount(7)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        for row in range(7):
            self.table.setItem(row, 0, QTableWidgetItem(f"الحصة {row + 1}"))
            self.table.setRowHeight(row, 43)
        self.table.setColumnWidth(0, 80)
        for col in range(1, 7):
            self.table.setColumnWidth(col, 120)

        self.add_widget(self.table)

        self.add_button("حفظ الجدول", self.save_schedule, "primary")
        self.add_button("إلغاء", self.reject, "default")

    def load_all(self):
        """تحميل المواد والجدول - Local أو Remote."""
        term = self.term_combo.currentIndex() + 1
        academic_year_id = self.academic_year_id
        grade_id = self.grade_id
        section_id = self.section_id

        def _fetch_data():
            if SchedulesFactory.is_remote():
                service = SchedulesFactory.get_service()
                subjects = service.subjects_for_grade(
                    grade_id=grade_id,
                    academic_year_id=academic_year_id,
                )
                schedule_result = service.get_weekly(
                    section_id=section_id,
                    academic_year_id=academic_year_id,
                    term=term,
                )
                existing = {
                    (s['day_of_week'], s['period_number']): s['subject_id']
                    for s in schedule_result.get('schedules', [])
                }
                return {'subjects': subjects, 'existing': existing}

            # Local
            with session_scope() as session:
                subjects = session.execute(
                    select(Subject)
                    .select_from(TeacherSubjectSection)
                    .join(Subject, TeacherSubjectSection.subject_id == Subject.id)
                    .where(
                        TeacherSubjectSection.grade_id == grade_id,
                        TeacherSubjectSection.academic_year_id == academic_year_id
                    )
                    .distinct()
                    .order_by(Subject.subject_name)
                ).scalars().all()

                subjects_data = [
                    {'id': s.id, 'name': s.subject_name or ''}
                    for s in subjects
                ]

                schedules = session.execute(
                    select(WeeklySchedule).where(
                        WeeklySchedule.section_id == section_id,
                        WeeklySchedule.academic_year_id == academic_year_id,
                        WeeklySchedule.term == term
                    )
                ).scalars().all()

                existing = {}
                for s in schedules:
                    existing[(s.day_of_week, s.period_number)] = s.subject_id

                return {'subjects': subjects_data, 'existing': existing}

        def _on_result(data):
            try:
                self.subjects_data = data['subjects']
                self.existing_schedules = data['existing']

                for row in range(7):
                    for col in range(1, 7):
                        combo = QComboBox()
                        combo.addItem("", None)
                        for s in self.subjects_data:
                            combo.addItem(s['name'], s['id'])

                        day_key = self.days_english[col - 1]
                        period_key = row + 1
                        if (day_key, period_key) in self.existing_schedules:
                            subject_id = self.existing_schedules[
                                (day_key, period_key)
                            ]
                            idx = combo.findData(subject_id)
                            if idx >= 0:
                                combo.setCurrentIndex(idx)

                        self.table.setCellWidget(row, col, combo)
            except Exception as e:
                print(f"خطأ: {str(e)}")

        run_async(_fetch_data, on_result=_on_result)

    def save_schedule(self):
        """حفظ الجدول - Local أو Remote."""
        term = self.term_combo.currentIndex() + 1
        academic_year_id = self.academic_year_id
        grade_id = self.grade_id
        section_id = self.section_id

        records = []
        for row in range(7):
            for col in range(1, 7):
                combo = self.table.cellWidget(row, col)
                if isinstance(combo, QComboBox) and combo.currentData():
                    records.append({
                        'day_of_week': self.days_english[col - 1],
                        'period_number': row + 1,
                        'subject_id': combo.currentData(),
                    })

        try:
            if SchedulesFactory.is_remote():
                service = SchedulesFactory.get_service()
                service.save_weekly({
                    'academic_year_id': academic_year_id,
                    'grade_id': grade_id,
                    'section_id': section_id,
                    'term': term,
                    'records': records,
                })
            else:
                self._save_local(
                    records, academic_year_id, grade_id,
                    section_id, term
                )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل الحفظ: {str(e)}")

    def _save_local(self, records, academic_year_id, grade_id,
                     section_id, term):
        with session_scope() as session:
            old = session.execute(
                select(WeeklySchedule).where(
                    WeeklySchedule.section_id == section_id,
                    WeeklySchedule.academic_year_id == academic_year_id,
                    WeeklySchedule.term == term
                )
            ).scalars().all()
            for s in old:
                session.delete(s)
            session.flush()

            for r in records:
                session.add(WeeklySchedule(
                    academic_year_id=academic_year_id,
                    term=term,
                    grade_id=grade_id,
                    section_id=section_id,
                    day_of_week=r['day_of_week'],
                    period_number=r['period_number'],
                    subject_id=r['subject_id']
                ))
            session.commit()


class MonthlyExamScheduleDialog(ModernDialog):
    """نافذة جدول الامتحانات الشهرية."""
    
    def __init__(self, academic_year_id: int, grade_id: int, 
                 section_id: int, parent=None):
        super().__init__(
            "تعديل جدول الامتحانات الشهرية",
            "fa5s.calendar-check",
            parent,
            width=700,
            height=600
        )
        # ✅ IDs فقط
        self.academic_year_id = academic_year_id
        self.grade_id = grade_id
        self.section_id = section_id
        
        self.days_arabic = ["السبت", "الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس"]
        
        # ✅ dicts
        self.subjects_data: List[Dict] = []
        self.existing_schedules: Dict = {}  # {subject_id: {...}}
        
        self.setup_ui()
        
        # ✅ تحميل أولي
        QTimer.singleShot(50, self.load_all)
    
    def setup_ui(self):        
        fl = QHBoxLayout()
        fl.addWidget(QLabel("الفصل:"))
        self.term_combo = QComboBox()
        self.term_combo.addItems(["الأول", "الثاني"])
        self.term_combo.currentIndexChanged.connect(self.load_all)
        fl.addWidget(self.term_combo)
        fl.addWidget(QLabel("الشهر:"))
        self.month_combo = QComboBox()
        self.month_combo.addItems(["الأول", "الثاني", "الثالث"])
        self.month_combo.currentIndexChanged.connect(self.load_all)
        fl.addWidget(self.month_combo)
        fl.addStretch()
        self.add_layout(fl)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["المادة", "التاريخ", "اليوم", "الحصة"])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 130)
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(3, 100)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.add_widget(self.table)

        self.add_button("حفظ الجدول", self.save_schedule, "primary")
        self.add_button("إلغاء", self.reject, "default")

    def load_all(self):
        """تحميل المواد والجدول - Local أو Remote."""
        term = self.term_combo.currentIndex() + 1
        month = self.month_combo.currentIndex() + 1
        academic_year_id = self.academic_year_id
        grade_id = self.grade_id
        section_id = self.section_id

        def _fetch_data():
            if SchedulesFactory.is_remote():
                service = SchedulesFactory.get_service()
                subjects = service.subjects_for_grade(
                    grade_id=grade_id,
                    academic_year_id=academic_year_id,
                )
                exams = service.get_monthly_exam(
                    section_id=section_id,
                    academic_year_id=academic_year_id,
                    term=term,
                    month=month,
                )
                existing = {}
                for e in exams:
                    existing[e['subject_id']] = {
                        'exam_date': e.get('exam_date'),
                        'day_name': e.get('day_name', ''),
                        'period_number': e.get('period_number', 1),
                    }
                return {'subjects': subjects, 'existing': existing}

            # Local
            with session_scope() as session:
                subjects = session.execute(
                    select(Subject)
                    .select_from(TeacherSubjectSection)
                    .join(Subject, TeacherSubjectSection.subject_id == Subject.id)
                    .where(
                        TeacherSubjectSection.grade_id == grade_id,
                        TeacherSubjectSection.academic_year_id == academic_year_id
                    )
                    .distinct()
                    .order_by(Subject.subject_name)
                ).scalars().all()

                subjects_data = [
                    {'id': s.id, 'name': s.subject_name or ''}
                    for s in subjects
                ]

                schedules = session.execute(
                    select(MonthlyExamSchedule).where(
                        MonthlyExamSchedule.section_id == section_id,
                        MonthlyExamSchedule.academic_year_id == academic_year_id,
                        MonthlyExamSchedule.term == term,
                        MonthlyExamSchedule.month == month
                    )
                ).scalars().all()

                existing = {}
                for s in schedules:
                    existing[s.subject_id] = {
                        'exam_date': s.exam_date,
                        'day_name': s.day_name or '',
                        'period_number': s.period_number or 1,
                    }

                return {'subjects': subjects_data, 'existing': existing}

        def _on_result(data):
            try:
                self.subjects_data = data['subjects']
                self.existing_schedules = data['existing']

                self.table.setRowCount(len(self.subjects_data))

                for row, subject in enumerate(self.subjects_data):
                    self.table.setItem(row, 0, QTableWidgetItem(subject['name']))

                    date_input = QDateEditEN()
                    self.table.setCellWidget(row, 1, date_input)

                    day_combo = QComboBox()
                    day_combo.addItems(self.days_arabic)
                    self.table.setCellWidget(row, 2, day_combo)

                    period_spin = QSpinBoxEN(1, 7)
                    self.table.setCellWidget(row, 3, period_spin)

                    if subject['id'] in self.existing_schedules:
                        existing = self.existing_schedules[subject['id']]

                        ed = existing.get('exam_date')
                        if ed:
                            # قد يكون str (من API) أو date (من Local)
                            if isinstance(ed, str):
                                try:
                                    from datetime import date as _date
                                    ed = _date.fromisoformat(ed)
                                except Exception:
                                    ed = None
                            if ed:
                                date_input.setDate(QDate(
                                    ed.year, ed.month, ed.day
                                ))

                        if existing.get('day_name'):
                            day_combo.setCurrentText(existing['day_name'])

                        period_spin.setValue(existing.get('period_number', 1))

                    self.table.setRowHeight(row, 43)
            except Exception as e:
                print(f"خطأ: {str(e)}")

        run_async(_fetch_data, on_result=_on_result)

    def save_schedule(self):
        """حفظ الجدول - Local أو Remote."""
        term = self.term_combo.currentIndex() + 1
        month = self.month_combo.currentIndex() + 1
        academic_year_id = self.academic_year_id
        grade_id = self.grade_id
        section_id = self.section_id

        records = []
        for row in range(self.table.rowCount()):
            subject_id = self.subjects_data[row]['id']
            date_input = self.table.cellWidget(row, 1)
            day_combo = self.table.cellWidget(row, 2)
            period_spin = self.table.cellWidget(row, 3)

            if all(isinstance(w, (QDateEdit, QComboBox, QSpinBox))
                   for w in [date_input, day_combo, period_spin]):
                d = date_input.date()
                records.append({
                    'subject_id': subject_id,
                    'exam_date': date(
                        d.year(), d.month(), d.day()
                    ).isoformat(),
                    'day_name': day_combo.currentText(),
                    'period_number': period_spin.value(),
                })

        try:
            if SchedulesFactory.is_remote():
                service = SchedulesFactory.get_service()
                service.save_monthly_exam({
                    'academic_year_id': academic_year_id,
                    'grade_id': grade_id,
                    'section_id': section_id,
                    'term': term,
                    'month': month,
                    'records': records,
                })
            else:
                self._save_local(
                    records, academic_year_id, grade_id,
                    section_id, term, month
                )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل الحفظ: {str(e)}")

    def _save_local(self, records, academic_year_id, grade_id,
                     section_id, term, month):
        with session_scope() as session:
            old = session.execute(
                select(MonthlyExamSchedule).where(
                    MonthlyExamSchedule.section_id == section_id,
                    MonthlyExamSchedule.academic_year_id == academic_year_id,
                    MonthlyExamSchedule.term == term,
                    MonthlyExamSchedule.month == month
                )
            ).scalars().all()
            for s in old:
                session.delete(s)
            session.flush()

            for r in records:
                session.add(MonthlyExamSchedule(
                    academic_year_id=academic_year_id,
                    term=term,
                    month=month,
                    grade_id=grade_id,
                    section_id=section_id,
                    subject_id=r['subject_id'],
                    exam_date=date.fromisoformat(r['exam_date']),
                    day_name=r['day_name'],
                    period_number=r['period_number']
                ))
            session.commit()


class FinalExamScheduleDialog(ModernDialog):
    """نافذة جدول الامتحانات النهائية."""
    
    def __init__(self, academic_year_id: int, grade_id: int, parent=None):
        super().__init__(
            "تعديل جدول الامتحانات النهائية",
            "fa5s.calendar-alt",
            parent,
            width=790,
            height=600
        )
        # ✅ IDs فقط
        self.academic_year_id = academic_year_id
        self.grade_id = grade_id
        
        self.days_arabic = ["السبت", "الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس"]
        
        # ✅ dicts
        self.subjects_data: List[Dict] = []
        self.existing_schedules: Dict = {}
        
        self.setup_ui()
        
        # ✅ تحميل أولي
        QTimer.singleShot(50, self.load_all)
    
    def setup_ui(self):
        fl = QHBoxLayout()
        fl.addWidget(QLabel("الفصل:"))
        self.term_combo = QComboBox()
        self.term_combo.addItems(["الأول", "الثاني"])
        self.term_combo.currentIndexChanged.connect(self.load_all)
        fl.addWidget(self.term_combo)
        fl.addStretch()
        self.add_layout(fl)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["المادة", "التاريخ", "اليوم", "البداية", "النهاية"])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 130)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 140)
        self.table.setColumnWidth(4, 140)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.add_widget(self.table)

        self.add_button("حفظ الجدول", self.save_schedule, "primary")
        self.add_button("إلغاء", self.reject, "default")
    
    def load_all(self):
        """تحميل المواد والجدول - Local أو Remote."""
        term = self.term_combo.currentIndex() + 1
        academic_year_id = self.academic_year_id
        grade_id = self.grade_id

        def _fetch_data():
            if SchedulesFactory.is_remote():
                service = SchedulesFactory.get_service()
                subjects = service.subjects_for_grade(
                    grade_id=grade_id,
                    academic_year_id=academic_year_id,
                )
                exams = service.get_final_exam(
                    grade_id=grade_id,
                    academic_year_id=academic_year_id,
                    term=term,
                )
                existing = {}
                for e in exams:
                    existing[e['subject_id']] = {
                        'exam_date': e.get('exam_date'),
                        'day_name': e.get('day_name', ''),
                        'start_time': e.get('start_time'),
                        'end_time': e.get('end_time'),
                    }
                return {'subjects': subjects, 'existing': existing}

            # Local
            with session_scope() as session:
                subjects = session.execute(
                    select(Subject)
                    .select_from(TeacherSubjectSection)
                    .join(Subject, TeacherSubjectSection.subject_id == Subject.id)
                    .where(
                        TeacherSubjectSection.grade_id == grade_id,
                        TeacherSubjectSection.academic_year_id == academic_year_id
                    )
                    .distinct()
                    .order_by(Subject.subject_name)
                ).scalars().all()

                subjects_data = [
                    {'id': s.id, 'name': s.subject_name or ''}
                    for s in subjects
                ]

                schedules = session.execute(
                    select(FinalExamSchedule).where(
                        FinalExamSchedule.grade_id == grade_id,
                        FinalExamSchedule.academic_year_id == academic_year_id,
                        FinalExamSchedule.term == term
                    )
                ).scalars().all()

                existing = {}
                for s in schedules:
                    existing[s.subject_id] = {
                        'exam_date': s.exam_date,
                        'day_name': s.day_name or '',
                        'start_time': s.start_time,
                        'end_time': s.end_time,
                    }

                return {'subjects': subjects_data, 'existing': existing}

        def _on_result(data):
            try:
                self.subjects_data = data['subjects']
                self.existing_schedules = data['existing']

                self.table.setRowCount(len(self.subjects_data))

                for row, subject in enumerate(self.subjects_data):
                    self.table.setItem(row, 0, QTableWidgetItem(subject['name']))

                    date_input = QDateEditEN()
                    self.table.setCellWidget(row, 1, date_input)

                    day_combo = QComboBox()
                    day_combo.addItems(self.days_arabic)
                    self.table.setCellWidget(row, 2, day_combo)

                    start_time = QTimeEdit()
                    start_time.setTime(QTime(8, 0))
                    start_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    start_time.setLocale(QLocale(
                        QLocale.Language.English,
                        QLocale.Country.UnitedStates
                    ))
                    self.table.setCellWidget(row, 3, start_time)

                    end_time = QTimeEdit()
                    end_time.setTime(QTime(10, 0))
                    end_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    end_time.setLocale(QLocale(
                        QLocale.Language.English,
                        QLocale.Country.UnitedStates
                    ))
                    self.table.setCellWidget(row, 4, end_time)

                    if subject['id'] in self.existing_schedules:
                        existing = self.existing_schedules[subject['id']]

                        ed = existing.get('exam_date')
                        if ed:
                            if isinstance(ed, str):
                                try:
                                    from datetime import date as _date
                                    ed = _date.fromisoformat(ed)
                                except Exception:
                                    ed = None
                            if ed:
                                date_input.setDate(QDate(
                                    ed.year, ed.month, ed.day
                                ))

                        if existing.get('day_name'):
                            day_combo.setCurrentText(existing['day_name'])

                        # start/end وقت
                        st = existing.get('start_time')
                        if st:
                            h, m = self._parse_hhmm(st)
                            start_time.setTime(QTime(h, m))

                        et = existing.get('end_time')
                        if et:
                            h, m = self._parse_hhmm(et)
                            end_time.setTime(QTime(h, m))

                    self.table.setRowHeight(row, 43)
            except Exception as e:
                print(f"خطأ: {str(e)}")

        run_async(_fetch_data, on_result=_on_result)

    def _parse_hhmm(self, v):
        """يحوّل time أو 'HH:MM' إلى (h, m)."""
        if hasattr(v, 'hour'):
            return v.hour, v.minute
        try:
            h, m = str(v).split(':')
            return int(h), int(m)
        except Exception:
            return 8, 0
        
    def save_schedule(self):
        """حفظ الجدول - Local أو Remote."""
        term = self.term_combo.currentIndex() + 1
        academic_year_id = self.academic_year_id
        grade_id = self.grade_id

        records = []
        for row in range(self.table.rowCount()):
            subject_id = self.subjects_data[row]['id']
            date_input = self.table.cellWidget(row, 1)
            day_combo = self.table.cellWidget(row, 2)
            start_input = self.table.cellWidget(row, 3)
            end_input = self.table.cellWidget(row, 4)

            if all(isinstance(w, (QDateEdit, QComboBox, QTimeEdit))
                   for w in [date_input, day_combo, start_input, end_input]):
                d = date_input.date()
                st = start_input.time()
                et = end_input.time()

                records.append({
                    'subject_id': subject_id,
                    'exam_date': date(
                        d.year(), d.month(), d.day()
                    ).isoformat(),
                    'day_name': day_combo.currentText(),
                    'start_time': f"{st.hour():02d}:{st.minute():02d}",
                    'end_time': f"{et.hour():02d}:{et.minute():02d}",
                })

        try:
            if SchedulesFactory.is_remote():
                service = SchedulesFactory.get_service()
                service.save_final_exam({
                    'academic_year_id': academic_year_id,
                    'grade_id': grade_id,
                    'term': term,
                    'records': records,
                })
            else:
                self._save_local(
                    records, academic_year_id, grade_id, term
                )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل الحفظ: {str(e)}")

    def _save_local(self, records, academic_year_id, grade_id, term):
        with session_scope() as session:
            old = session.execute(
                select(FinalExamSchedule).where(
                    FinalExamSchedule.grade_id == grade_id,
                    FinalExamSchedule.academic_year_id == academic_year_id,
                    FinalExamSchedule.term == term
                )
            ).scalars().all()
            for s in old:
                session.delete(s)
            session.flush()

            for r in records:
                st_h, st_m = r['start_time'].split(':')
                et_h, et_m = r['end_time'].split(':')
                session.add(FinalExamSchedule(
                    academic_year_id=academic_year_id,
                    term=term,
                    grade_id=grade_id,
                    subject_id=r['subject_id'],
                    exam_date=date.fromisoformat(r['exam_date']),
                    day_name=r['day_name'],
                    start_time=time(int(st_h), int(st_m)),
                    end_time=time(int(et_h), int(et_m))
                ))
            session.commit()