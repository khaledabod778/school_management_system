"""
واجهة الرواتب.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Dict, Optional
import qtawesome as qta
from datetime import date, datetime
from decimal import Decimal

from app.database.session import session_scope
from app.database.models import (
    Employee, PayrollRecord, EmployeeAllowanceDeduction,
    EmployeeLoan, User,
)
from app.services.finance_extras_factory import FinanceExtrasFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    PageHeader, Card, QSpinBoxEN, SearchBox, ModernTable,
    GradientButton,
)
from app.views.widgets.dialogs import (
    ConfirmationDialog, SuccessDialog, ErrorDialog,
)
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select, func, extract
from sqlalchemy.orm import joinedload


class PayrollPage(QWidget):
    """صفحة الرواتب."""

    def __init__(self, user, academic_year,
                 permission_service: Optional[PermissionService] = None,
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        self.user_id = user.id if user else None
        self.all_payroll: List[Dict] = []

        self.setup_ui()
        self.loading_overlay = LoadingOverlay(self)
        QTimer.singleShot(100, self.load_data)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)

        title = QLabel("كشف الرواتب الشهري")
        title.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #0F172A;"
        )
        main_layout.addWidget(title)

        subtitle = QLabel("إدارة رواتب الموظفين والمعلمين")
        subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(subtitle)

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

        filter_layout.addWidget(QLabel("الشهر:"))
        self.month_combo = QComboBox()
        self.month_combo.addItems([
            "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
            "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
        ])
        self.month_combo.setCurrentIndex(date.today().month - 1)
        self.month_combo.currentIndexChanged.connect(self.load_data)
        filter_layout.addWidget(self.month_combo)

        filter_layout.addWidget(QLabel("السنة:"))
        self.year_spin = QSpinBoxEN(2010, 2030)
        self.year_spin.setValue(date.today().year)
        self.year_spin.valueChanged.connect(self.load_data)
        filter_layout.addWidget(self.year_spin)

        filter_layout.addStretch()

        generate_btn = GradientButton("توليد الرواتب", "fa5s.calculator")
        generate_btn.clicked.connect(self.generate_payroll)
        filter_layout.addWidget(generate_btn)

        print_btn = GradientButton("طباعة الكشف", "fa5s.print")
        print_btn.setObjectName("successButton")
        print_btn.clicked.connect(self.print_payroll)
        filter_layout.addWidget(print_btn)

        main_layout.addWidget(filter_card)

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

        toolbar = QHBoxLayout()
        self.count_label = QLabel("عدد الموظفين: 0")
        self.count_label.setObjectName("count_label")
        toolbar.addWidget(self.count_label)
        toolbar.addStretch()

        self.total_label = QLabel("إجمالي الرواتب: 0 ر.ي")
        self.total_label.setStyleSheet("""
            color: #1976D3;
            font-weight: 700;
            padding: 8px 15px;
            border: 2px solid #1976D3;
            border-radius: 10px;
            font-size: 14px;
        """)
        toolbar.addWidget(self.total_label)
        card_layout.addLayout(toolbar)

        self.table = ModernTable()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "الموظف", "الراتب الأساسي", "البدلات", "الخصومات",
            "السلف", "صافي الراتب", "الحالة", "تاريخ الصرف", "إجراء",
        ])
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 110)
        self.table.setColumnWidth(3, 110)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 80)
        self.table.setColumnWidth(7, 140)
        self.table.setColumnWidth(8, 100)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.verticalHeader().setVisible(False)
        card_layout.addWidget(self.table)

        main_layout.addWidget(table_card)

    # ============================================================
    # LOAD
    # ============================================================

    def load_data(self):
        month = self.month_combo.currentIndex() + 1
        year = self.year_spin.value()

        self.loading_overlay.show_loading("جاري التحميل...")

        def _fetch():
            if FinanceExtrasFactory.is_remote():
                return FinanceExtrasFactory.get_service() \
                    .list_payroll(month, year)

            with session_scope() as session:
                records = session.execute(
                    select(PayrollRecord)
                    .options(joinedload(PayrollRecord.employee))
                    .join(
                        Employee,
                        PayrollRecord.employee_id == Employee.id,
                    )
                    .where(
                        PayrollRecord.month == month,
                        PayrollRecord.year == year,
                    )
                    .order_by(Employee.full_name)
                ).unique().scalars().all()

                total_net = 0.0
                payroll_data = []
                for r in records:
                    net = float(r.net_salary or 0)
                    total_net += net
                    payroll_data.append({
                        'id': r.id,
                        'employee_id': r.employee_id,
                        'employee_name': (
                            r.employee.full_name if r.employee else ''
                        ),
                        'basic_salary': float(r.basic_salary or 0),
                        'total_allowances': float(r.total_allowances or 0),
                        'total_deductions': float(r.total_deductions or 0),
                        'loan_deduction': float(r.loan_deduction or 0),
                        'net_salary': net,
                        'payment_status': r.payment_status or '',
                        'payment_date_str': (
                            r.payment_date.strftime("%Y/%m/%d")
                            if r.payment_date else ''
                        ),
                    })
                return {'payroll': payroll_data, 'total_net': total_net}

        def _ok(data):
            try:
                self.all_payroll = data.get('payroll', [])
                self.display_payroll(data.get('total_net', 0))
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            ErrorDialog("خطأ", str(m), self).exec()
            self.all_payroll = []
            self.display_payroll(0)

        run_async(_fetch, on_result=_ok, on_error=_err)

    def display_payroll(self, total_net: float = 0):
        self.table.setRowCount(len(self.all_payroll))

        for row, p in enumerate(self.all_payroll):
            self.table.setItem(
                row, 0, QTableWidgetItem(p['employee_name'])
            )
            self.table.setItem(
                row, 1, QTableWidgetItem(f"{p['basic_salary']:,.2f}")
            )
            self.table.setItem(
                row, 2,
                QTableWidgetItem(f"{p['total_allowances']:,.2f}")
            )
            self.table.setItem(
                row, 3,
                QTableWidgetItem(f"{p['total_deductions']:,.2f}")
            )
            self.table.setItem(
                row, 4,
                QTableWidgetItem(f"{p['loan_deduction']:,.2f}")
            )

            net_item = QTableWidgetItem(f"{p['net_salary']:,.2f}")
            net_item.setForeground(QColor('#10B981'))
            net_item.setFont(QFont("Cairo", 10, QFont.Weight.Bold))
            self.table.setItem(row, 5, net_item)

            status_item = QTableWidgetItem(p['payment_status'])
            if p['payment_status'] == 'مسلم':
                status_item.setForeground(QColor('#10B981'))
            else:
                status_item.setForeground(QColor('#F59E0B'))
            self.table.setItem(row, 6, status_item)

            self.table.setItem(
                row, 7, QTableWidgetItem(p['payment_date_str'])
            )

            pay_btn = QPushButton("صرف")
            pay_btn.setObjectName("successButton")
            pay_btn.setStyleSheet("""
                QPushButton#successButton {
                    border-radius: 6px;
                    padding: 5px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }
            """)
            if p['payment_status'] == 'مسلم':
                pay_btn.setEnabled(False)
                pay_btn.setText("✓ مسلم")

            pay_btn.clicked.connect(
                lambda checked, pid=p['id']: self.pay_salary(pid)
            )
            self.table.setCellWidget(row, 8, pay_btn)

            self.table.setRowHeight(row, 45)

        self.count_label.setText(f"عدد الموظفين: {len(self.all_payroll)}")
        self.total_label.setText(f"إجمالي الرواتب: {total_net:,.0f} ر.ي")

    # ============================================================
    # GENERATE
    # ============================================================

    def generate_payroll(self):
        if self.permission_service \
           and not self.permission_service.can_add("كشف الرواتب"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        month = self.month_combo.currentIndex() + 1
        year = self.year_spin.value()

        reply = QMessageBox.question(
            self, "تأكيد",
            f"توليد رواتب {self.month_combo.currentText()} {year}؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.loading_overlay.show_loading("جاري التوليد...")

        def _gen():
            if FinanceExtrasFactory.is_remote():
                return FinanceExtrasFactory.get_service() \
                    .generate_payroll(month, year)

            generated = 0
            skipped = 0
            with session_scope() as session:
                employees = session.execute(
                    select(Employee).where(Employee.status == 'نشط')
                ).scalars().all()

                for emp in employees:
                    existing = session.execute(
                        select(PayrollRecord).where(
                            PayrollRecord.employee_id == emp.id,
                            PayrollRecord.month == month,
                            PayrollRecord.year == year,
                        )
                    ).scalar_one_or_none()
                    if existing:
                        skipped += 1
                        continue

                    allowances = session.execute(
                        select(func.sum(
                            EmployeeAllowanceDeduction.amount
                        )).where(
                            EmployeeAllowanceDeduction.employee_id == emp.id,
                            EmployeeAllowanceDeduction.type.in_(
                                ['بدل', 'حافز', 'مكافأة']
                            ),
                            extract(
                                'month',
                                EmployeeAllowanceDeduction.date,
                            ) == month,
                            extract(
                                'year',
                                EmployeeAllowanceDeduction.date,
                            ) == year,
                        )
                    ).scalar() or Decimal('0.00')

                    deductions = session.execute(
                        select(func.sum(
                            EmployeeAllowanceDeduction.amount
                        )).where(
                            EmployeeAllowanceDeduction.employee_id == emp.id,
                            EmployeeAllowanceDeduction.type.in_(
                                ['خصم', 'غياب']
                            ),
                            extract(
                                'month',
                                EmployeeAllowanceDeduction.date,
                            ) == month,
                            extract(
                                'year',
                                EmployeeAllowanceDeduction.date,
                            ) == year,
                        )
                    ).scalar() or Decimal('0.00')

                    active_loans = session.execute(
                        select(EmployeeLoan).where(
                            EmployeeLoan.employee_id == emp.id,
                            EmployeeLoan.status == 'مستمرة',
                            EmployeeLoan.remaining_amount > 0,
                        )
                    ).scalars().all()

                    loan_deduction = Decimal('0.00')
                    for loan in active_loans:
                        m = loan.monthly_deduction or Decimal('0')
                        r = loan.remaining_amount or Decimal('0')
                        loan_deduction += m if m <= r else r

                    basic = emp.basic_salary or Decimal('0.00')
                    net = basic + allowances - deductions - loan_deduction

                    session.add(PayrollRecord(
                        employee_id=emp.id,
                        month=month,
                        year=year,
                        basic_salary=basic,
                        total_allowances=allowances,
                        total_deductions=deductions,
                        loan_deduction=loan_deduction,
                        net_salary=net,
                        payment_status='معلق',
                    ))
                    generated += 1
                session.commit()

            return {'generated': generated, 'skipped': skipped}

        def _ok(data):
            self.loading_overlay.hide_loading()
            msg = f"تم توليد {data.get('generated', 0)} راتب"
            if data.get('skipped', 0) > 0:
                msg += f"\nتم تخطي {data['skipped']}"
            SuccessDialog("نجاح", msg, self).exec()
            self.load_data()

        def _err(m):
            self.loading_overlay.hide_loading()
            ErrorDialog("خطأ", str(m), self).exec()

        run_async(_gen, on_result=_ok, on_error=_err)

    # ============================================================
    # PAY
    # ============================================================

    def pay_salary(self, payroll_id: int):
        if self.permission_service \
           and not self.permission_service.can_edit("كشف الرواتب"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        payroll = next(
            (p for p in self.all_payroll if p['id'] == payroll_id),
            None,
        )
        if not payroll:
            return

        if ConfirmationDialog(
            "صرف راتب",
            f"صرف راتب {payroll['employee_name']} - "
            f"{payroll['net_salary']:,.2f} ر.ي؟",
            self,
        ).exec() != QDialog.DialogCode.Accepted:
            return

        self.loading_overlay.show_loading("جاري الصرف...")

        def _pay():
            if FinanceExtrasFactory.is_remote():
                return FinanceExtrasFactory.get_service() \
                    .pay_salary(payroll_id)

            with session_scope() as session:
                rec = session.get(PayrollRecord, payroll_id)
                if not rec:
                    raise ValueError("السجل غير موجود")
                if rec.payment_status == 'مسلم':
                    raise ValueError("تم الصرف مسبقاً")

                rec.payment_status = 'مسلم'
                rec.payment_date = datetime.now()

                details = []
                active_loans = session.execute(
                    select(EmployeeLoan).where(
                        EmployeeLoan.employee_id == rec.employee_id,
                        EmployeeLoan.status == 'مستمرة',
                        EmployeeLoan.remaining_amount > 0,
                    ).order_by(EmployeeLoan.loan_date)
                ).scalars().all()

                remaining_ded = rec.loan_deduction or Decimal('0.00')
                for loan in active_loans:
                    if remaining_ded <= 0:
                        break
                    lr = loan.remaining_amount or Decimal('0.00')
                    if lr <= 0:
                        loan.status = 'منتهية'
                        continue

                    monthly = loan.monthly_deduction or Decimal('0.00')
                    ded = monthly if monthly <= lr else lr
                    if ded > remaining_ded:
                        ded = remaining_ded

                    loan.remaining_amount = lr - ded
                    remaining_ded -= ded

                    details.append(
                        f"سلفة - خصم: {ded:,.2f} - "
                        f"المتبقي: {loan.remaining_amount:,.2f}"
                    )
                    if loan.remaining_amount <= 0:
                        loan.remaining_amount = Decimal('0.00')
                        loan.status = 'منتهية'
                        details.append("✓ تم سداد السلفة")

                session.commit()
                return {
                    'employee_name': payroll['employee_name'],
                    'net_salary': float(rec.net_salary or 0),
                    'details': details,
                }

        def _ok(data):
            self.loading_overlay.hide_loading()
            msg = (
                f"تم صرف راتب {data.get('employee_name', '')} بنجاح\n"
                f"المبلغ: {data.get('net_salary', 0):,.2f} ر.ي"
            )
            if data.get('details'):
                msg += "\n\n" + "\n".join(data['details'])
            SuccessDialog("نجاح", msg, self).exec()
            self.load_data()

        def _err(m):
            self.loading_overlay.hide_loading()
            ErrorDialog("خطأ", str(m), self).exec()

        run_async(_pay, on_result=_ok, on_error=_err)

    def print_payroll(self):
        if self.permission_service \
           and not self.permission_service.can_print("كشف الرواتب"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return
        QMessageBox.information(
            self, "طباعة", "سيتم تنفيذها في مرحلة التقارير"
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())

    def refresh(self):
        self.load_data()