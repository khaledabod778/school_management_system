"""
واجهة التقارير والإحصائيات - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta
from datetime import date

from app.database.session import session_scope
from app.database.models import (
    Student, Receipt, ExpenseVoucher, PayrollRecord, Employee,
    Grade, Section, AcademicYear
)
from app.services.report_service import ReportService
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    PageHeader, Card, GradientButton, QDateEditEN, QSpinBoxEN
)
from app.views.widgets.dialogs import SuccessDialog, ErrorDialog
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class ReportsPage(QWidget):
    """صفحة التقارير - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, 
                 permission_service: Optional[PermissionService] = None, 
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        # ✅ تعريف permission_service (كان مفقوداً)
        self.permission_service = permission_service
        self.report_service = ReportService()
        
        # ✅ تخزين ID السنة قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        
        # ✅ dicts للبيانات
        self.grades_data: List[Dict] = []
        self.sections_data: List[Dict] = []
        
        # ✅ منع التوليد المزدوج
        self._is_generating = False
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل أولي للفلاتر (كان مفقوداً!)
        QTimer.singleShot(100, self.load_data)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)
        
        header = PageHeader(
            "التقارير والإحصائيات",
            "توليد التقارير وطباعتها"
        )
        main_layout.addWidget(header)
        
        # تبويبات التقارير
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                background: white;
                padding: 15px;
            }
        """)
        
        # تبويب التقارير الأكاديمية
        academic_tab = self._create_academic_reports_tab()
        tabs.addTab(academic_tab, "التقارير الأكاديمية")
        
        # تبويب التقارير المالية
        financial_tab = self._create_financial_reports_tab()
        tabs.addTab(financial_tab, "التقارير المالية")
        
        # تبويب تقارير الموظفين
        employee_tab = self._create_employee_reports_tab()
        tabs.addTab(employee_tab, "تقارير الموظفين")
        
        main_layout.addWidget(tabs)
    
    def _create_academic_reports_tab(self) -> QWidget:
        """إنشاء تبويب التقارير الأكاديمية."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # بطاقة كشف الطلاب
        students_card = Card("كشف أسماء الطلاب")
        
        students_layout = QHBoxLayout()
        students_layout.addWidget(QLabel("الصف:"))
        self.students_grade_combo = QComboBox()
        self.students_grade_combo.addItem("جميع الصفوف", None)
        students_layout.addWidget(self.students_grade_combo)
        
        students_layout.addWidget(QLabel("الشعبة:"))
        self.students_section_combo = QComboBox()
        self.students_section_combo.addItem("جميع الشعب", None)
        students_layout.addWidget(self.students_section_combo)
        
        students_layout.addStretch()
        
        generate_btn = GradientButton("توليد التقرير", "fa5s.file-pdf")
        generate_btn.clicked.connect(self.generate_students_report)
        students_layout.addWidget(generate_btn)
        
        students_card.add_widget(self._create_widget(students_layout))
        layout.addWidget(students_card)
        
        # بطاقة تقرير الحضور
        attendance_card = Card("تقرير الحضور والغياب")
        
        attendance_layout = QHBoxLayout()
        attendance_layout.addWidget(QLabel("من:"))
        self.attendance_from = QDateEditEN(QDate.currentDate().addMonths(-1))
        attendance_layout.addWidget(self.attendance_from)
        
        attendance_layout.addWidget(QLabel("إلى:"))
        self.attendance_to = QDateEditEN()
        attendance_layout.addWidget(self.attendance_to)
        
        attendance_layout.addStretch()
        
        # ✅ تفعيل الزر (كان معطلاً!)
        generate_attendance_btn = GradientButton("توليد التقرير", "fa5s.file-pdf")
        generate_attendance_btn.setObjectName("successButton")
        generate_attendance_btn.clicked.connect(self.generate_attendance_report)
        attendance_layout.addWidget(generate_attendance_btn)
        
        attendance_card.add_widget(self._create_widget(attendance_layout))
        layout.addWidget(attendance_card)
        
        layout.addStretch()
        
        return widget
    
    def _create_financial_reports_tab(self) -> QWidget:
        """إنشاء تبويب التقارير المالية."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # بطاقة التقرير المالي
        financial_card = Card("التقرير المالي الشامل")
        
        financial_layout = QHBoxLayout()
        financial_layout.addWidget(QLabel("من:"))
        self.financial_from = QDateEditEN(QDate.currentDate().addMonths(-1))
        financial_layout.addWidget(self.financial_from)
        
        financial_layout.addWidget(QLabel("إلى:"))
        self.financial_to = QDateEditEN()
        financial_layout.addWidget(self.financial_to)
        
        financial_layout.addStretch()
        
        generate_financial_btn = GradientButton("توليد التقرير", "fa5s.file-pdf")
        generate_financial_btn.setObjectName("primaryButton")
        generate_financial_btn.clicked.connect(self.generate_financial_report)
        financial_layout.addWidget(generate_financial_btn)
        
        financial_card.add_widget(self._create_widget(financial_layout))
        layout.addWidget(financial_card)
        
        # بطاقة تقرير الديون
        debts_card = Card("تقرير الديون والمبالغ المتبقية")
        
        debts_layout = QHBoxLayout()
        debts_layout.addWidget(QLabel("الصف:"))
        self.debts_grade_combo = QComboBox()
        self.debts_grade_combo.addItem("جميع الصفوف", None)
        debts_layout.addWidget(self.debts_grade_combo)
        
        debts_layout.addStretch()
        
        # ✅ تفعيل الزر (كان معطلاً!)
        generate_debts_btn = GradientButton("توليد التقرير", "fa5s.file-pdf")
        generate_debts_btn.setObjectName("dangerButton")
        generate_debts_btn.clicked.connect(self.generate_debts_report)
        debts_layout.addWidget(generate_debts_btn)
        
        debts_card.add_widget(self._create_widget(debts_layout))
        layout.addWidget(debts_card)
        
        layout.addStretch()
        
        return widget
    
    def _create_employee_reports_tab(self) -> QWidget:
        """إنشاء تبويب تقارير الموظفين."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # بطاقة كشف الرواتب
        payroll_card = Card("كشف الرواتب الشهري")
        
        payroll_layout = QHBoxLayout()
        payroll_layout.addWidget(QLabel("الشهر:"))
        self.payroll_month = QComboBox()
        self.payroll_month.addItems([
            "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
            "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
        ])
        self.payroll_month.setCurrentIndex(date.today().month - 1)
        payroll_layout.addWidget(self.payroll_month)
        
        payroll_layout.addWidget(QLabel("السنة:"))
        self.payroll_year = QSpinBoxEN(2010, 2030)
        self.payroll_year.setValue(date.today().year)
        payroll_layout.addWidget(self.payroll_year)
        
        payroll_layout.addStretch()
        
        generate_payroll_btn = GradientButton("توليد الكشف", "fa5s.file-pdf")
        generate_payroll_btn.setObjectName("successButton")
        generate_payroll_btn.clicked.connect(self.generate_payroll_report)
        payroll_layout.addWidget(generate_payroll_btn)
        
        payroll_card.add_widget(self._create_widget(payroll_layout))
        layout.addWidget(payroll_card)
        
        layout.addStretch()
        
        return widget
    
    def _create_widget(self, layout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    # ============================================================
    # ✅ التحميل غير المتزامن - الفلاتر
    # ============================================================
    
    def load_data(self):
        """تحميل الصفوف والشعب في الخلفية."""
        self.loading_overlay.show_loading("جاري تحميل الفلاتر...")
        
        def _fetch_data():
            with session_scope() as session:
                # ✅ الصفوف
                grades = session.execute(
                    select(Grade).order_by(Grade.grade_name)
                ).scalars().all()
                
                grades_data = [
                    {'id': g.id, 'name': g.grade_name or ''}
                    for g in grades
                ]
                
                # ✅ الشعب مع الصفوف
                sections = session.execute(
                    select(Section)
                    .options(joinedload(Section.grade))
                    .order_by(Section.section_name)
                ).unique().scalars().all()
                
                sections_data = [
                    {
                        'id': s.id,
                        'name': s.section_name or '',
                        'grade_id': s.grade_id,
                        'grade_name': s.grade.grade_name if s.grade else '',
                    }
                    for s in sections
                ]
                
                return {
                    'grades': grades_data,
                    'sections': sections_data,
                }
        
        def _on_result(data):
            try:
                self.grades_data = data['grades']
                self.sections_data = data['sections']
                
                # ============ تحديث students_grade_combo ============
                self.students_grade_combo.blockSignals(True)
                self.students_grade_combo.clear()
                self.students_grade_combo.addItem("جميع الصفوف", None)
                for grade in self.grades_data:
                    self.students_grade_combo.addItem(grade['name'], grade['id'])
                self.students_grade_combo.blockSignals(False)
                
                # ============ تحديث students_section_combo ============
                self.students_section_combo.blockSignals(True)
                self.students_section_combo.clear()
                self.students_section_combo.addItem("جميع الشعب", None)
                for section in self.sections_data:
                    display = (
                        f"{section['grade_name']} - {section['name']}"
                        if section['grade_name'] else section['name']
                    )
                    self.students_section_combo.addItem(display, section['id'])
                self.students_section_combo.blockSignals(False)
                
                # ============ تحديث debts_grade_combo ============
                self.debts_grade_combo.blockSignals(True)
                self.debts_grade_combo.clear()
                self.debts_grade_combo.addItem("جميع الصفوف", None)
                for grade in self.grades_data:
                    self.debts_grade_combo.addItem(grade['name'], grade['id'])
                self.debts_grade_combo.blockSignals(False)
                
            except Exception as e:
                print(f"خطأ في تحديث الواجهة: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()
        
        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            print(f"فشل تحميل الفلاتر: {error_msg}")
        
        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
    
    # ============================================================
    # ✅ توليد تقرير الطلاب (Async)
    # ============================================================
    
    def generate_students_report(self):
        """توليد تقرير الطلاب في الخلفية."""
        if self.permission_service and not self.permission_service.can_print("التقارير"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية لتوليد التقارير"
            )
            return
        
        if self._is_generating:
            return
        
        self._is_generating = True
        
        grade_id = self.students_grade_combo.currentData()
        section_id = self.students_section_combo.currentData()
        academic_year_id = self.academic_year_id
        
        self.loading_overlay.show_loading("جاري توليد تقرير الطلاب...")
        
        def _fetch_data():
            """جلب الطلاب (في الخلفية)."""
            with session_scope() as session:
                query = select(Student).where(
                    Student.academic_year_id == academic_year_id
                )
                
                if grade_id:
                    query = query.where(Student.grade_id == grade_id)
                if section_id:
                    query = query.where(Student.section_id == section_id)
                
                query = query.order_by(Student.full_name)
                students = session.execute(query).scalars().all()
                
                # ✅ تحويل إلى dicts
                return [
                    {
                        'student_number': s.student_number or '',
                        'full_name': s.full_name or '',
                        'gender': s.gender or '',
                        'status': s.status or '',
                    }
                    for s in students
                ]
        
        def _on_result(data):
            """عند اكتمال جلب الطلاب."""
            if not data:
                self.loading_overlay.hide_loading()
                self._is_generating = False
                ErrorDialog("تنبيه", "لا يوجد طلاب مطابقون للفلاتر", self).exec()
                return
            
            # ✅ توليد PDF في الخلفية (ثقيل)
            def _generate_pdf():
                filename = (
                    f"students_report_{date.today().strftime('%Y%m%d')}.pdf"
                )
                # ✅ نمرر dicts بدلاً من ORM
                self.report_service.generate_student_list_report(data, filename)
                return filename
            
            def _on_pdf_result(filename):
                self.loading_overlay.hide_loading()
                self._is_generating = False
                SuccessDialog(
                    "نجاح",
                    f"تم توليد التقرير: {filename}",
                    self
                ).exec()
            
            def _on_pdf_error(error_msg):
                self.loading_overlay.hide_loading()
                self._is_generating = False
                ErrorDialog(
                    "خطأ",
                    f"فشل توليد التقرير:\n{error_msg}",
                    self
                ).exec()
            
            run_async(_generate_pdf, on_result=_on_pdf_result, on_error=_on_pdf_error)
        
        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            self._is_generating = False
            ErrorDialog(
                "خطأ",
                f"فشل تحميل البيانات:\n{error_msg}",
                self
            ).exec()
        
        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
    
    # ============================================================
    # ✅ توليد التقرير المالي (Async)
    # ============================================================
    
    def generate_financial_report(self):
        """توليد التقرير المالي في الخلفية."""
        if self.permission_service and not self.permission_service.can_print("التقارير"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية لتوليد التقارير"
            )
            return
        
        if self._is_generating:
            return
        
        self._is_generating = True
        
        from_date = self.financial_from.date().toPython()
        to_date = self.financial_to.date().toPython()
        
        # ✅ التحقق من صحة النطاق
        if from_date > to_date:
            self._is_generating = False
            ErrorDialog(
                "تنبيه",
                "تاريخ البداية يجب أن يكون قبل تاريخ النهاية",
                self
            ).exec()
            return
        
        self.loading_overlay.show_loading("جاري توليد التقرير المالي...")
        
        def _fetch_data():
            """جلب السندات (في الخلفية)."""
            with session_scope() as session:
                from datetime import datetime, time as dt_time
                from_dt = datetime.combine(from_date, dt_time.min)
                to_dt = datetime.combine(to_date, dt_time.max)
                
                receipts = session.execute(
                    select(Receipt).where(
                        Receipt.payment_date >= from_dt,
                        Receipt.payment_date <= to_dt,
                        Receipt.status == 'نشط'
                    )
                ).scalars().all()
                
                vouchers = session.execute(
                    select(ExpenseVoucher).where(
                        ExpenseVoucher.payment_date >= from_dt,
                        ExpenseVoucher.payment_date <= to_dt,
                        ExpenseVoucher.status == 'نشط'
                    )
                ).scalars().all()
                
                # ✅ تحويل إلى dicts
                receipts_data = [
                    {
                        'receipt_number': r.receipt_number or '',
                        'amount_paid': float(r.amount_paid or 0),
                        'payment_date': r.payment_date,
                        'payment_method': r.payment_method or '',
                    }
                    for r in receipts
                ]
                
                vouchers_data = [
                    {
                        'voucher_number': v.voucher_number or '',
                        'amount': float(v.amount or 0),
                        'payment_date': v.payment_date,
                        'expense_category': v.expense_category or '',
                    }
                    for v in vouchers
                ]
                
                return {
                    'receipts': receipts_data,
                    'vouchers': vouchers_data,
                }
        
        def _on_result(data):
            """عند اكتمال جلب البيانات."""
            def _generate_pdf():
                filename = (
                    f"financial_report_{date.today().strftime('%Y%m%d')}.pdf"
                )
                self.report_service.generate_financial_report(
                    from_date, to_date,
                    data['receipts'], data['vouchers'],
                    filename
                )
                return filename
            
            def _on_pdf_result(filename):
                self.loading_overlay.hide_loading()
                self._is_generating = False
                SuccessDialog(
                    "نجاح",
                    f"تم توليد التقرير المالي: {filename}",
                    self
                ).exec()
            
            def _on_pdf_error(error_msg):
                self.loading_overlay.hide_loading()
                self._is_generating = False
                ErrorDialog(
                    "خطأ",
                    f"فشل توليد التقرير:\n{error_msg}",
                    self
                ).exec()
            
            run_async(_generate_pdf, on_result=_on_pdf_result, on_error=_on_pdf_error)
        
        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            self._is_generating = False
            ErrorDialog(
                "خطأ",
                f"فشل تحميل البيانات:\n{error_msg}",
                self
            ).exec()
        
        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
    
    # ============================================================
    # ✅ توليد كشف الرواتب (Async)
    # ============================================================
    
    def generate_payroll_report(self):
        """توليد كشف الرواتب في الخلفية."""
        if self.permission_service and not self.permission_service.can_print("التقارير"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية لتوليد التقارير"
            )
            return
        
        if self._is_generating:
            return
        
        self._is_generating = True
        
        month = self.payroll_month.currentIndex() + 1
        year = self.payroll_year.value()
        
        self.loading_overlay.show_loading("جاري توليد كشف الرواتب...")
        
        def _fetch_data():
            """جلب سجلات الرواتب (في الخلفية)."""
            with session_scope() as session:
                payroll_query = session.execute(
                    select(PayrollRecord)
                    .options(joinedload(PayrollRecord.employee))
                    .join(Employee, PayrollRecord.employee_id == Employee.id)
                    .where(
                        PayrollRecord.month == month,
                        PayrollRecord.year == year
                    )
                ).unique().scalars().all()
                
                # ✅ تحويل إلى dicts
                return [
                    {
                        'employee_name': (
                            p.employee.full_name 
                            if p.employee else ''
                        ),
                        'basic_salary': float(p.basic_salary or 0),
                        'total_allowances': float(p.total_allowances or 0),
                        'total_deductions': float(p.total_deductions or 0),
                        'loan_deduction': float(p.loan_deduction or 0),
                        'net_salary': float(p.net_salary or 0),
                        'payment_status': p.payment_status or '',
                    }
                    for p in payroll_query
                ]
        
        def _on_result(data):
            """عند اكتمال جلب البيانات."""
            if not data:
                self.loading_overlay.hide_loading()
                self._is_generating = False
                ErrorDialog(
                    "تنبيه",
                    "لا توجد سجلات رواتب لهذا الشهر",
                    self
                ).exec()
                return
            
            def _generate_pdf():
                filename = f"payroll_{year}_{month}.pdf"
                self.report_service.generate_payroll_report(
                    data, month, year, filename
                )
                return filename
            
            def _on_pdf_result(filename):
                self.loading_overlay.hide_loading()
                self._is_generating = False
                SuccessDialog(
                    "نجاح",
                    f"تم توليد كشف الرواتب: {filename}",
                    self
                ).exec()
            
            def _on_pdf_error(error_msg):
                self.loading_overlay.hide_loading()
                self._is_generating = False
                ErrorDialog(
                    "خطأ",
                    f"فشل توليد الكشف:\n{error_msg}",
                    self
                ).exec()
            
            run_async(_generate_pdf, on_result=_on_pdf_result, on_error=_on_pdf_error)
        
        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            self._is_generating = False
            ErrorDialog(
                "خطأ",
                f"فشل تحميل البيانات:\n{error_msg}",
                self
            ).exec()
        
        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
    
    # ============================================================
    # ✅ تقرير الحضور (Async) - كان معطلاً
    # ============================================================
    
    def generate_attendance_report(self):
        """توليد تقرير الحضور والغياب."""
        if self.permission_service and not self.permission_service.can_print("التقارير"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية لتوليد التقارير"
            )
            return
        
        if self._is_generating:
            return
        
        from_date = self.attendance_from.date().toPython()
        to_date = self.attendance_to.date().toPython()
        
        if from_date > to_date:
            ErrorDialog(
                "تنبيه",
                "تاريخ البداية يجب أن يكون قبل تاريخ النهاية",
                self
            ).exec()
            return
        
        self._is_generating = True
        academic_year_id = self.academic_year_id
        
        self.loading_overlay.show_loading("جاري توليد تقرير الحضور...")
        
        def _fetch_data():
            """جلب بيانات الحضور (في الخلفية)."""
            from app.database.models import DailyAttendance
            
            with session_scope() as session:
                attendance = session.execute(
                    select(DailyAttendance)
                    .where(
                        DailyAttendance.academic_year_id == academic_year_id,
                        DailyAttendance.attendance_date >= from_date,
                        DailyAttendance.attendance_date <= to_date
                    )
                    .order_by(DailyAttendance.attendance_date)
                ).scalars().all()
                
                return [
                    {
                        'attendance_date': a.attendance_date,
                        'status': a.status or '',
                        'notes': a.notes or '',
                        'student_id': a.student_id,
                    }
                    for a in attendance
                ]
        
        def _on_result(data):
            """عند اكتمال جلب البيانات."""
            if not data:
                self.loading_overlay.hide_loading()
                self._is_generating = False
                ErrorDialog(
                    "تنبيه",
                    "لا توجد بيانات حضور في هذه الفترة",
                    self
                ).exec()
                return
            
            # ✅ توليد PDF (نفترض وجود الدالة في ReportService)
            def _generate_pdf():
                filename = (
                    f"attendance_report_{date.today().strftime('%Y%m%d')}.pdf"
                )
                # ⚠️ تأكد من وجود هذه الدالة في ReportService
                if hasattr(self.report_service, 'generate_attendance_report'):
                    self.report_service.generate_attendance_report(
                        from_date, to_date, data, filename
                    )
                    return filename
                else:
                    raise NotImplementedError(
                        "دالة generate_attendance_report غير موجودة في ReportService"
                    )
            
            def _on_pdf_result(filename):
                self.loading_overlay.hide_loading()
                self._is_generating = False
                SuccessDialog(
                    "نجاح",
                    f"تم توليد التقرير: {filename}",
                    self
                ).exec()
            
            def _on_pdf_error(error_msg):
                self.loading_overlay.hide_loading()
                self._is_generating = False
                ErrorDialog(
                    "خطأ",
                    f"فشل توليد التقرير:\n{error_msg}",
                    self
                ).exec()
            
            run_async(_generate_pdf, on_result=_on_pdf_result, on_error=_on_pdf_error)
        
        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            self._is_generating = False
            ErrorDialog(
                "خطأ",
                f"فشل تحميل البيانات:\n{error_msg}",
                self
            ).exec()
        
        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
    
    # ============================================================
    # ✅ تقرير الديون (Async) - كان معطلاً
    # ============================================================
    
    def generate_debts_report(self):
        """توليد تقرير الديون والمبالغ المتبقية."""
        if self.permission_service and not self.permission_service.can_print("التقارير"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية لتوليد التقارير"
            )
            return
        
        if self._is_generating:
            return
        
        self._is_generating = True
        grade_id = self.debts_grade_combo.currentData()
        academic_year_id = self.academic_year_id
        
        self.loading_overlay.show_loading("جاري توليد تقرير الديون...")
        
        def _fetch_data():
            """جلب الديون (في الخلفية)."""
            from app.database.models import StudentFee
            from sqlalchemy import func
            
            with session_scope() as session:
                # ✅ جلب الطلاب
                students_query = select(Student).where(
                    Student.academic_year_id == academic_year_id
                )
                if grade_id:
                    students_query = students_query.where(
                        Student.grade_id == grade_id
                    )
                
                students = session.execute(students_query).scalars().all()
                student_ids = [s.id for s in students]
                
                if not student_ids:
                    return []
                
                # ✅ جلب الرسوم مُجمّعة
                fees_data = session.execute(
                    select(
                        StudentFee.student_id,
                        func.sum(StudentFee.net_total_required).label('total')
                    )
                    .where(
                        StudentFee.student_id.in_(student_ids),
                        StudentFee.academic_year_id == academic_year_id
                    )
                    .group_by(StudentFee.student_id)
                ).all()
                
                # ✅ جلب المدفوعات مُجمّعة
                paid_data = session.execute(
                    select(
                        Receipt.student_id,
                        func.sum(Receipt.amount_paid).label('paid')
                    )
                    .where(
                        Receipt.student_id.in_(student_ids),
                        Receipt.status == 'نشط'
                    )
                    .group_by(Receipt.student_id)
                ).all()
                
                # ✅ خريطة الطلاب
                student_map = {s.id: s for s in students}
                fee_map = {sid: float(total or 0) for sid, total in fees_data}
                paid_map = {sid: float(paid or 0) for sid, paid in paid_data}
                
                # ✅ بناء القائمة
                debts = []
                for sid in student_ids:
                    total = fee_map.get(sid, 0.0)
                    paid = paid_map.get(sid, 0.0)
                    remaining = total - paid
                    
                    if remaining > 0:
                        s = student_map[sid]
                        debts.append({
                            'student_number': s.student_number or '',
                            'full_name': s.full_name or '',
                            'total_fees': total,
                            'paid': paid,
                            'remaining': remaining,
                        })
                
                return debts
        
        def _on_result(data):
            """عند اكتمال جلب البيانات."""
            if not data:
                self.loading_overlay.hide_loading()
                self._is_generating = False
                ErrorDialog(
                    "تنبيه",
                    "لا توجد ديون مستحقة",
                    self
                ).exec()
                return
            
            def _generate_pdf():
                filename = (
                    f"debts_report_{date.today().strftime('%Y%m%d')}.pdf"
                )
                # ⚠️ تأكد من وجود هذه الدالة في ReportService
                if hasattr(self.report_service, 'generate_debts_report'):
                    self.report_service.generate_debts_report(data, filename)
                    return filename
                else:
                    raise NotImplementedError(
                        "دالة generate_debts_report غير موجودة في ReportService"
                    )
            
            def _on_pdf_result(filename):
                self.loading_overlay.hide_loading()
                self._is_generating = False
                SuccessDialog(
                    "نجاح",
                    f"تم توليد التقرير: {filename}",
                    self
                ).exec()
            
            def _on_pdf_error(error_msg):
                self.loading_overlay.hide_loading()
                self._is_generating = False
                ErrorDialog(
                    "خطأ",
                    f"فشل توليد التقرير:\n{error_msg}",
                    self
                ).exec()
            
            run_async(_generate_pdf, on_result=_on_pdf_result, on_error=_on_pdf_error)
        
        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            self._is_generating = False
            ErrorDialog(
                "خطأ",
                f"فشل تحميل البيانات:\n{error_msg}",
                self
            ).exec()
        
        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
    
    # ============================================================
    # ✅ الأحداث
    # ============================================================
    
    def resizeEvent(self, event):
        """تحديث حجم طبقة التحميل."""
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())
    
    def refresh(self):
        """إعادة تحميل الفلاتر."""
        self.load_data()