"""
واجهة كشوفات الترتيب التنافسي (الأوائل) - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict, Tuple
import qtawesome as qta
from decimal import Decimal

from app.database.session import session_scope
from app.database.models import (
    Student, Grade, Section, MonthlyEvaluation, 
    TermExamScore, Subject, AcademicYear
)
from app.services.grades_factory import GradesFactory
from app.services.permission_service import PermissionService
from sqlalchemy import select, func

from app.views.widgets.custom_widgets import GradientButton
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class TopStudentsPage(QWidget):
    """صفحة كشوفات الأوائل - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, 
                 permission_service: Optional[PermissionService] = None, 
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        # ✅ تعريف permission_service (كان ناقصاً!)
        self.permission_service = permission_service
        
        # ✅ تخزين بيانات السنة قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        
        # ✅ منع التوليد المزدوج
        self._is_generating = False
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل أولي للصفوف
        QTimer.singleShot(100, self.load_data)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)
        
        # رأس الصفحة
        title = QLabel("كشوفات الترتيب التنافسي (الأوائل)")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #0F172A;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("عرض ترتيب الطلاب الأوائل حسب النوع المحدد")
        subtitle.setStyleSheet("font-size: 13px; color: #64748B;")
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
        filter_layout.setSpacing(10)
        
        filter_layout.addWidget(QLabel("نوع الكشف:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["شهري", "فصلي", "سنوي"])
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        filter_layout.addWidget(self.type_combo)
        
        filter_layout.addWidget(QLabel("الصف:"))
        self.grade_combo = QComboBox()
        self.grade_combo.addItem("جميع الصفوف", None)
        filter_layout.addWidget(self.grade_combo)
        
        # فلاتر إضافية حسب النوع
        self.term_label = QLabel("الفصل:")
        self.term_combo = QComboBox()
        self.term_combo.addItems(["الأول", "الثاني"])
        filter_layout.addWidget(self.term_label)
        filter_layout.addWidget(self.term_combo)
        
        self.month_label = QLabel("الشهر:")
        self.month_combo = QComboBox()
        self.month_combo.addItems(["الأول", "الثاني", "الثالث"])
        filter_layout.addWidget(self.month_label)
        filter_layout.addWidget(self.month_combo)
        
        filter_layout.addStretch()
        
        self.generate_btn = GradientButton("عرض الكشف", "fa5s.trophy")
        self.generate_btn.setObjectName("warningButton")
        self.generate_btn.clicked.connect(self.generate_report)
        filter_layout.addWidget(self.generate_btn)
        
        main_layout.addWidget(filter_card)
        
        # منطقة النتائج مع التمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )
        
        scroll_widget = QWidget()
        self.results_layout = QVBoxLayout(scroll_widget)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(15)
        
        # ✅ Placeholder أولي
        self._show_placeholder()
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # ضبط الإظهار حسب النوع
        self._on_type_changed()
    
    def _show_placeholder(self, message: str = "اختر الفلاتر واضغط عرض الكشف"):
        """عرض رسالة مؤقتة."""
        self._clear_results()
        
        placeholder = QLabel(message)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("""
            font-size: 14px; 
            color: #94A3B8; 
            padding: 50px;
            background: white;
            border: 2px dashed #E2E8F0;
            border-radius: 12px;
        """)
        self.results_layout.addWidget(placeholder)
    
    def _on_type_changed(self):
        """عند تغيير نوع الكشف."""
        report_type = self.type_combo.currentText()
        
        # إظهار/إخفاء فلتر الشهر
        is_monthly = report_type == "شهري"
        self.month_label.setVisible(is_monthly)
        self.month_combo.setVisible(is_monthly)
        
        # الفصل يظهر للشهري والفصلي
        is_term = report_type in ["شهري", "فصلي"]
        self.term_label.setVisible(is_term)
        self.term_combo.setVisible(is_term)
    
    # ============================================================
    # ✅ التحميل غير المتزامن - البيانات الأولية
    # ============================================================
    
    def load_data(self):
        """تحميل الصفوف - Local أو Remote."""
        self.loading_overlay.show_loading("جاري التحميل...")

        def _fetch_data():
            if GradesFactory.is_remote():
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
                self.grade_combo.addItem("جميع الصفوف", None)
                for grade in data:
                    self.grade_combo.addItem(
                        grade.get('name', grade.get('grade_name', '')),
                        grade['id']
                    )
                self.grade_combo.blockSignals(False)
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            print(f"فشل: {error_msg}")

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
        
    def _clear_results(self):
        """مسح النتائج السابقة."""
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    # ============================================================
    # ✅ توليد الكشف (Async)
    # ============================================================
    
    def generate_report(self):
        """توليد الكشف في الخلفية."""
        # ✅ منع التوليد المزدوج
        if self._is_generating:
            return
        
        self._is_generating = True
        
        report_type = self.type_combo.currentText()
        grade_id = self.grade_combo.currentData()
        term = self.term_combo.currentIndex() + 1
        month = self.month_combo.currentIndex() + 1
        
        # ✅ تأكيد التوليد للسنوي (ثقيل)
        if report_type == "سنوي":
            reply = QMessageBox.question(
                self, "تأكيد",
                "توليد الكشف السنوي قد يستغرق وقتاً. هل تريد المتابعة؟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                self._is_generating = False
                return
        
        self.loading_overlay.show_loading(
            f"جاري حساب كشف {report_type}..."
        )
        
        academic_year_id = self.academic_year_id
        
        def _fetch_data():
            if GradesFactory.is_remote():
                service = GradesFactory.get_service()
                return service.get_top_students(
                    academic_year_id=academic_year_id,
                    report_type=report_type,
                    grade_id=grade_id,
                    term=term,
                    month=month,
                )
            
            # Local (الكود القديم — احتفظ به)
            with session_scope() as session:
                # ============ 1. الصفوف المطلوبة ============
                if grade_id:
                    grades_query = session.execute(
                        select(Grade).where(Grade.id == grade_id)
                    ).scalars().all()
                else:
                    grades_query = session.execute(
                        select(Grade).order_by(Grade.grade_name)
                    ).scalars().all()
                
                # ✅ تحويل إلى dicts
                grades_data = [
                    {
                        'id': g.id,
                        'grade_name': g.grade_name or '',
                        'stage_name': g.stage_name or '',
                    }
                    for g in grades_query
                ]
                
                # ============ 2. حساب درجات الطلاب ============
                results = []
                
                for grade in grades_data:
                    student_scores = _calculate_student_scores(
                        session,
                        grade_id=grade['id'],
                        report_type=report_type,
                        term=term,
                        month=month,
                        academic_year_id=academic_year_id,
                    )
                    
                    results.append({
                        'grade': grade,
                        'students': student_scores,
                    })
                
                return results
        
        def _on_result(data):
            """عند اكتمال الحساب."""
            self._is_generating = False
            self.loading_overlay.hide_loading()
            
            # ✅ عرض النتائج
            self._clear_results()
            
            if not data:
                self._create_empty_card_generic("لا توجد صفوف")
                return
            
            has_any_data = False
            
            for result in data:
                grade = result['grade']
                student_scores = result['students']
                
                if student_scores:
                    has_any_data = True
                    self._create_grade_result_card(
                        grade, student_scores, report_type
                    )
            
            if not has_any_data:
                self._create_empty_card_generic(
                    "لا توجد درجات مسجلة للفترة المحددة"
                )
        
        def _on_error(error_msg):
            """عند حدوث خطأ."""
            self._is_generating = False
            self.loading_overlay.hide_loading()
            self._create_error_card(f"فشل توليد الكشف: {error_msg}")
        
        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
    
    # ============================================================
    # ✅ عرض النتائج
    # ============================================================
    
    def _create_grade_result_card(self, grade: Dict, 
                                    student_scores: List[Dict], 
                                    report_type: str):
        """إنشاء بطاقة نتائج للصف."""
        card = QFrame()
        card.setObjectName("filterCard")
        card.setStyleSheet("""
            QFrame#filterCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        
        # عنوان الصف
        title_layout = QHBoxLayout()
        
        trophy_icon = QLabel()
        trophy_icon.setPixmap(
            qta.icon('fa5s.trophy', color='#F59E0B').pixmap(30, 30)
        )
        title_layout.addWidget(trophy_icon)
        
        grade_title = QLabel(
            f"الصف: {grade['grade_name']} - {grade['stage_name']}"
        )
        grade_title.setStyleSheet(
            "font-size: 18px; font-weight: 700; color: #0F172A;"
        )
        title_layout.addWidget(grade_title)
        
        title_layout.addStretch()
        
        # شارة نوع الكشف
        type_badge = QLabel(report_type)
        type_badge.setStyleSheet("""
            background: #FEF3C7;
            color: #D97706;
            padding: 5px 15px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 12px;
        """)
        title_layout.addWidget(type_badge)
        
        card_layout.addLayout(title_layout)
        
        # جدول الأوائل
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "الترتيب", "رقم الطالب", "اسم الطالب", "المجموع", "النسبة"
        ])
        table.setColumnWidth(0, 60)
        table.setColumnWidth(1, 100)
        table.setColumnWidth(2, 200)
        table.setColumnWidth(3, 100)
        table.setColumnWidth(4, 100)
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        
        table.setRowCount(len(student_scores))
        
        medals = ["🥇", "🥈", "🥉"]
        
        for row, student in enumerate(student_scores):
            # الترتيب
            if row < 3:
                rank_item = QTableWidgetItem(f"{medals[row]} {row + 1}")
                rank_item.setFont(QFont("Cairo", 12, QFont.Weight.Bold))
            else:
                rank_item = QTableWidgetItem(str(row + 1))
            
            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 0, rank_item)
            
            table.setItem(
                row, 1, QTableWidgetItem(student['student_number'])
            )
            table.setItem(
                row, 2, QTableWidgetItem(student['full_name'])
            )
            
            # المجموع
            total_item = QTableWidgetItem(f"{student['total_score']:.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item.setFont(QFont("Cairo", 10, QFont.Weight.Bold))
            table.setItem(row, 3, total_item)
            
            # النسبة
            percentage = student['percentage']
            percentage_item = QTableWidgetItem(f"{percentage:.2f}%")
            percentage_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # تلوين النسبة حسب الدرجة
            if percentage >= 90:
                percentage_item.setForeground(QColor('#10B981'))
            elif percentage >= 80:
                percentage_item.setForeground(QColor('#1976D3'))
            elif percentage >= 70:
                percentage_item.setForeground(QColor('#06B6D4'))
            elif percentage >= 50:
                percentage_item.setForeground(QColor('#F59E0B'))
            else:
                percentage_item.setForeground(QColor('#EF4444'))
            
            table.setItem(row, 4, percentage_item)
            
            table.setRowHeight(row, 35)

        # ضبط ارتفاع الجدول
        total_height = (
            table.horizontalHeader().height() + 
            (len(student_scores) * 35) + 5
        )
        table.setMinimumHeight(total_height)
        
        card_layout.addWidget(table)
        
        # زر الطباعة
        print_btn = GradientButton("طباعة الكشف", "fa5s.print")
        print_btn.clicked.connect(self.generate_print)
        card_layout.addWidget(print_btn)
        
        self.results_layout.addWidget(card)
    
    def _create_empty_card_generic(self, message: str):
        """إنشاء بطاقة فارغة عامة."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #F8FAFC;
                border: 2px dashed #E2E8F0;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        icon_label = QLabel()
        icon_label.setPixmap(
            qta.icon('fa5s.info-circle', color='#94A3B8').pixmap(40, 40)
        )
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        message_label = QLabel(message)
        message_label.setStyleSheet("font-size: 14px; color: #64748B;")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)
        
        self.results_layout.addWidget(card)
    
    def _create_error_card(self, message: str):
        """إنشاء بطاقة خطأ."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #FEF2F2;
                border: 2px solid #EF4444;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        error_label = QLabel(f"⚠️ {message}")
        error_label.setStyleSheet(
            "font-size: 14px; color: #DC2626; font-weight: 600;"
        )
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(error_label)
        
        self.results_layout.addWidget(card)
    
    # ============================================================
    # ✅ الطباعة
    # ============================================================
    
    def generate_print(self):
        """طباعة الكشف."""
        if self.permission_service and not self.permission_service.can_print("الشهادات والأوائل"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للطباعة في الشهادات والأوائل"
            )
            return
        
        QMessageBox.information(
            self, 
            "طباعة", 
            "سيتم تنفيذ الطباعة في مرحلة التقارير والطباعة"
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
        self._show_placeholder()


# ============================================================
# ✅ دالة حساب درجات الطلاب (تعمل داخل الجلسة)
# ============================================================

def _calculate_student_scores(session, grade_id: int, report_type: str, 
                                term: int, month: int, 
                                academic_year_id: int) -> List[Dict]:
    """
    حساب درجات الطلاب لصف معين.
    
    ✅ تعمل داخل الجلسة - تُعيد dicts فقط
    ✅ بدون N+1 (استعلام واحد لكل تقرير)
    """
    # ============ 1. جلب الطلاب ============
    students = session.execute(
        select(Student).where(
            Student.grade_id == grade_id,
            Student.academic_year_id == academic_year_id,
            Student.status == 'مستمر'
        )
    ).scalars().all()
    
    if not students:
        return []
    
    student_ids = [s.id for s in students]
    student_map = {s.id: s for s in students}
    
    # ============ 2. جلب كل البيانات مُجمّعة (batch) ============
    student_scores = []
    
    if report_type == "شهري":
        # ✅ استعلام واحد لكل الطلاب
        monthly_data = session.execute(
            select(
                MonthlyEvaluation.student_id,
                func.sum(
                    MonthlyEvaluation.written_score +
                    MonthlyEvaluation.oral_score +
                    MonthlyEvaluation.homework_score +
                    MonthlyEvaluation.attendance_score
                ).label('total_score'),
                func.count(
                    func.distinct(MonthlyEvaluation.subject_id)
                ).label('subjects_count')
            ).where(
                MonthlyEvaluation.student_id.in_(student_ids),
                MonthlyEvaluation.term == term,
                MonthlyEvaluation.month == month,
                MonthlyEvaluation.academic_year_id == academic_year_id
            ).group_by(MonthlyEvaluation.student_id)
        ).all()
        
        for student_id, total_score, subjects_count in monthly_data:
            total_score = float(total_score or 0)
            subjects_count = int(subjects_count or 0)
            max_score = subjects_count * 100 if subjects_count > 0 else 1
            percentage = (total_score / max_score) * 100
            
            student = student_map.get(student_id)
            if student:
                student_scores.append({
                    'student_number': student.student_number or '',
                    'full_name': student.full_name or '',
                    'total_score': total_score,
                    'percentage': percentage,
                })
    
    elif report_type == "فصلي":
        # ✅ استعلام واحد للجميع
        monthly_data = session.execute(
            select(
                MonthlyEvaluation.student_id,
                func.sum(
                    MonthlyEvaluation.written_score +
                    MonthlyEvaluation.oral_score +
                    MonthlyEvaluation.homework_score +
                    MonthlyEvaluation.attendance_score
                ).label('monthly_total'),
                func.count(
                    func.distinct(MonthlyEvaluation.subject_id)
                ).label('subjects_count')
            ).where(
                MonthlyEvaluation.student_id.in_(student_ids),
                MonthlyEvaluation.term == term,
                MonthlyEvaluation.academic_year_id == academic_year_id
            ).group_by(MonthlyEvaluation.student_id)
        ).all()
        
        # ✅ استعلام واحد للاختبارات
        exam_data = session.execute(
            select(
                TermExamScore.student_id,
                func.sum(TermExamScore.exam_score).label('exam_total')
            ).where(
                TermExamScore.student_id.in_(student_ids),
                TermExamScore.term == term,
                TermExamScore.academic_year_id == academic_year_id
            ).group_by(TermExamScore.student_id)
        ).all()
        
        exam_map = {sid: float(total or 0) for sid, total in exam_data}
        
        for student_id, monthly_total, subjects_count in monthly_data:
            monthly_total = float(monthly_total or 0)
            subjects_count = int(subjects_count or 0)
            exam_total = exam_map.get(student_id, 0.0)
            
            monthly_avg = monthly_total / subjects_count if subjects_count > 0 else 0
            works_score = monthly_avg * 0.2
            
            max_score = subjects_count * 50 if subjects_count > 0 else 1
            total_score = works_score * subjects_count + exam_total
            percentage = (total_score / max_score) * 100
            
            student = student_map.get(student_id)
            if student:
                student_scores.append({
                    'student_number': student.student_number or '',
                    'full_name': student.full_name or '',
                    'total_score': total_score,
                    'percentage': percentage,
                })
    
    else:  # سنوي
        # ✅ استعلام واحد للجميع
        monthly_data = session.execute(
            select(
                MonthlyEvaluation.student_id,
                func.sum(
                    MonthlyEvaluation.written_score +
                    MonthlyEvaluation.oral_score +
                    MonthlyEvaluation.homework_score +
                    MonthlyEvaluation.attendance_score
                ).label('monthly_total'),
                func.count(
                    func.distinct(MonthlyEvaluation.subject_id)
                ).label('subjects_count')
            ).where(
                MonthlyEvaluation.student_id.in_(student_ids),
                MonthlyEvaluation.academic_year_id == academic_year_id
            ).group_by(MonthlyEvaluation.student_id)
        ).all()
        
        exam_data = session.execute(
            select(
                TermExamScore.student_id,
                func.sum(TermExamScore.exam_score).label('exam_total')
            ).where(
                TermExamScore.student_id.in_(student_ids),
                TermExamScore.academic_year_id == academic_year_id
            ).group_by(TermExamScore.student_id)
        ).all()
        
        exam_map = {sid: float(total or 0) for sid, total in exam_data}
        
        for student_id, monthly_total, subjects_count in monthly_data:
            monthly_total = float(monthly_total or 0)
            subjects_count = int(subjects_count or 0)
            exam_total = exam_map.get(student_id, 0.0)
            
            monthly_avg = (
                monthly_total / (subjects_count * 6) 
                if subjects_count > 0 else 0
            )
            works_score = monthly_avg * 0.2
            
            max_score = subjects_count * 100 if subjects_count > 0 else 1
            total_score = works_score * subjects_count * 2 + exam_total
            percentage = (total_score / max_score) * 100
            
            student = student_map.get(student_id)
            if student:
                student_scores.append({
                    'student_number': student.student_number or '',
                    'full_name': student.full_name or '',
                    'total_score': total_score,
                    'percentage': percentage,
                })
    
    # ترتيب تنازلي حسب النسبة
    student_scores.sort(key=lambda x: x['percentage'], reverse=True)
    
    return student_scores[:10]  # أول 10 طلاب