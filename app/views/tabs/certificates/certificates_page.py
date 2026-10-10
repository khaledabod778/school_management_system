"""
واجهة الشهادات - شهرية وفصلية ونهائية - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta
from decimal import Decimal

from app.database.models.academic import SchoolInfo
from app.database.session import session_scope
from app.database.models import (
    Student, Grade, Section, Subject, MonthlyEvaluation, 
    TermExamScore, AcademicYear
)
from sqlalchemy import select, func

from app.services.grades_factory import GradesFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    GradientButton, QLineEditPlus, SearchBox
)
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class CertificatesPage(QWidget):
    """صفحة الشهادات - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, cert_type: str = "monthly", 
                 permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.cert_type = cert_type  # monthly, term, final
        self.permission_service = permission_service
        
        # ✅ تخزين البيانات قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        self.academic_year_name = (
            academic_year.year_name_gregorian if academic_year else ''
        )
        
        # ✅ dicts بدلاً من ORM
        self.selected_student_id: Optional[int] = None
        self.selected_student_data: Dict = {}
        self.students_data: List[Dict] = []
        
        # ✅ debounce للبحث
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self.search_students)
        
        # تعريف العناوين
        self.titles = {
            'monthly': 'الشهادة الشهرية',
            'term': 'الشهادة الفصلية',
            'final': 'الشهادة النهائية',
        }           
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل أولي
        QTimer.singleShot(100, self.search_students)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)
        
        # رأس الصفحة
        title = QLabel(self.titles.get(self.cert_type, 'الشهادات'))
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #0F172A;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("اختر طالباً لعرض شهادته وطباعتها")
        subtitle.setStyleSheet("font-size: 13px; color: #64748B;")
        main_layout.addWidget(subtitle)
        
        # فلاتر إضافية حسب نوع الشهادة
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
        
        # البحث        
        self.search_input = SearchBox("بحث عن طالب بالاسم أو الرقم...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        filter_layout.addWidget(self.search_input)
                
        # فلاتر إضافية
        if self.cert_type == 'monthly':
            filter_layout.addWidget(QLabel("الشهر:"))
            self.month_combo = QComboBox()
            self.month_combo.addItems([
                "الشهر الأول", "الشهر الثاني", "الشهر الثالث"
            ])
            self.month_combo.currentIndexChanged.connect(self._on_filter_changed)
            filter_layout.addWidget(self.month_combo)
        
        if self.cert_type in ['monthly', 'term']:
            filter_layout.addWidget(QLabel("الفصل الدراسي:"))
            self.term_combo = QComboBox()
            self.term_combo.addItems(["الفصل الأول", "الفصل الثاني"])
            self.term_combo.currentIndexChanged.connect(self._on_filter_changed)
            filter_layout.addWidget(self.term_combo)
        
        main_layout.addWidget(filter_card)
        
        # منطقة التمرير للشهادة
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(15)
        
        # قائمة الطلاب 
        self.students_list = QListWidget()
        self.students_list.setMaximumHeight(110)
        self.students_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F1F5F9;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background: #F1F5F9;
            }
            QListWidget::item:selected {
                background: #EEF2FF;
                color: #0D47A1;
                font-weight: 600;
            }
        """)
        self.students_list.itemClicked.connect(self.select_student)
        scroll_layout.addWidget(self.students_list)

        # بطاقة الشهادة
        self.certificate_card = QFrame()
        self.certificate_card.setObjectName("certificate_card")
        self.certificate_card.setStyleSheet("""
            QFrame#certificate_card {
                background: white;
                border: 3px solid #1976D3;
                border-radius: 16px;
                padding: 30px;
            }
        """)
        self.certificate_card.setVisible(False)
        
        cert_layout = QVBoxLayout(self.certificate_card)
        cert_layout.setSpacing(15)
        
        # شعار المدرسة
        logo_label = QLabel()
        logo_label.setPixmap(
            qta.icon('fa5s.school', color='#1976D3').pixmap(50, 50)
        )
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cert_layout.addWidget(logo_label)
        
        # اسم المدرسة
        self.school_name = QLabel()
        self.school_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.school_name.setStyleSheet(
            "font-size: 22px; font-weight: 800; color: #1976D3;"
        )
        cert_layout.addWidget(self.school_name)
        
        # عنوان الشهادة
        cert_title = QLabel(self.titles.get(self.cert_type, ''))
        cert_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cert_title.setStyleSheet("""
            font-size: 18px; 
            font-weight: 700; 
            color: #0F172A;
            padding: 10px;
            background: #EEF2FF;
            border-radius: 8px;
        """)
        cert_layout.addWidget(cert_title)
        
        # معلومات الطالب
        self.student_info_label = QLabel()
        self.student_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.student_info_label.setStyleSheet("""
            font-size: 14px; 
            color: #475569;
            line-height: 1.8;
        """)
        cert_layout.addWidget(self.student_info_label)
        
        # خط فاصل
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #E2E8F0;")
        cert_layout.addWidget(line)
        
        # جدول الدرجات
        self.grades_table = QTableWidget()
        self.grades_table.horizontalHeader().setStretchLastSection(True)
        self.grades_table.setAlternatingRowColors(True)
        self.grades_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.grades_table.verticalHeader().setVisible(False)
        self.grades_table.setMinimumHeight(200)
        cert_layout.addWidget(self.grades_table)
        
        # المجموع الكلي
        self.total_label = QLabel()
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_label.setStyleSheet("""
            font-size: 16px; 
            font-weight: 700; 
            color: #10B981;
            padding: 10px;
            background: #ECFDF5;
            border-radius: 8px;
        """)
        cert_layout.addWidget(self.total_label)
        
        # النسبة والتقدير العام
        self.percentage_label = QLabel()
        self.percentage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.percentage_label.setStyleSheet(
            "font-size: 13px; color: #475569;"
        )
        cert_layout.addWidget(self.percentage_label)
        
        # زر الطباعة
        self.print_btn = GradientButton("طباعة الشهادة", "fa5s.print")
        self.print_btn.clicked.connect(self.print_certificate)
        self.print_btn.setEnabled(False)  # ✅ معطّل حتى اختيار طالب
        cert_layout.addWidget(self.print_btn)

        scroll_layout.addStretch()
        scroll_layout.addWidget(self.certificate_card)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
    
    # ============================================================
    # ✅ البحث عن الطلاب (Async)
    # ============================================================
    
    def _on_search_text_changed(self):
        """عند تغيير نص البحث - debounce."""
        self._search_timer.stop()
        self._search_timer.start()
    
    def _on_filter_changed(self):
        """عند تغيير الفلاتر (الفصل/الشهر) - إعادة تحميل الشهادة."""
        if self.selected_student_id:
            self._load_student_certificate(self.selected_student_id)
    
    def search_students(self):
        """البحث عن الطلاب - Local أو Remote."""
        search_text = (
            self.search_input.text().strip()
            if hasattr(self, 'search_input') else ""
        )
        self.loading_overlay.show_loading("جاري البحث...")
        academic_year_id = self.academic_year_id

        def _fetch_data():
            if GradesFactory.is_remote():
                from app.services.student_factory import StudentFactory
                service = StudentFactory.get_service()
                return service.list_students(
                    academic_year_id=academic_year_id,
                    search=search_text or None,
                    status='مستمر',
                )[:30]
            with session_scope() as session:
                query = select(Student).where(
                    Student.academic_year_id == academic_year_id,
                    Student.status == 'مستمر'
                )
                if search_text:
                    query = query.where(
                        (Student.full_name.ilike(f"%{search_text}%")) |
                        (Student.student_number.ilike(f"%{search_text}%"))
                    )
                students = session.execute(
                    query.order_by(Student.full_name).limit(30)
                ).scalars().all()
                return [
                    {
                        'id': s.id,
                        'full_name': s.full_name or '',
                        'student_number': s.student_number or '',
                    }
                    for s in students
                ]

        def _on_result(data):
            try:
                self.students_data = data
                self.students_list.clear()
                for student in data:
                    item = QListWidgetItem(
                        f"{student['full_name']} - {student['student_number']}"
                    )
                    item.setData(Qt.ItemDataRole.UserRole, student['id'])
                    self.students_list.addItem(item)
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            print(f"فشل: {error_msg}")

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)

    # ============================================================
    # ✅ اختيار طالب - تحميل الشهادة (Async)
    # ============================================================
    
    def select_student(self, item: QListWidgetItem):
        """اختيار طالب - تحميل شهادته."""
        student_id = item.data(Qt.ItemDataRole.UserRole)
        
        # ✅ البحث في القائمة المحفوظة
        student = next(
            (s for s in self.students_data if s['id'] == student_id),
            None
        )
        if not student:
            return
        
        self.selected_student_id = student_id
        self.selected_student_data = student
        
        # ✅ تفعيل زر الطباعة
        self.print_btn.setEnabled(True)
        
        # ✅ تحميل الشهادة الكاملة
        self._load_student_certificate(student_id)
    
    def _load_student_certificate(self, student_id: int):
        """تحميل الشهادة - Local أو Remote."""
        self.loading_overlay.show_loading("جاري تحميل الشهادة...")

        term = (
            self.term_combo.currentIndex() + 1
            if hasattr(self, 'term_combo') else 1
        )
        month = (
            self.month_combo.currentIndex() + 1
            if hasattr(self, 'month_combo') else 1
        )
        cert_type = self.cert_type
        academic_year_id = self.academic_year_id
        academic_year_name = self.academic_year_name

        def _fetch_data():
            if GradesFactory.is_remote():
                service = GradesFactory.get_service()
                return service.get_certificate(
                    student_id=student_id,
                    academic_year_id=academic_year_id,
                    cert_type=cert_type,
                    term=term,
                    month=month,
                )
            # Local (الكود القديم — احتفظ به)
            with session_scope() as session:
                student = session.execute(
                    select(Student).where(Student.id == student_id)
                ).scalar_one_or_none()
                if not student:
                    return None

                grade_name = ''
                section_name = ''
                try:
                    if student.grade:
                        grade_name = student.grade.grade_name
                    if student.section:
                        section_name = student.section.section_name
                except Exception:
                    pass

                school_info = session.execute(
                    select(SchoolInfo).limit(1)
                ).scalar_one_or_none()
                school_name = school_info.school_name_ar if school_info else ''

                # ... (استخدم نفس دوال _fetch_monthly_grades إلخ)
                if cert_type == 'monthly':
                    grades_data = self._fetch_monthly_grades(
                        session, student_id, term, month, academic_year_id
                    )
                elif cert_type == 'term':
                    grades_data = self._fetch_term_grades(
                        session, student_id, term, academic_year_id
                    )
                else:
                    grades_data = self._fetch_final_grades(
                        session, student_id, academic_year_id
                    )

                return {
                    'student': {
                        'id': student.id,
                        'full_name': student.full_name or '',
                        'student_number': student.student_number or '',
                        'grade_name': grade_name,
                        'section_name': section_name,
                    },
                    'school_name': school_name,
                    'grades': grades_data,
                    'term': term,
                    'month': month,
                    'academic_year_name': academic_year_name,
                }

        def _on_result(data):
            try:
                if not data:
                    QMessageBox.critical(self, "خطأ", "الطالب غير موجود")
                    return
                self._display_certificate(data)
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(self, "خطأ", f"فشل: {error_msg}")

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
        
    # ============================================================
    # ✅ دوال جلب الدرجات (تُنفذ داخل الجلسة)
    # ============================================================
    
    def _fetch_monthly_grades(self, session, student_id: int, 
                                term: int, month: int, 
                                academic_year_id: int) -> Dict:
        """جلب درجات الشهادة الشهرية."""
        evaluations = session.execute(
            select(MonthlyEvaluation, Subject)
            .select_from(MonthlyEvaluation)
            .join(Subject, MonthlyEvaluation.subject_id == Subject.id)
            .where(
                MonthlyEvaluation.student_id == student_id,
                MonthlyEvaluation.term == term,
                MonthlyEvaluation.month == month,
                MonthlyEvaluation.academic_year_id == academic_year_id
            )
            .order_by(Subject.subject_name)
        ).all()
        
        subjects_data = []
        for ev, subject in evaluations:
            written = float(ev.written_score or 0)
            oral = float(ev.oral_score or 0)
            homework = float(ev.homework_score or 0)
            attendance = float(ev.attendance_score or 0)
            total = written + oral + homework + attendance
            
            subjects_data.append({
                'subject_name': subject.subject_name or '',
                'written': written,
                'oral': oral,
                'homework': homework,
                'attendance': attendance,
                'total': total,
            })
        
        return {
            'type': 'monthly',
            'subjects': subjects_data,
        }
    
    def _fetch_term_grades(self, session, student_id: int, 
                            term: int, academic_year_id: int) -> Dict:
        """جلب درجات الشهادة الفصلية."""
        # ✅ متوسط التقييمات الشهرية
        monthly_avg = session.execute(
            select(
                func.avg(
                    MonthlyEvaluation.written_score +
                    MonthlyEvaluation.oral_score +
                    MonthlyEvaluation.homework_score +
                    MonthlyEvaluation.attendance_score
                ).label('avg_score'),
                Subject.id.label('subject_id'),
                Subject.subject_name
            )
            .select_from(MonthlyEvaluation)
            .join(Subject, MonthlyEvaluation.subject_id == Subject.id)
            .where(
                MonthlyEvaluation.student_id == student_id,
                MonthlyEvaluation.term == term,
                MonthlyEvaluation.academic_year_id == academic_year_id
            )
            .group_by(Subject.id, Subject.subject_name)
        ).all()
        
        # ✅ درجات الاختبار
        exam_scores = session.execute(
            select(TermExamScore, Subject)
            .select_from(TermExamScore)
            .join(Subject, TermExamScore.subject_id == Subject.id)
            .where(
                TermExamScore.student_id == student_id,
                TermExamScore.term == term,
                TermExamScore.academic_year_id == academic_year_id
            )
        ).all()
        
        # دمج البيانات
        grades_map = {}
        for avg_score, subject_id, subject_name in monthly_avg:
            grades_map[subject_id] = {
                'subject_name': subject_name or '',
                'works': float(avg_score or 0),
                'exam': 0.0,
            }
        
        for exam, subject in exam_scores:
            if subject.id in grades_map:
                grades_map[subject.id]['exam'] = float(exam.exam_score or 0)
            else:
                grades_map[subject.id] = {
                    'subject_name': subject.subject_name or '',
                    'works': 0.0,
                    'exam': float(exam.exam_score or 0),
                }
        
        # ✅ تحويل إلى قائمة مع الحسابات
        subjects_data = []
        for subject_id, data in sorted(
            grades_map.items(), key=lambda x: x[1]['subject_name']
        ):
            works = data['works'] / 5
            exam = data['exam']
            total = works + exam
            
            subjects_data.append({
                'subject_name': data['subject_name'],
                'works': works,
                'exam': exam,
                'total': total,
            })
        
        return {
            'type': 'term',
            'subjects': subjects_data,
        }
    
    def _fetch_final_grades(self, session, student_id: int, 
                              academic_year_id: int) -> Dict:
        """جلب درجات الشهادة النهائية (الفصلين)."""
        # ✅ الفصل الأول
        term1_monthly = session.execute(
            select(
                func.avg(
                    MonthlyEvaluation.written_score +
                    MonthlyEvaluation.oral_score +
                    MonthlyEvaluation.homework_score +
                    MonthlyEvaluation.attendance_score
                ).label('avg_score'),
                Subject.id.label('subject_id'),
                Subject.subject_name
            )
            .select_from(MonthlyEvaluation)
            .join(Subject, MonthlyEvaluation.subject_id == Subject.id)
            .where(
                MonthlyEvaluation.student_id == student_id,
                MonthlyEvaluation.term == 1,
                MonthlyEvaluation.academic_year_id == academic_year_id
            )
            .group_by(Subject.id, Subject.subject_name)
        ).all()
        
        term1_exams = session.execute(
            select(TermExamScore, Subject)
            .select_from(TermExamScore)
            .join(Subject, TermExamScore.subject_id == Subject.id)
            .where(
                TermExamScore.student_id == student_id,
                TermExamScore.term == 1,
                TermExamScore.academic_year_id == academic_year_id
            )
        ).all()
        
        # ✅ الفصل الثاني
        term2_monthly = session.execute(
            select(
                func.avg(
                    MonthlyEvaluation.written_score +
                    MonthlyEvaluation.oral_score +
                    MonthlyEvaluation.homework_score +
                    MonthlyEvaluation.attendance_score
                ).label('avg_score'),
                Subject.id.label('subject_id'),
                Subject.subject_name
            )
            .select_from(MonthlyEvaluation)
            .join(Subject, MonthlyEvaluation.subject_id == Subject.id)
            .where(
                MonthlyEvaluation.student_id == student_id,
                MonthlyEvaluation.term == 2,
                MonthlyEvaluation.academic_year_id == academic_year_id
            )
            .group_by(Subject.id, Subject.subject_name)
        ).all()
        
        term2_exams = session.execute(
            select(TermExamScore, Subject)
            .select_from(TermExamScore)
            .join(Subject, TermExamScore.subject_id == Subject.id)
            .where(
                TermExamScore.student_id == student_id,
                TermExamScore.term == 2,
                TermExamScore.academic_year_id == academic_year_id
            )
        ).all()
        
        # دمج البيانات
        grades_map = {}
        
        for avg_score, subject_id, subject_name in term1_monthly:
            grades_map[subject_id] = {
                'subject_name': subject_name or '',
                'term1_works': float(avg_score or 0),
                'term1_exam': 0.0,
                'term2_works': 0.0,
                'term2_exam': 0.0,
            }
        
        for exam, subject in term1_exams:
            if subject.id in grades_map:
                grades_map[subject.id]['term1_exam'] = float(exam.exam_score or 0)
            else:
                grades_map[subject.id] = {
                    'subject_name': subject.subject_name or '',
                    'term1_works': 0.0,
                    'term1_exam': float(exam.exam_score or 0),
                    'term2_works': 0.0,
                    'term2_exam': 0.0,
                }
        
        for avg_score, subject_id, subject_name in term2_monthly:
            if subject_id in grades_map:
                grades_map[subject_id]['term2_works'] = float(avg_score or 0)
            else:
                grades_map[subject_id] = {
                    'subject_name': subject_name or '',
                    'term1_works': 0.0,
                    'term1_exam': 0.0,
                    'term2_works': float(avg_score or 0),
                    'term2_exam': 0.0,
                }
        
        for exam, subject in term2_exams:
            if subject.id in grades_map:
                grades_map[subject.id]['term2_exam'] = float(exam.exam_score or 0)
            else:
                grades_map[subject.id] = {
                    'subject_name': subject.subject_name or '',
                    'term1_works': 0.0,
                    'term1_exam': 0.0,
                    'term2_works': 0.0,
                    'term2_exam': float(exam.exam_score or 0),
                }
        
        # ✅ تحويل إلى قائمة مع الحسابات
        subjects_data = []
        for subject_id, data in sorted(
            grades_map.items(), key=lambda x: x[1]['subject_name']
        ):
            t1_works = data['term1_works'] / 5
            t1_exam = data['term1_exam']
            t1_total = t1_works + t1_exam
            
            t2_works = data['term2_works'] / 5
            t2_exam = data['term2_exam']
            t2_total = t2_works + t2_exam
            
            total = t1_total + t2_total
            
            subjects_data.append({
                'subject_name': data['subject_name'],
                'term1_works': t1_works,
                'term1_exam': t1_exam,
                'term1_total': t1_total,
                'term2_works': t2_works,
                'term2_exam': t2_exam,
                'term2_total': t2_total,
                'total': total,
            })
        
        return {
            'type': 'final',
            'subjects': subjects_data,
        }
    
    # ============================================================
    # ✅ عرض الشهادة
    # ============================================================
    
    def _display_certificate(self, data: Dict):
        """عرض الشهادة الكاملة."""
        self.certificate_card.setVisible(True)
        
        # ============ معلومات المدرسة ============
        self.school_name.setText(data['school_name'])
        
        # ============ معلومات الطالب ============
        student = data['student']
        term = data['term']
        
        info_lines = [
            f"الطالب: {student['full_name']}",
            f"الصف: {student['grade_name']} - شعبة: {student['section_name']}",
            f"السنة الدراسية: {data['academic_year_name']}",
        ]
        
        if self.cert_type == 'monthly':
            info_lines.append(
                f"الفصل الدراسي: {'الأول' if term == 1 else 'الثاني'}"
            )
            info_lines.append(
                f"الشهر: {'الأول' if data['month'] == 1 else 'الثاني' if data['month'] == 2 else 'الثالث'}"
            )
        elif self.cert_type == 'term':
            info_lines.append(
                f"الفصل الدراسي: {'الأول' if term == 1 else 'الثاني'}"
            )
        
        self.student_info_label.setText("\n".join(info_lines))
        
        # ============ عرض الجدول ============
        grades = data['grades']
        
        if grades['type'] == 'monthly':
            self._display_monthly_table(grades['subjects'])
        elif grades['type'] == 'term':
            self._display_term_table(grades['subjects'])
        else:
            self._display_final_table(grades['subjects'])
    
    def _display_monthly_table(self, subjects: List[Dict]):
        """عرض جدول الشهادة الشهرية."""
        self.grades_table.setColumnCount(8)
        self.grades_table.setHorizontalHeaderLabels([
            "المادة", "تحريري (40)", "شفوي (20)", 
            "واجبات (20)", "مواظبة (20)",
            "المجموع", "التقدير", "الملاحظات"
        ])
        self.grades_table.setColumnWidth(0, 180)
        self.grades_table.setColumnWidth(1, 90)
        self.grades_table.setColumnWidth(2, 90)
        self.grades_table.setColumnWidth(3, 90)
        self.grades_table.setColumnWidth(4, 90)
        self.grades_table.setColumnWidth(5, 100)
        self.grades_table.setColumnWidth(6, 100)
        
        self.grades_table.setRowCount(len(subjects))
        
        total_sum = 0.0
        for row, subject in enumerate(subjects):
            self.grades_table.setItem(
                row, 0, QTableWidgetItem(subject['subject_name'])
            )
            self.grades_table.setItem(
                row, 1, QTableWidgetItem(f"{subject['written']:.2f}")
            )
            self.grades_table.setItem(
                row, 2, QTableWidgetItem(f"{subject['oral']:.2f}")
            )
            self.grades_table.setItem(
                row, 3, QTableWidgetItem(f"{subject['homework']:.2f}")
            )
            self.grades_table.setItem(
                row, 4, QTableWidgetItem(f"{subject['attendance']:.2f}")
            )
            
            total_item = QTableWidgetItem(f"{subject['total']:.2f}")
            total_item.setFont(QFont("Cairo", 10, QFont.Weight.Bold))
            self.grades_table.setItem(row, 5, total_item)
            
            grade_text = self._get_grade_text(subject['total'])
            grade_item = QTableWidgetItem(grade_text)
            grade_item.setForeground(self._get_grade_color(grade_text))
            self.grades_table.setItem(row, 6, grade_item)
            
            self.grades_table.setRowHeight(row, 40)
            total_sum += subject['total']
        
        self._update_total_summary(total_sum, len(subjects))
    
    def _display_term_table(self, subjects: List[Dict]):
        """عرض جدول الشهادة الفصلية."""
        self.grades_table.setColumnCount(6)
        self.grades_table.setHorizontalHeaderLabels([
            "المادة", "المحصلة", "الاختبار", 
            "المجموع", "التقدير", "الملاحظات"
        ])
        self.grades_table.setColumnWidth(0, 200)
        self.grades_table.setColumnWidth(1, 80)
        self.grades_table.setColumnWidth(2, 80)
        self.grades_table.setColumnWidth(3, 80)
        self.grades_table.setColumnWidth(4, 100)
        
        self.grades_table.setRowCount(len(subjects))
        
        total_sum = 0.0
        for row, subject in enumerate(subjects):
            self.grades_table.setItem(
                row, 0, QTableWidgetItem(subject['subject_name'])
            )
            self.grades_table.setItem(
                row, 1, QTableWidgetItem(f"{subject['works']:.2f}")
            )
            self.grades_table.setItem(
                row, 2, QTableWidgetItem(f"{subject['exam']:.2f}")
            )
            
            total_item = QTableWidgetItem(f"{subject['total']:.2f}")
            total_item.setFont(QFont("Cairo", 10, QFont.Weight.Bold))
            self.grades_table.setItem(row, 3, total_item)
            
            grade_text = self._get_grade_text2(subject['total'])
            grade_item = QTableWidgetItem(grade_text)
            grade_item.setForeground(self._get_grade_color(grade_text))
            self.grades_table.setItem(row, 4, grade_item)
            
            self.grades_table.setRowHeight(row, 40)
            total_sum += subject['total']
        
        self._update_total_summary50(total_sum, len(subjects))
    
    def _display_final_table(self, subjects: List[Dict]):
        """عرض جدول الشهادة النهائية."""
        self.grades_table.setColumnCount(9)
        self.grades_table.setHorizontalHeaderLabels([
            "المادة", "م1", "اختبار1", "مجموع1",
            "م2", "اختبار2", "مجموع2", "المجموع النهائي", "التقدير"
        ])
        self.grades_table.setColumnWidth(0, 180)
        self.grades_table.setColumnWidth(1, 80)
        self.grades_table.setColumnWidth(2, 80)
        self.grades_table.setColumnWidth(3, 80)
        self.grades_table.setColumnWidth(4, 80)
        self.grades_table.setColumnWidth(5, 80)
        self.grades_table.setColumnWidth(6, 80)
        self.grades_table.setColumnWidth(7, 100)
        
        self.grades_table.setRowCount(len(subjects))
        
        total_sum = 0.0
        for row, subject in enumerate(subjects):
            self.grades_table.setItem(
                row, 0, QTableWidgetItem(subject['subject_name'])
            )
            self.grades_table.setItem(
                row, 1, QTableWidgetItem(f"{subject['term1_works']:.2f}")
            )
            self.grades_table.setItem(
                row, 2, QTableWidgetItem(f"{subject['term1_exam']:.2f}")
            )
            self.grades_table.setItem(
                row, 3, QTableWidgetItem(f"{subject['term1_total']:.2f}")
            )
            self.grades_table.setItem(
                row, 4, QTableWidgetItem(f"{subject['term2_works']:.2f}")
            )
            self.grades_table.setItem(
                row, 5, QTableWidgetItem(f"{subject['term2_exam']:.2f}")
            )
            self.grades_table.setItem(
                row, 6, QTableWidgetItem(f"{subject['term2_total']:.2f}")
            )
            
            total_item = QTableWidgetItem(f"{subject['total']:.2f}")
            total_item.setFont(QFont("Cairo", 10, QFont.Weight.Bold))
            total_item.setForeground(QColor('#1976D3'))
            self.grades_table.setItem(row, 7, total_item)
            
            grade_text = self._get_grade_text(subject['total'])
            grade_item = QTableWidgetItem(grade_text)
            grade_item.setForeground(self._get_grade_color(grade_text))
            self.grades_table.setItem(row, 8, grade_item)
            
            self.grades_table.setRowHeight(row, 40)
            total_sum += subject['total']
        
        self._update_total_summary_final(total_sum, len(subjects))
    
    # ============================================================
    # ✅ دوال مساعدة للتقديرات والمجاميع
    # ============================================================
    
    def _get_grade_text(self, score: float) -> str:
        """الحصول على التقدير (للشهادة الشهرية والنهائية)."""
        if score >= 90:
            return "ممتاز"
        elif score >= 80:
            return "جيد جداً"
        elif score >= 70:
            return "جيد"
        elif score >= 60:
            return "مقبول"
        elif score >= 50:
            return "ضعيف"
        else:
            return "راسب"
        
    def _get_grade_text2(self, score: float) -> str:
        """الحصول على التقدير (للشهادة الفصلية)."""
        if score >= 45:
            return "ممتاز"
        elif score >= 40:
            return "جيد جداً"
        elif score >= 35:
            return "جيد"
        elif score >= 30:
            return "مقبول"
        elif score >= 25:
            return "ضعيف"
        else:
            return "راسب"
    
    def _get_grade_color(self, grade_text: str) -> QColor:
        """الحصول على لون التقدير."""
        colors = {
            'ممتاز': '#10B981',
            'جيد جداً': '#1976D3',
            'جيد': '#06B6D4',
            'مقبول': '#F59E0B',
            'ضعيف': '#EF4444',
            'راسب': '#DC2626',
        }
        return QColor(colors.get(grade_text, '#64748B'))
    
    def _update_total_summary(self, total_sum: float, subjects_count: int):
        """تحديث ملخص المجموع (شهري + نهائي)."""
        self.total_label.setText(f"المجموع الكلي: {total_sum:.2f}")
        
        if subjects_count > 0:
            percentage = (total_sum / (subjects_count * 100)) * 100
            grade_text = self._get_grade_text(percentage)
            self.percentage_label.setText(
                f"النسبة المئوية: {percentage:.2f}% | "
                f"التقدير العام: {grade_text}"
            )
        else:
            self.percentage_label.setText("لا توجد درجات مسجلة لهذه الفترة")

    def _update_total_summary50(self, total_sum: float, subjects_count: int):
        """تحديث ملخص المجموع (فصلي)."""
        self.total_label.setText(f"المجموع الكلي: {total_sum:.2f}")
        
        if subjects_count > 0:
            percentage = (total_sum / (subjects_count * 50)) * 100
            grade_text = self._get_grade_text(percentage)
            self.percentage_label.setText(
                f"النسبة المئوية: {percentage:.2f}% | "
                f"التقدير العام: {grade_text}"
            )
        else:
            self.percentage_label.setText("لا توجد درجات مسجلة لهذه الفترة")
    
    def _update_total_summary_final(self, total_sum: float, 
                                      subjects_count: int):
        """تحديث ملخص المجموع النهائي."""
        self.total_label.setText(f"المجموع الكلي النهائي: {total_sum:.2f}")
        
        if subjects_count > 0:
            percentage = (total_sum / (subjects_count * 100)) * 100
            grade_text = self._get_grade_text(percentage)
            result = "ناجح" if percentage >= 50 else "راسب / دور ثاني"
            
            self.percentage_label.setText(
                f"النسبة المئوية: {percentage:.2f}%  |  "
                f"التقدير: {grade_text}  |  النتيجة: {result}"
            )
        else:
            self.percentage_label.setText("لا توجد درجات مسجلة")
    
    # ============================================================
    # ✅ الطباعة
    # ============================================================
    
    def print_certificate(self):
        """طباعة الشهادة PDF - Local أو Remote."""
        if self.permission_service and not self.permission_service.can_print("الشهادات والأوائل"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للطباعة في الشهادات والأوائل"
            )
            return

        if not self.selected_student_id:
            QMessageBox.warning(self, "تنبيه", "اختر طالباً")
            return

        # ✅ سؤال: فتح أم حفظ؟
        choice = QMessageBox.question(
            self, "طباعة الشهادة",
            "اختر طريقة الحفظ:",
            QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Save,
            QMessageBox.StandardButton.Open,
        )

        if choice == QMessageBox.StandardButton.Save:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "حفظ الشهادة",
                f"certificate_{self.selected_student_id}.pdf",
                "PDF Files (*.pdf)"
            )
            if not file_path:
                return
        else:
            # فتح: احفظ مؤقتاً ثم افتح
            import tempfile
            tmp_dir = tempfile.gettempdir()
            file_path = f"{tmp_dir}/certificate_{self.selected_student_id}.pdf"

        # ✅ قراءة الفلاتر
        term = (
            self.term_combo.currentIndex() + 1
            if hasattr(self, 'term_combo') else 1
        )
        month = (
            self.month_combo.currentIndex() + 1
            if hasattr(self, 'month_combo') else 1
        )

        self.loading_overlay.show_loading("جاري توليد الشهادة...")

        def _download():
            if GradesFactory.is_remote():
                from app.services.auth_factory import AuthFactory
                client = AuthFactory.get_api_client()
                url = f"/api/print/certificate/{self.selected_student_id}"
                params = {
                    'academic_year_id': self.academic_year_id,
                    'cert_type': self.cert_type,
                    'term': term,
                    'month': month,
                }
                # ✅ download_file موجود في ApiClient
                client.download_file_with_params(
                    url, file_path, params=params,
                )
            else:
                # Local: يولّد PDF محلياً (اختياري — يمكن إضافته لاحقاً)
                raise Exception(
                    "الطباعة المحلية غير مدعومة حالياً. "
                    "استخدم api_mode=remote"
                )
            return file_path

        def _ok(path):
            self.loading_overlay.hide_loading()
            try:
                import os, sys, subprocess
                if sys.platform == "win32":
                    os.startfile(path)
                elif sys.platform == "darwin":
                    subprocess.call(["open", path])
                else:
                    subprocess.call(["xdg-open", path])
                QMessageBox.information(
                    self, "نجاح", f"تم فتح الشهادة:\n{path}"
                )
            except Exception as e:
                QMessageBox.information(
                    self, "نجاح", f"تم الحفظ في:\n{path}"
                )

        def _err(m):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(self, "خطأ", f"فشل الطباعة: {m}")

        run_async(_download, on_result=_ok, on_error=_err)
    
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
        # إخفاء الشهادة
        self.certificate_card.setVisible(False)
        
        # إعادة تعيين الحالة
        self.selected_student_id = None
        self.selected_student_data = {}
        self.print_btn.setEnabled(False)
        
        # إعادة تحميل الطلاب
        self.search_students()