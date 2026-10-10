"""
واجهة تسجيل الحضور والغياب اليومي - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Dict, Optional
import qtawesome as qta
from datetime import date, datetime

from app.database.session import session_scope
from app.database.models import (
    Student, Grade, Section, DailyAttendance, AcademicYear
)
from app.services.operations_factory import OperationsFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    PageHeader, Card, QDateEditEN, SearchBox, ModernTable, Badge, GradientButton
)
from app.views.widgets.dialogs import (
    ConfirmationDialog, SuccessDialog, ErrorDialog
)
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select, func


class AttendancePage(QWidget):
    """صفحة تسجيل الحضور والغياب - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ تخزين ID السنة قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        
        # ✅ dicts بدلاً من ORM
        self.attendance_data: Dict[int, Dict] = {}
        self.current_students: List[Dict] = []
        
        # ✅ منع التحميل المتزامن
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
        main_layout.setSpacing(10)

        # رأس الصفحة
        title = QLabel("تسجيل الحضور والغياب")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("تسجيل حضور الطلاب اليومي مع دعم التنقل السريع")
        subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(subtitle)

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
        
        # اختيار الصف
        filter_layout.addWidget(QLabel("الصف:"))
        self.grade_combo = QComboBox()
        self.grade_combo.setMinimumWidth(150)
        self.grade_combo.currentIndexChanged.connect(self._on_grade_changed)
        filter_layout.addWidget(self.grade_combo)
        
        # اختيار الشعبة
        filter_layout.addWidget(QLabel("الشعبة:"))
        self.section_combo = QComboBox()
        self.section_combo.setMinimumWidth(100)
        self.section_combo.currentIndexChanged.connect(self._on_section_changed)
        filter_layout.addWidget(self.section_combo)
        
        # اختيار التاريخ
        filter_layout.addWidget(QLabel("التاريخ:"))
        self.date_input = QDateEditEN()
        self.date_input.dateChanged.connect(self._on_date_changed)
        filter_layout.addWidget(self.date_input)
        
        filter_layout.addStretch()
        
        # زر جعل الكل حاضرين
        all_present_btn = GradientButton("الكل حاضر", "fa5s.user-check")
        all_present_btn.setObjectName("successButton")
        all_present_btn.clicked.connect(self.mark_all_present)
        filter_layout.addWidget(all_present_btn)
        
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
        # شريط الأدوات
        toolbar = QHBoxLayout()
        
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            color: #000000; 
            font-weight: 600; 
            padding: 8px 15px;
            border: 2px solid #1976D3;
            border-radius: 10px;
        """)          
        toolbar.addWidget(self.stats_label)
        
        toolbar.addStretch()
        
        save_btn = GradientButton("حفظ", "fa5s.save")
        save_btn.clicked.connect(self.save_attendance)
        toolbar.addWidget(save_btn)
        
        print_btn = GradientButton("طباعة", "fa5s.print")
        print_btn.setObjectName("successButton")
        print_btn.clicked.connect(self.print_attendance)
        toolbar.addWidget(print_btn)
        
        card_layout.addLayout(toolbar)
        
        # الجدول
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "رقم الطالب", "اسم الطالب", "الحالة", "ملاحظات"
        ])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 200)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)        
        card_layout.addWidget(self.table)
        
        main_layout.addWidget(table_card)
    
    # ============================================================
    # ✅ التحميل غير المتزامن - البيانات الأولية
    # ============================================================
    
    def load_data(self):
        """تحميل قائمة الصفوف - Local أو Remote."""
        self.loading_overlay.show_loading("جاري تحميل الصفوف...")

        def _fetch_data():
            # ✅ Remote
            if OperationsFactory.is_remote():
                from app.services.student_factory import StudentFactory
                service = StudentFactory.get_service()
                grades = service.list_grades()
                return [
                    {
                        'id': g['id'],
                        'name': g.get('grade_name', g.get('name', '')),
                    }
                    for g in grades
                ]

            # Local
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
                    self.grade_combo.addItem(grade['name'], grade['id'])
                self.grade_combo.blockSignals(False)

                if data:
                    self._on_grade_changed()
            except Exception as e:
                print(f"خطأ: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            ErrorDialog(
                "خطأ",
                f"فشل تحميل الصفوف:\n{error_msg}",
                self
            ).exec()

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
        
    # ============================================================
    # ✅ معالجات التغيير
    # ============================================================
    
    def _on_grade_changed(self):
        """عند تغيير الصف - تحميل الشعب."""
        grade_id = self.grade_combo.currentData()
        if not grade_id:
            return
        
        self._load_sections(grade_id)
    
    def _on_section_changed(self):
        """عند تغيير الشعبة - تحميل الطلاب."""
        self.load_students()
    
    def _on_date_changed(self):
        """عند تغيير التاريخ - تحميل الطلاب."""
        self.load_students()
    
    def _load_sections(self, grade_id: int):
        """تحميل الشعب - Local أو Remote."""
        self.loading_overlay.show_loading("جاري تحميل الشعب...")

        def _fetch_data():
            # ✅ Remote
            if OperationsFactory.is_remote():
                from app.services.student_factory import StudentFactory
                service = StudentFactory.get_service()
                sections = service.list_sections(grade_id=grade_id)
                return [
                    {'id': s['id'], 'name': s.get('name', '')}
                    for s in sections
                ]

            # Local
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

                self.load_students()
            except Exception as e:
                print(f"خطأ: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            print(f"فشل تحميل الشعب: {error_msg}")

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)

    # ============================================================
    # ✅ تحميل الطلاب والحضور (Async)
    # ============================================================
    
    def load_students(self):
        """تحميل الطلاب + الحضور المسجل - Local أو Remote."""
        grade_id = self.grade_combo.currentData()
        section_id = self.section_combo.currentData()
        attendance_date = self.date_input.date().toPython()

        if not all([grade_id, section_id]):
            self.table.setRowCount(0)
            self.update_stats()
            return

        if self._is_loading:
            return

        self._is_loading = True
        self.loading_overlay.show_loading("جاري تحميل الطلاب...")

        academic_year_id = self.academic_year_id

        def _fetch_data():
            # ✅ Remote
            if OperationsFactory.is_remote():
                service = OperationsFactory.get_service()
                return service.get_attendance(
                    academic_year_id=academic_year_id,
                    grade_id=grade_id,
                    section_id=section_id,
                    attendance_date=attendance_date.isoformat(),
                )

            # Local (السلوك القديم)
            with session_scope() as session:
                students = session.execute(
                    select(Student)
                    .where(
                        Student.grade_id == grade_id,
                        Student.section_id == section_id,
                        Student.academic_year_id == academic_year_id,
                        Student.status == 'مستمر'
                    )
                    .order_by(Student.full_name)
                ).scalars().all()

                students_data = [
                    {
                        'id': s.id,
                        'student_number': s.student_number or '',
                        'full_name': s.full_name or '',
                    }
                    for s in students
                ]

                existing_attendance = session.execute(
                    select(DailyAttendance)
                    .where(
                        DailyAttendance.attendance_date == attendance_date,
                        DailyAttendance.grade_id == grade_id,
                        DailyAttendance.section_id == section_id,
                        DailyAttendance.academic_year_id == academic_year_id
                    )
                ).scalars().all()

                attendance_map = {}
                for att in existing_attendance:
                    attendance_map[att.student_id] = {
                        'id': att.id,
                        'status': att.status or 'حاضر',
                        'notes': att.notes or '',
                    }

                return {
                    'students': students_data,
                    'attendance': attendance_map,
                }

        def _on_result(data):
            try:
                self.current_students = data['students']
                
                attendance_map = {a['id']: a for a in data['attendance']}
                self.attendance_data = attendance_map

                self._display_students(data['students'], attendance_map)

            except Exception as e:
                print(f"خطأ في تحديث الواجهة: {str(e)}")
            finally:
                self._is_loading = False
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self._is_loading = False
            self.loading_overlay.hide_loading()
            print(f"فشل تحميل الطلاب: {error_msg}")

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)

    # ============================================================
    # ✅ عرض الطلاب
    # ============================================================
    
    def _display_students(self, students: List[Dict], attendance_map: Dict):
        """عرض الطلاب في الجدول."""
        # ✅ منع الإشارات أثناء الإعداد
        self.table.blockSignals(True)
        
        self.table.setRowCount(len(students))
        
        for row, student in enumerate(students):
            self.table.setItem(
                row, 0, QTableWidgetItem(student['student_number'])
            )
            self.table.setItem(
                row, 1, QTableWidgetItem(student['full_name'])
            )
            
            # قائمة الحالة
            status_combo = QComboBox()
            status_combo.addItems(['حاضر', 'غائب', 'متأخر', 'غائب بمبرر'])
            
            # ✅ استرجاع الحالة المسجلة (المفاتيح int الآن)
            if student['id'] in attendance_map:
                saved_status = attendance_map[student['id']]['status']
                # ضبط القيمة بدون إطلاق signal بعد (نفعّله بعد التنسيق)
                status_combo.blockSignals(True)
                status_combo.setCurrentText(saved_status)
                status_combo.blockSignals(False)

            # ✅ ربط signal لتحديث اللون عند التغيير
            status_combo.currentTextChanged.connect(
                lambda text, c=status_combo: self._style_status_combo(c)
            )

            # ✅ تطبيق اللون الأولي
            self._style_status_combo(status_combo)

            self.table.setCellWidget(row, 2, status_combo)
            
            # حقل الملاحظات
            notes_input = QLineEdit()
            notes_input.setPlaceholderText("ملاحظات...")
            
            if student['id'] in attendance_map:
                notes_input.setText(attendance_map[student['id']]['notes'])
            
            self.table.setCellWidget(row, 3, notes_input)
            self.table.setRowHeight(row, 45)
        
        self.table.blockSignals(False)
        self.update_stats()
    
    # ============================================================
    # ✅ العمليات
    # ============================================================
    
    def mark_all_present(self):
        """جعل جميع الطلاب حاضرين."""
        # ✅ blockSignals لمنع استدعاء update_stats مئات المرات
        self.table.blockSignals(True)
        
        for row in range(self.table.rowCount()):
            combo = self.table.cellWidget(row, 2)
            if isinstance(combo, QComboBox):
                combo.blockSignals(True)
                combo.setCurrentText('حاضر')
                combo.blockSignals(False)
        
        self.table.blockSignals(False)
        self.update_stats()
    
    def update_stats(self):
        """تحديث الإحصائيات."""
        total = self.table.rowCount()
        present = 0
        absent = 0
        late = 0
        excused = 0
        
        for row in range(total):
            combo = self.table.cellWidget(row, 2)
            if isinstance(combo, QComboBox):
                status = combo.currentText()
                if status == 'حاضر':
                    present += 1
                elif status == 'غائب':
                    absent += 1
                elif status == 'متأخر':
                    late += 1
                elif status == 'غائب بمبرر':
                    excused += 1
        
        self.stats_label.setText(
            f"الإجمالي: {total} | حاضر: {present} | غائب: {absent} | "
            f"متأخر: {late} | غائب بممبرر: {excused}"
        )

    def _style_status_combo(self, combo: QComboBox):
        """تطبيق لون على QComboBox حسب الحالة الحالية."""
        status = combo.currentText()
        colors = {
            'حاضر': ('#10B981', '#059669'),
            'غائب': ('#EF4444', '#DC2626'),
            'متأخر': ('#F59E0B', '#D97706'),
            'غائب بمبرر': ('#3B82F6', '#2563EB'),
        }
        border, color = colors.get(status, ('#E2E8F0', '#64748B'))
        combo.setStyleSheet(f"""
            QComboBox {{
                background: white;
                border: 2px solid {border};
                border-radius: 6px;
                padding: 5px;
                min-width: 100px;
                color: {color};
                font-weight: 600;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
        """)

    # ============================================================
    # ✅ حفظ الحضور (Async)
    # ============================================================
    
    def save_attendance(self):
        """حفظ بيانات الحضور - Local أو Remote."""
        if self.permission_service and not self.permission_service.can_add("الحضور والغياب"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للإضافة في الحضور والغياب"
            )
            return

        if self.table.rowCount() == 0:
            ErrorDialog("تنبيه", "لا يوجد طلاب للحفظ", self).exec()
            return

        attendance_date = self.date_input.date().toPython()
        grade_id = self.grade_combo.currentData()
        section_id = self.section_combo.currentData()

        attendance_records = []
        for row in range(self.table.rowCount()):
            if row >= len(self.current_students):
                continue

            student_id = self.current_students[row]['id']
            status_combo = self.table.cellWidget(row, 2)
            notes_input = self.table.cellWidget(row, 3)

            if not isinstance(status_combo, QComboBox):
                continue

            attendance_records.append({
                'student_id': student_id,
                'status': status_combo.currentText(),
                'notes': notes_input.text() if isinstance(notes_input, QLineEdit) else '',
            })

        if not attendance_records:
            ErrorDialog("تنبيه", "لا توجد بيانات للحفظ", self).exec()
            return

        reply = QMessageBox.question(
            self, "تأكيد الحفظ",
            f"هل تريد حفظ الحضور لتاريخ {attendance_date.strftime('%Y/%m/%d')}؟\n\n"
            f"عدد الطلاب: {len(attendance_records)}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.loading_overlay.show_loading("جاري حفظ الحضور...")
        academic_year_id = self.academic_year_id

        def _save_data():
            # ✅ Remote
            if OperationsFactory.is_remote():
                service = OperationsFactory.get_service()
                result = service.save_attendance({
                    'academic_year_id': academic_year_id,
                    'grade_id': grade_id,
                    'section_id': section_id,
                    'attendance_date': attendance_date.isoformat(),
                    'records': attendance_records,
                })
                return result.get('saved', len(attendance_records))

            # Local
            with session_scope() as session:
                existing = session.execute(
                    select(DailyAttendance).where(
                        DailyAttendance.attendance_date == attendance_date,
                        DailyAttendance.grade_id == grade_id,
                        DailyAttendance.section_id == section_id,
                        DailyAttendance.academic_year_id == academic_year_id
                    )
                ).scalars().all()
                for att in existing:
                    session.delete(att)
                session.flush()

                saved = 0
                for rec in attendance_records:
                    session.add(DailyAttendance(
                        student_id=rec['student_id'],
                        academic_year_id=academic_year_id,
                        grade_id=grade_id,
                        section_id=section_id,
                        attendance_date=attendance_date,
                        status=rec['status'],
                        notes=rec['notes'] or None,
                    ))
                    saved += 1
                session.commit()
                return saved

        def _on_result(saved_count):
            self.loading_overlay.hide_loading()
            SuccessDialog(
                "نجاح",
                f"تم حفظ حضور {saved_count} طالب بنجاح",
                self
            ).exec()
            self.load_students()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(
                self, "خطأ",
                f"فشل حفظ البيانات:\n{error_msg}"
            )

        run_async(_save_data, on_result=_on_result, on_error=_on_error)
        
    # ============================================================
    # ✅ الطباعة
    # ============================================================
    
    def print_attendance(self):
        """طباعة كشف الحضور."""
        if self.permission_service and not self.permission_service.can_print("الحضور والغياب"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للطباعة في الحضور والغياب"
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
        """تحديث حجم طبقة التحميل."""
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())
    
    def refresh(self):
        """إعادة تحميل البيانات."""
        self.load_data()