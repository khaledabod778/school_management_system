"""
واجهة رصد الدرجات والنتائج - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Dict, Optional
import qtawesome as qta
from datetime import date
from decimal import Decimal

from app.database.models.users import TeacherSubjectSection
from app.database.session import session_scope
from app.database.models import (
    Student, Grade, Section, Subject, MonthlyEvaluation, 
    TermExamScore, AcademicYear
)
from app.services.grades_factory import GradesFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    PageHeader, Card, ModernTable, GradientButton, QDoubleSpinBoxEN
)
from app.views.widgets.dialogs import (
    SuccessDialog, ErrorDialog
)
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select


class GradesPage(QWidget):
    """صفحة رصد الدرجات - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ تخزين ID السنة قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        
        # ✅ dicts
        self.existing_scores: Dict[int, Dict] = {}  # {student_id: {...}}
        self.current_students: List[Dict] = []  # الطلاب المعروضين حالياً
        
        # ✅ منع إعادة التحميل أثناء تعديل المستخدم
        self._is_loading = False
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل أولي
        QTimer.singleShot(100, self.load_initial_data)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)

        # رأس الصفحة
        title = QLabel("رصد الدرجات والنتائج")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("رصد التقييمات الشهرية ودرجات نهاية الفصل")
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
        
        # نوع الرصد
        filter_layout.addWidget(QLabel("نوع الرصد:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["التقييمات الشهرية", "درجات نهاية الفصل"])
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        filter_layout.addWidget(self.type_combo)
        
        # الصف
        filter_layout.addWidget(QLabel("الصف:"))
        self.grade_combo = QComboBox()
        self.grade_combo.currentIndexChanged.connect(self._on_grade_changed)
        filter_layout.addWidget(self.grade_combo)
        
        # الشعبة
        filter_layout.addWidget(QLabel("الشعبة:"))
        self.section_combo = QComboBox()
        self.section_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.section_combo)
        
        # المادة
        filter_layout.addWidget(QLabel("المادة:"))
        self.subject_combo = QComboBox()
        self.subject_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.subject_combo)
        
        # الفصل الدراسي
        filter_layout.addWidget(QLabel("الفصل:"))
        self.term_combo = QComboBox()
        self.term_combo.addItems(["الأول", "الثاني"])
        self.term_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.term_combo)
        
        # الشهر (للتقييمات الشهرية)
        self.month_label = QLabel("الشهر:")
        filter_layout.addWidget(self.month_label)
        self.month_combo = QComboBox()
        self.month_combo.addItems(["الأول", "الثاني", "الثالث"])
        self.month_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.month_combo)
        
        filter_layout.addStretch()
        
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
        
        self.info_label = QLabel()
        self.info_label.setStyleSheet("""
            color: #000000; 
            font-weight: 600; 
            padding: 8px 15px;
            border: 2px solid #1976D3;
            border-radius: 10px;
        """)  
        toolbar.addWidget(self.info_label)
        
        toolbar.addStretch()
        
        save_btn = GradientButton("حفظ الدرجات", "fa5s.save")
        save_btn.clicked.connect(self.save_grades)
        toolbar.addWidget(save_btn)
        
        print_btn = GradientButton("طباعة", "fa5s.print")
        print_btn.clicked.connect(self.print_grades)
        print_btn.setObjectName("successButton")
        toolbar.addWidget(print_btn)
        
        card_layout.addLayout(toolbar)
        
        # الجدول
        self.table = ModernTable()
        card_layout.addWidget(self.table)
        
        main_layout.addWidget(table_card)
    
    def _create_widget(self, layout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    # ============================================================
    # ✅ التحميل غير المتزامن - البيانات الأولية
    # ============================================================
    
    def load_initial_data(self):
        """تحميل الصفوف - Local أو Remote."""
        self.loading_overlay.show_loading("جاري تحميل الصفوف...")

        def _fetch_data():
            if GradesFactory.is_remote():
                from app.services.student_factory import StudentFactory
                service = StudentFactory.get_service()
                return service.list_grades()
            with session_scope() as session:
                grades = session.execute(
                    select(Grade).order_by(Grade.id)
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
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            ErrorDialog("خطأ", f"فشل تحميل الصفوف:\n{error_msg}", self).exec()

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
        
    def _on_grade_changed(self):
        """عند تغيير الصف - تحميل الشعب والمواد معاً."""
        grade_id = self.grade_combo.currentData()
        if not grade_id:
            return
        
        self._load_sections_and_subjects(grade_id)
    
    def _load_sections_and_subjects(self, grade_id: int):
        """تحميل الشعب والمواد - Local أو Remote."""
        self.loading_overlay.show_loading("جاري التحميل...")
        academic_year_id = self.academic_year_id

        def _fetch_data():
            if GradesFactory.is_remote():
                service = GradesFactory.get_service()
                return service.get_sections_and_subjects(
                    grade_id=grade_id,
                    academic_year_id=academic_year_id,
                )
            with session_scope() as session:
                sections = session.execute(
                    select(Section)
                    .where(Section.grade_id == grade_id)
                    .order_by(Section.section_name)
                ).scalars().all()

                subject_ids_subq = session.execute(
                    select(TeacherSubjectSection.subject_id)
                    .where(
                        TeacherSubjectSection.grade_id == grade_id,
                        TeacherSubjectSection.academic_year_id
                        == academic_year_id,
                    )
                    .distinct()
                ).scalars().all()

                subjects = session.execute(
                    select(Subject)
                    .where(Subject.id.in_(subject_ids_subq))
                    .order_by(Subject.subject_name)
                ).scalars().all()

                return {
                    'sections': [
                        {'id': s.id, 'name': s.section_name or ''}
                        for s in sections
                    ],
                    'subjects': [
                        {'id': s.id, 'name': s.subject_name or ''}
                        for s in subjects
                    ],
                }

        def _on_result(data):
            try:
                self.section_combo.blockSignals(True)
                self.section_combo.clear()
                for section in data['sections']:
                    self.section_combo.addItem(section['name'], section['id'])
                self.section_combo.blockSignals(False)

                self.subject_combo.blockSignals(True)
                self.subject_combo.clear()
                for subject in data['subjects']:
                    self.subject_combo.addItem(subject['name'], subject['id'])
                self.subject_combo.blockSignals(False)

                self.load_students()
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            print(f"فشل: {error_msg}")

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)

    def _on_filter_changed(self):
        """عند تغيير أي فلتر آخر."""
        self.load_students()
    
    def _on_type_changed(self, index: int):
        """عند تغيير نوع الرصد."""
        is_monthly = index == 0
        self.month_combo.setVisible(is_monthly)
        self.month_label.setVisible(is_monthly)
        self.load_students()
    
    # ============================================================
    # ✅ تحميل الطلاب والدرجات (Async)
    # ============================================================
    
    def load_students(self):
        """تحميل الطلاب والدرجات - Local أو Remote."""
        grade_id = self.grade_combo.currentData()
        section_id = self.section_combo.currentData()
        subject_id = self.subject_combo.currentData()
        term = self.term_combo.currentIndex() + 1
        month = self.month_combo.currentIndex() + 1
        is_monthly = self.type_combo.currentIndex() == 0

        if not all([grade_id, section_id, subject_id]):
            return
        if self._is_loading:
            return

        self._is_loading = True
        self.loading_overlay.show_loading("جاري تحميل الطلاب...")
        academic_year_id = self.academic_year_id

        def _fetch_data():
            if GradesFactory.is_remote():
                service = GradesFactory.get_service()
                return service.get_students_and_scores(
                    academic_year_id=academic_year_id,
                    grade_id=grade_id,
                    section_id=section_id,
                    subject_id=subject_id,
                    term=term,
                    month=month if is_monthly else None,
                    is_monthly=is_monthly,
                )
            # Local (نفس الكود القديم — احتفظ به)
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

                existing_scores = {}
                if is_monthly:
                    evals = session.execute(
                        select(MonthlyEvaluation).where(
                            MonthlyEvaluation.subject_id == subject_id,
                            MonthlyEvaluation.term == term,
                            MonthlyEvaluation.month == month,
                            MonthlyEvaluation.academic_year_id
                            == academic_year_id
                        )
                    ).scalars().all()
                    for ev in evals:
                        existing_scores[ev.student_id] = {
                            'written': float(ev.written_score or 0),
                            'oral': float(ev.oral_score or 0),
                            'homework': float(ev.homework_score or 0),
                            'attendance': float(ev.attendance_score or 0),
                        }
                else:
                    exams = session.execute(
                        select(TermExamScore).where(
                            TermExamScore.subject_id == subject_id,
                            TermExamScore.term == term,
                            TermExamScore.academic_year_id
                            == academic_year_id
                        )
                    ).scalars().all()
                    for exam in exams:
                        existing_scores[exam.student_id] = {
                            'exam': float(exam.exam_score or 0),
                        }

                return {
                    'students': students_data,
                    'existing_scores': existing_scores,
                    'is_monthly': is_monthly,
                }

        def _on_result(data):
            try:
                # ✅ تحويل المفاتيح من str إلى int (JSON)
                raw_map = data.get('existing_scores', {}) or {}
                existing = {}
                for k, v in raw_map.items():
                    try:
                        existing[int(k)] = v
                    except (ValueError, TypeError):
                        pass

                self.existing_scores = existing
                self.current_students = data['students']

                if data['is_monthly']:
                    self._setup_monthly_table(
                        data['students'], subject_id, term, month
                    )
                else:
                    self._setup_term_table(
                        data['students'], subject_id, term
                    )
            finally:
                self._is_loading = False
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self._is_loading = False
            self.loading_overlay.hide_loading()
            print(f"فشل: {error_msg}")

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)

    # ============================================================
    # ✅ إعداد جداول الدرجات
    # ============================================================
    
    def _setup_monthly_table(self, students: List[Dict], 
                              subject_id: int, term: int, month: int):
        """إعداد جدول التقييمات الشهرية."""
        # ✅ منع إشارات valueChanged أثناء الإعداد
        self.table.blockSignals(True)
        
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "رقم الطالب", "اسم الطالب", "تحريري (40)", "شفوي (20)", 
            "واجبات (20)", "مواظبة (20)", "المجموع"
        ])
        
        self.table.setRowCount(len(students))
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 120)        
        self.table.setColumnWidth(5, 120)        
        
        recorded_count = 0
        
        for row, student in enumerate(students):
            self.table.setItem(
                row, 0, QTableWidgetItem(student['student_number'])
            )
            self.table.setItem(
                row, 1, QTableWidgetItem(student['full_name'])
            )
            
            # ✅ استخدام student_id
            scores = self.existing_scores.get(student['id'], {})
            if scores:
                recorded_count += 1
            
            # حقول الإدخال
            for col, (key, max_score) in enumerate([
                ("written", 40), ("oral", 20), 
                ("homework", 20), ("attendance", 20)
            ], start=2):
                input_widget = QDoubleSpinBoxEN()
                input_widget.setRange(0, max_score)
                input_widget.setSingleStep(0.5)
                
                if key in scores:
                    input_widget.setValue(scores[key])
                    # ✅ تمييز الدرجات المسجلة
                    input_widget.setStyleSheet("""
                        QDoubleSpinBox {
                            border: 2px solid #10B981;
                            border-radius: 4px;
                            padding: 5px;
                            background: #ECFDF5;
                            font-weight: 600;
                        }
                        QDoubleSpinBox:focus {
                            border-color: #1976D3;
                            background: white;
                        }
                    """)
                else:
                    input_widget.setStyleSheet("""
                        QDoubleSpinBox {
                            border: 1px solid #E2E8F0;
                            border-radius: 4px;
                            padding: 5px;
                            background: #F8FAFC;
                        }
                        QDoubleSpinBox:focus {
                            border-color: #1976D3;
                            background: white;
                        }
                    """)
                
                input_widget.valueChanged.connect(
                    lambda: self._update_monthly_total_row(row)
                )
                self.table.setCellWidget(row, col, input_widget)
            
            # المجموع
            total_label = QLabel("0.00")
            total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if scores:
                total = sum(scores.values())
                total_label.setText(f"{total:.2f}")
                if total >= 50:
                    total_label.setStyleSheet(
                        "font-weight: 700; color: #10B981;"
                    )
                else:
                    total_label.setStyleSheet(
                        "font-weight: 700; color: #EF4444;"
                    )
            else:
                total_label.setStyleSheet(
                    "font-weight: 700; color: #1976D3;"
                )
            
            self.table.setCellWidget(row, 6, total_label)
            self.table.setRowHeight(row, 45)
        
        self.table.blockSignals(False)
        
        # تحديث المعلومات
        self.info_label.setText(
            f"عدد الطلاب: {len(students)} | الدرجات المسجلة: {recorded_count} | "
            f"التقييم الشهري {month} - الفصل {term}"
        )
    
    def _setup_term_table(self, students: List[Dict], 
                           subject_id: int, term: int):
        """إعداد جدول درجات نهاية الفصل."""
        self.table.blockSignals(True)
        
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "رقم الطالب", "اسم الطالب", "درجة الاختبار (30)", "المجموع"
        ])
        
        self.table.setRowCount(len(students))
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 120)        
        
        recorded_count = 0
        
        for row, student in enumerate(students):
            self.table.setItem(
                row, 0, QTableWidgetItem(student['student_number'])
            )
            self.table.setItem(
                row, 1, QTableWidgetItem(student['full_name'])
            )
            
            scores = self.existing_scores.get(student['id'], {})
            if scores:
                recorded_count += 1
            
            # حقل الإدخال
            input_widget = QDoubleSpinBoxEN()
            input_widget.setRange(0, 30)
            input_widget.setSingleStep(0.5)
            
            if 'exam' in scores:
                input_widget.setValue(scores['exam'])
                input_widget.setStyleSheet("""
                    QDoubleSpinBox {
                        border: 2px solid #10B981;
                        border-radius: 4px;
                        padding: 5px;
                        background: #ECFDF5;
                        font-weight: 600;
                    }
                    QDoubleSpinBox:focus {
                        border-color: #1976D3;
                        background: white;
                    }
                """)
            else:
                input_widget.setStyleSheet("""
                    QDoubleSpinBox {
                        border: 1px solid #E2E8F0;
                        border-radius: 4px;
                        padding: 5px;
                        background: #F8FAFC;
                    }
                    QDoubleSpinBox:focus {
                        border-color: #1976D3;
                        background: white;
                    }
                """)
            
            input_widget.valueChanged.connect(
                lambda: self._update_term_total_row(row)
            )
            self.table.setCellWidget(row, 2, input_widget)
            
            # المجموع
            total_label = QLabel("0.00")
            total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if 'exam' in scores:
                total_label.setText(f"{scores['exam']:.2f}")
                if scores['exam'] >= 15:
                    total_label.setStyleSheet(
                        "font-weight: 700; color: #10B981;"
                    )
                else:
                    total_label.setStyleSheet(
                        "font-weight: 700; color: #EF4444;"
                    )
            else:
                total_label.setStyleSheet(
                    "font-weight: 700; color: #1976D3;"
                )
            
            self.table.setCellWidget(row, 3, total_label)
            self.table.setRowHeight(row, 45)
        
        self.table.blockSignals(False)
        
        # تحديث المعلومات
        self.info_label.setText(
            f"عدد الطلاب: {len(students)} | الدرجات المسجلة: {recorded_count} | "
            f"اختبار الفصل {term}"
        )
    
    # ============================================================
    # ✅ تحديث المجاميع (فقط للصف المحدد - أداء أفضل)
    # ============================================================
    
    def _update_monthly_total_row(self, row: int):
        """تحديث مجموع صف واحد فقط."""
        total = 0
        for col in range(2, 6):
            widget = self.table.cellWidget(row, col)
            if isinstance(widget, QDoubleSpinBox):
                total += widget.value()
        
        total_label = self.table.cellWidget(row, 6)
        if isinstance(total_label, QLabel):
            total_label.setText(f"{total:.2f}")
            if total >= 50:
                total_label.setStyleSheet(
                    "font-weight: 700; color: #10B981;"
                )
            else:
                total_label.setStyleSheet(
                    "font-weight: 700; color: #EF4444;"
                )
    
    def _update_term_total_row(self, row: int):
        """تحديث مجموع صف واحد (اختبار الفصل)."""
        widget = self.table.cellWidget(row, 2)
        if not isinstance(widget, QDoubleSpinBox):
            return
        
        score = widget.value()
        total_label = self.table.cellWidget(row, 3)
        if isinstance(total_label, QLabel):
            total_label.setText(f"{score:.2f}")
            if score >= 15:
                total_label.setStyleSheet(
                    "font-weight: 700; color: #10B981;"
                )
            else:
                total_label.setStyleSheet(
                    "font-weight: 700; color: #EF4444;"
                )
    
    # ============================================================
    # ✅ حفظ الدرجات (Async)
    # ============================================================
    
    def save_grades(self):
        """حفظ الدرجات - Local أو Remote."""
        if self.permission_service and not self.permission_service.can_add("رصد الدرجات"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        if self.table.rowCount() == 0:
            ErrorDialog("تنبيه", "لا يوجد طلاب للحفظ", self).exec()
            return

        grade_id = self.grade_combo.currentData()
        section_id = self.section_combo.currentData()
        subject_id = self.subject_combo.currentData()
        term = self.term_combo.currentIndex() + 1
        month = self.month_combo.currentIndex() + 1
        is_monthly = self.type_combo.currentIndex() == 0

        if not subject_id:
            ErrorDialog("تنبيه", "لا يوجد مواد", self).exec()
            return

        records = []
        for row in range(self.table.rowCount()):
            if row >= len(self.current_students):
                continue
            student_id = self.current_students[row]['id']

            if is_monthly:
                ws = [self.table.cellWidget(row, c) for c in (2, 3, 4, 5)]
                if not all(isinstance(w, QDoubleSpinBox) for w in ws):
                    continue
                records.append({
                    'student_id': student_id,
                    'written': ws[0].value(),
                    'oral': ws[1].value(),
                    'homework': ws[2].value(),
                    'attendance': ws[3].value(),
                })
            else:
                w = self.table.cellWidget(row, 2)
                if not isinstance(w, QDoubleSpinBox):
                    continue
                records.append({
                    'student_id': student_id,
                    'exam': w.value(),
                })

        if not records:
            ErrorDialog("تنبيه", "لا توجد درجات", self).exec()
            return

        self.loading_overlay.show_loading("جاري الحفظ...")
        academic_year_id = self.academic_year_id

        def _save_data():
            if GradesFactory.is_remote():
                service = GradesFactory.get_service()
                payload = {
                    'academic_year_id': academic_year_id,
                    'grade_id': grade_id,
                    'section_id': section_id,
                    'subject_id': subject_id,
                    'term': term,
                    'is_monthly': is_monthly,
                    'records': records,
                }
                if is_monthly:
                    payload['month'] = month
                result = service.save_grades(payload)
                return result.get('saved', len(records))

            # Local
            with session_scope() as session:
                saved = 0
                for rec in records:
                    sid = rec['student_id']
                    if is_monthly:
                        existing = session.execute(
                            select(MonthlyEvaluation).where(
                                MonthlyEvaluation.student_id == sid,
                                MonthlyEvaluation.subject_id == subject_id,
                                MonthlyEvaluation.term == term,
                                MonthlyEvaluation.month == month,
                                MonthlyEvaluation.academic_year_id
                                == academic_year_id
                            )
                        ).scalar_one_or_none()
                        if existing:
                            existing.written_score = Decimal(str(rec['written']))
                            existing.oral_score = Decimal(str(rec['oral']))
                            existing.homework_score = Decimal(str(rec['homework']))
                            existing.attendance_score = Decimal(str(rec['attendance']))
                        else:
                            session.add(MonthlyEvaluation(
                                student_id=sid,
                                academic_year_id=academic_year_id,
                                grade_id=grade_id,
                                section_id=section_id,
                                subject_id=subject_id,
                                term=term,
                                month=month,
                                written_score=Decimal(str(rec['written'])),
                                oral_score=Decimal(str(rec['oral'])),
                                homework_score=Decimal(str(rec['homework'])),
                                attendance_score=Decimal(str(rec['attendance'])),
                            ))
                        saved += 1
                    else:
                        existing = session.execute(
                            select(TermExamScore).where(
                                TermExamScore.student_id == sid,
                                TermExamScore.subject_id == subject_id,
                                TermExamScore.term == term,
                                TermExamScore.academic_year_id
                                == academic_year_id
                            )
                        ).scalar_one_or_none()
                        if existing:
                            existing.exam_score = Decimal(str(rec['exam']))
                        else:
                            session.add(TermExamScore(
                                student_id=sid,
                                academic_year_id=academic_year_id,
                                grade_id=grade_id,
                                section_id=section_id,
                                subject_id=subject_id,
                                term=term,
                                exam_score=Decimal(str(rec['exam'])),
                            ))
                        saved += 1
                session.commit()
                return saved

        def _on_result(saved_count):
            self.loading_overlay.hide_loading()
            SuccessDialog("نجاح", f"تم حفظ {saved_count} درجة", self).exec()
            self.load_students()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            ErrorDialog("خطأ", f"فشل الحفظ:\n{error_msg}", self).exec()

        run_async(_save_data, on_result=_on_result, on_error=_on_error)

    # ============================================================
    # ✅ الطباعة
    # ============================================================
    
    def print_grades(self):
        """طباعة كشف الدرجات."""
        if self.permission_service and not self.permission_service.can_print("رصد الدرجات"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للطباعة في رصد الدرجات"
            )
            return

        if self.table.rowCount() == 0:
            ErrorDialog("تنبيه", "لا يوجد طلاب للطباعة", self).exec()
            return
        
        QMessageBox.information(
            self, 
            "طباعة", 
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
        self.load_initial_data()