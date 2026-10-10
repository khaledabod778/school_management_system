"""
كشف حساب الموظف التفصيلي.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta
from datetime import date
from decimal import Decimal

from app.database.session import session_scope
from app.database.models import (
    Employee, PayrollRecord, EmployeeAllowanceDeduction,
    EmployeeLoan, User,
)
from app.services.finance_extras_factory import FinanceExtrasFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import GradientButton, SearchBox
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select


class EmployeeStatementPage(QWidget):
    """صفحة كشف حساب الموظف."""

    def __init__(self, user, academic_year,
                 permission_service: Optional[PermissionService] = None,
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service

        self.selected_employee_id: Optional[int] = None
        self.selected_employee_data: Dict = {}
        self.employees_data: List[Dict] = []

        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self.search_employees)

        self.setup_ui()
        self.loading_overlay = LoadingOverlay(self)
        QTimer.singleShot(100, self.search_employees)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        title = QLabel("كشف حساب الموظف التفصيلي")
        title.setStyleSheet(
            "font-size: 22px; font-weight: 800; color: #0F172A;"
        )
        main_layout.addWidget(title)

        subtitle = QLabel(
            "عرض السلف والبدلات والخصومات والرواتب للموظف"
        )
        subtitle.setStyleSheet("font-size: 13px; color: #64748B;")
        main_layout.addWidget(subtitle)

        search_card = QFrame()
        search_card.setObjectName("filterCard")
        search_card.setStyleSheet("""
            QFrame#filterCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        search_layout = QHBoxLayout(search_card)
        self.search_input = SearchBox("بحث عن موظف بالاسم أو الهاتف...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        search_layout.addWidget(self.search_input)
        main_layout.addWidget(search_card)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(15)

        self.employees_list = QListWidget()
        self.employees_list.setMaximumHeight(110)
        self.employees_list.setStyleSheet("""
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
            QListWidget::item:hover { background: #F1F5F9; }
            QListWidget::item:selected {
                background: #EEF2FF;
                color: #0D47A1;
                font-weight: 600;
            }
        """)
        self.employees_list.itemClicked.connect(self.select_employee)
        scroll_layout.addWidget(self.employees_list)

        self.info_card = QFrame()
        self.info_card.setObjectName("filterCard")
        self.info_card.setStyleSheet("""
            QLabel {
                border: 1px solid #1976D3;
                color: #0F172A;
                font-size: 12px;
                border-radius: 6px;
                background: #EEF2FF;
                padding: 10px 15px;
            }
        """)
        self.info_card.setVisible(False)
        self._setup_info_card()
        scroll_layout.addWidget(self.info_card)

        self.loans_summary_card = QFrame()
        self.loans_summary_card.setObjectName("filterCard")
        self.loans_summary_card.setVisible(False)
        self._setup_loans_summary_card()
        scroll_layout.addWidget(self.loans_summary_card)

        self.loans_card = QFrame()
        self.loans_card.setObjectName("tableCard")
        self.loans_card.setVisible(False)
        self._setup_loans_card()
        scroll_layout.addWidget(self.loans_card)

        self.allowances_card = QFrame()
        self.allowances_card.setObjectName("tableCard")
        self.allowances_card.setVisible(False)
        self._setup_allowances_card()
        scroll_layout.addWidget(self.allowances_card)

        self.payroll_card = QFrame()
        self.payroll_card.setObjectName("tableCard")
        self.payroll_card.setVisible(False)
        self._setup_payroll_card()
        scroll_layout.addWidget(self.payroll_card)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        self.print_btn = GradientButton(
            "طباعة كشف الحساب", "fa5s.print"
        )
        self.print_btn.clicked.connect(self.print_statement)
        self.print_btn.setEnabled(False)
        main_layout.addWidget(self.print_btn)

    def _setup_info_card(self):
        layout = QVBoxLayout(self.info_card)
        layout.setSpacing(8)

        self.employee_name_label = QLabel()
        self.employee_name_label.setStyleSheet(
            "font-size: 16px; font-weight: 700; border: none; "
            "padding-top: 0px; background: none;"
        )
        self.employee_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.employee_name_label)

        info_row = QHBoxLayout()
        info_row.addStretch()
        self.employee_job_label = QLabel()
        info_row.addWidget(self.employee_job_label)
        self.employee_phone_label = QLabel()
        info_row.addWidget(self.employee_phone_label)
        self.employee_status_label = QLabel()
        info_row.addWidget(self.employee_status_label)
        self.basic_salary_label = QLabel()
        self.basic_salary_label.setStyleSheet("""
            font-size: 14px; font-weight: 700; color: #1976D3;
            padding: 8px; background: #EEF2FF; border-radius: 6px;
        """)
        info_row.addWidget(self.basic_salary_label)
        info_row.addStretch()
        layout.addLayout(info_row)

    def _setup_loans_summary_card(self):
        layout = QVBoxLayout(self.loans_summary_card)
        layout.setSpacing(10)
        title = QLabel("ملخص السلف")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(1)

        grid.addWidget(self._create_label("إجمالي السلف:"), 0, 0)
        self.total_loans_label = self._create_value_label(
            "0.00", "#EF4444", "#FEF2F2"
        )
        grid.addWidget(self.total_loans_label, 1, 0)

        grid.addWidget(self._create_label("إجمالي المسدد:"), 0, 1)
        self.total_loans_paid_label = self._create_value_label(
            "0.00", "#10B981", "#ECFDF5"
        )
        grid.addWidget(self.total_loans_paid_label, 1, 1)

        grid.addWidget(self._create_label("إجمالي المتبقي:"), 0, 2)
        self.total_loans_remaining_label = self._create_value_label(
            "0.00", "#F59E0B", "#FFFBEB"
        )
        grid.addWidget(self.total_loans_remaining_label, 1, 2)

        grid.addWidget(self._create_label("السلف النشطة:"), 0, 3)
        self.active_loans_count_label = self._create_value_label(
            "0", "#1976D3", "#EEF2FF"
        )
        grid.addWidget(self.active_loans_count_label, 1, 3)

        layout.addLayout(grid)

    def _setup_loans_card(self):
        layout = QVBoxLayout(self.loans_card)
        layout.setSpacing(10)
        title = QLabel("تفاصيل السلف")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        self.loans_table = QTableWidget()
        self.loans_table.setColumnCount(8)
        self.loans_table.setHorizontalHeaderLabels([
            "تاريخ السلفة", "المبلغ الكلي", "القسط الشهري",
            "المسدد", "المتبقي", "الحالة", "السبب", "نسبة السداد",
        ])
        for i, w in enumerate([100, 100, 100, 100, 100, 80, 150, 120]):
            self.loans_table.setColumnWidth(i, w)
        self.loans_table.horizontalHeader().setStretchLastSection(True)
        self.loans_table.setAlternatingRowColors(True)
        self.loans_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.loans_table.verticalHeader().setVisible(False)
        layout.addWidget(self.loans_table)

    def _setup_allowances_card(self):
        layout = QVBoxLayout(self.allowances_card)
        layout.setSpacing(10)
        title = QLabel("البدلات والخصومات")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        self.allowances_table = QTableWidget()
        self.allowances_table.setColumnCount(5)
        self.allowances_table.setHorizontalHeaderLabels([
            "التاريخ", "النوع", "المبلغ", "السبب", "الاتجاه",
        ])
        for i, w in enumerate([100, 100, 100, 200, 100]):
            self.allowances_table.setColumnWidth(i, w)
        self.allowances_table.horizontalHeader().setStretchLastSection(True)
        self.allowances_table.setAlternatingRowColors(True)
        self.allowances_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.allowances_table.verticalHeader().setVisible(False)
        layout.addWidget(self.allowances_table)

    def _setup_payroll_card(self):
        layout = QVBoxLayout(self.payroll_card)
        layout.setSpacing(10)
        title = QLabel("سجل الرواتب")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        self.payroll_table = QTableWidget()
        self.payroll_table.setColumnCount(8)
        self.payroll_table.setHorizontalHeaderLabels([
            "الشهر", "الأساسي", "البدلات", "الخصومات",
            "السلف", "الصافي", "الحالة", "تاريخ الصرف",
        ])
        for i, w in enumerate([80, 100, 100, 100, 100, 100, 70, 120]):
            self.payroll_table.setColumnWidth(i, w)
        self.payroll_table.horizontalHeader().setStretchLastSection(True)
        self.payroll_table.setAlternatingRowColors(True)
        self.payroll_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.payroll_table.verticalHeader().setVisible(False)
        layout.addWidget(self.payroll_table)

    def _create_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            color: #475569; font-weight: 600; font-size: 12px;
            border: 1px solid #E2E8F0; border-radius: 6px;
            padding: 10px; margin: 0px 3px;
        """)
        return label

    def _create_value_label(self, text, color, bg="transparent"):
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"""
            color: {color}; font-weight: 700; font-size: 14px;
            padding: 8px; border: 1px solid #E2E8F0;
            background: {bg}; margin: 0px 3px; border-radius: 6px;
        """)
        return label

    # ============================================================
    # SEARCH
    # ============================================================

    def _on_search_text_changed(self):
        self._search_timer.stop()
        self._search_timer.start()

    def search_employees(self):
        search_text = self.search_input.text().strip()
        self.loading_overlay.show_loading("جاري التحميل...")

        def _fetch():
            if FinanceExtrasFactory.is_remote():
                from app.services.student_factory import StudentFactory
                # نستخدم endpoint من hr_users (سنستخدم service جديد)
                from app.services.auth_factory import AuthFactory
                client = AuthFactory.get_api_client()
                params = {}
                if search_text:
                    params['search'] = search_text
                employees = client.get("/api/hr/employees/", params=params)
                return [
                    {
                        'id': e['id'],
                        'full_name': e['full_name'],
                        'job_title': e.get('job_title', ''),
                    }
                    for e in employees[:30]
                ]

            with session_scope() as session:
                query = select(Employee)
                if search_text:
                    query = query.where(
                        (Employee.full_name.ilike(f"%{search_text}%"))
                        | (Employee.primary_phone.ilike(
                            f"%{search_text}%"
                        ))
                    )
                query = query.order_by(Employee.full_name).limit(30)
                emps = session.execute(query).scalars().all()
                return [
                    {
                        'id': e.id,
                        'full_name': e.full_name or '',
                        'job_title': e.job_title or '',
                    }
                    for e in emps
                ]

        def _ok(data):
            try:
                self.employees_data = data
                self.employees_list.clear()
                for e in data:
                    item = QListWidgetItem(
                        f"{e['full_name']} - {e['job_title']}"
                    )
                    item.setData(Qt.ItemDataRole.UserRole, e['id'])
                    self.employees_list.addItem(item)
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            print(f"فشل: {m}")

        run_async(_fetch, on_result=_ok, on_error=_err)

    def select_employee(self, item: QListWidgetItem):
        employee_id = item.data(Qt.ItemDataRole.UserRole)
        employee = next(
            (e for e in self.employees_data if e['id'] == employee_id),
            None,
        )
        if not employee:
            return

        self.selected_employee_id = employee_id
        self.selected_employee_data = employee
        self.print_btn.setEnabled(True)
        self._load_employee_statement(employee_id)

    # ============================================================
    # LOAD STATEMENT
    # ============================================================

    def _load_employee_statement(self, employee_id: int):
        self.loading_overlay.show_loading("جاري تحميل كشف الحساب...")

        def _fetch():
            if FinanceExtrasFactory.is_remote():
                return FinanceExtrasFactory.get_service() \
                    .get_employee_statement(employee_id)

            # Local
            with session_scope() as session:
                emp = session.get(Employee, employee_id)
                if not emp:
                    return None

                employee_info = {
                    'id': emp.id,
                    'full_name': emp.full_name or '',
                    'job_title': emp.job_title or '',
                    'primary_phone': emp.primary_phone or '',
                    'status': emp.status or 'نشط',
                    'basic_salary': float(emp.basic_salary or 0),
                }

                loans = session.execute(
                    select(EmployeeLoan)
                    .where(EmployeeLoan.employee_id == employee_id)
                    .order_by(EmployeeLoan.loan_date.desc())
                ).scalars().all()

                loans_data = []
                total_loans = Decimal('0.00')
                total_paid = Decimal('0.00')
                total_remaining = Decimal('0.00')
                active_count = 0

                for loan in loans:
                    total_amount = loan.total_loan_amount or Decimal('0.00')
                    remaining = loan.remaining_amount or Decimal('0.00')
                    paid_amount = total_amount - remaining

                    status = loan.status or ''
                    if status == 'مستمرة':
                        active_count += 1

                    pct = 0.0
                    if total_amount > 0:
                        pct = float((paid_amount / total_amount) * 100)

                    loans_data.append({
                        'date_str': (
                            loan.loan_date.strftime("%Y/%m/%d")
                            if loan.loan_date else ''
                        ),
                        'total_amount': float(total_amount),
                        'monthly_deduction': float(
                            loan.monthly_deduction or 0
                        ),
                        'paid_amount': float(paid_amount),
                        'remaining': float(remaining),
                        'status': status,
                        'reason': loan.reason or '',
                        'percentage': pct,
                    })

                    total_loans += total_amount
                    total_paid += paid_amount
                    total_remaining += remaining

                records = session.execute(
                    select(EmployeeAllowanceDeduction)
                    .where(
                        EmployeeAllowanceDeduction.employee_id == employee_id
                    )
                    .order_by(EmployeeAllowanceDeduction.date.desc())
                ).scalars().all()

                allowances_data = []
                for r in records:
                    is_allowance = r.type in ['بدل', 'حافز', 'مكافأة']
                    allowances_data.append({
                        'date_str': (
                            r.date.strftime("%Y/%m/%d") if r.date else ''
                        ),
                        'type': r.type or '',
                        'amount': float(r.amount or 0),
                        'reason': r.reason or '',
                        'is_allowance': is_allowance,
                    })

                payrolls = session.execute(
                    select(PayrollRecord)
                    .where(PayrollRecord.employee_id == employee_id)
                    .order_by(
                        PayrollRecord.year.desc(),
                        PayrollRecord.month.desc(),
                    )
                ).scalars().all()

                months = [
                    "", "يناير", "فبراير", "مارس", "أبريل", "مايو",
                    "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر",
                    "نوفمبر", "ديسمبر",
                ]

                payroll_data = []
                for p in payrolls:
                    month_name = (
                        months[p.month]
                        if 1 <= p.month <= 12 else str(p.month)
                    )
                    payroll_data.append({
                        'month_year': f"{month_name} {p.year}",
                        'basic_salary': float(p.basic_salary or 0),
                        'total_allowances': float(
                            p.total_allowances or 0
                        ),
                        'total_deductions': float(
                            p.total_deductions or 0
                        ),
                        'loan_deduction': float(p.loan_deduction or 0),
                        'net_salary': float(p.net_salary or 0),
                        'payment_status': p.payment_status or '',
                        'payment_date_str': (
                            p.payment_date.strftime("%Y/%m/%d")
                            if p.payment_date else ''
                        ),
                    })

                return {
                    'employee': employee_info,
                    'loans': loans_data,
                    'loans_summary': {
                        'total_loans': float(total_loans),
                        'total_paid': float(total_paid),
                        'total_remaining': float(total_remaining),
                        'active_count': active_count,
                    },
                    'allowances': allowances_data,
                    'payroll': payroll_data,
                }

        def _ok(data):
            try:
                if not data:
                    QMessageBox.critical(self, "خطأ", "الموظف غير موجود")
                    return
                self._display_statement(data)
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(self, "خطأ", f"فشل: {m}")

        run_async(_fetch, on_result=_ok, on_error=_err)

    def _display_statement(self, data: Dict):
        self.info_card.setVisible(True)
        self.loans_summary_card.setVisible(True)
        self.loans_card.setVisible(True)
        self.allowances_card.setVisible(True)
        self.payroll_card.setVisible(True)

        self._display_employee_info(data['employee'])
        self._display_loans(data['loans'])
        self._display_loans_summary(data['loans_summary'])
        self._display_allowances(data['allowances'])
        self._display_payroll(data['payroll'])

    def _display_employee_info(self, employee: Dict):
        self.employee_name_label.setText(employee['full_name'])
        self.employee_job_label.setText(f"المسمى: {employee['job_title']}")
        self.employee_phone_label.setText(
            f"الهاتف: {employee['primary_phone']}"
        )

        status_colors = {
            'نشط': '#10B981',
            'إجازة': '#F59E0B',
            'مستقيل': '#EF4444',
        }
        status = employee['status']
        self.employee_status_label.setText(f"الحالة: {status}")
        self.employee_status_label.setStyleSheet(
            f"color: {status_colors.get(status, '#64748B')}; "
            "font-size: 12px; font-weight: 600;"
        )

        self.basic_salary_label.setText(
            f"الراتب الأساسي: {employee['basic_salary']:,.2f} ر.ي"
        )

    def _display_loans_summary(self, summary: Dict):
        self.total_loans_label.setText(f"{summary['total_loans']:,.2f}")
        self.total_loans_paid_label.setText(f"{summary['total_paid']:,.2f}")
        self.total_loans_remaining_label.setText(
            f"{summary['total_remaining']:,.2f}"
        )
        self.active_loans_count_label.setText(
            str(summary['active_count'])
        )

    def _display_loans(self, loans: List[Dict]):
        self.loans_table.setRowCount(len(loans))
        for row, loan in enumerate(loans):
            self.loans_table.setItem(
                row, 0, QTableWidgetItem(loan['date_str'])
            )
            self.loans_table.setItem(
                row, 1,
                QTableWidgetItem(f"{loan['total_amount']:,.2f}")
            )
            self.loans_table.setItem(
                row, 2,
                QTableWidgetItem(f"{loan['monthly_deduction']:,.2f}")
            )

            paid_item = QTableWidgetItem(f"{loan['paid_amount']:,.2f}")
            paid_item.setForeground(QColor('#10B981'))
            self.loans_table.setItem(row, 3, paid_item)

            rem_item = QTableWidgetItem(f"{loan['remaining']:,.2f}")
            rem_item.setForeground(
                QColor('#EF4444') if loan['remaining'] > 0
                else QColor('#10B981')
            )
            self.loans_table.setItem(row, 4, rem_item)

            status_item = QTableWidgetItem(loan['status'])
            status_item.setForeground(
                QColor('#F59E0B') if loan['status'] == 'مستمرة'
                else QColor('#10B981')
            )
            self.loans_table.setItem(row, 5, status_item)
            self.loans_table.setItem(
                row, 6, QTableWidgetItem(loan['reason'])
            )

            pct_item = QTableWidgetItem(f"{loan['percentage']:.1f}%")
            if loan['percentage'] >= 100:
                pct_item.setForeground(QColor('#10B981'))
            elif loan['percentage'] >= 50:
                pct_item.setForeground(QColor('#F59E0B'))
            else:
                pct_item.setForeground(QColor('#EF4444'))
            self.loans_table.setItem(row, 7, pct_item)

            self.loans_table.setRowHeight(row, 40)

        h = self.loans_table.horizontalHeader().height()
        self.loans_table.setMinimumHeight(h + len(loans) * 40 + 5)

    def _display_allowances(self, records: List[Dict]):
        self.allowances_table.setRowCount(len(records))
        type_colors = {
            'بدل': '#10B981', 'حافز': '#1976D3', 'مكافأة': '#06B6D4',
            'خصم': '#EF4444', 'غياب': '#F59E0B',
        }
        for row, r in enumerate(records):
            self.allowances_table.setItem(
                row, 0, QTableWidgetItem(r['date_str'])
            )
            type_item = QTableWidgetItem(r['type'])
            type_item.setForeground(QColor(
                type_colors.get(r['type'], '#64748B')
            ))
            self.allowances_table.setItem(row, 1, type_item)

            amount_item = QTableWidgetItem(f"{r['amount']:,.2f}")
            amount_item.setForeground(
                QColor('#10B981') if r['is_allowance']
                else QColor('#EF4444')
            )
            self.allowances_table.setItem(row, 2, amount_item)
            self.allowances_table.setItem(
                row, 3, QTableWidgetItem(r['reason'])
            )
            dir_item = QTableWidgetItem(
                "بدل" if r['is_allowance'] else "خصم"
            )
            dir_item.setForeground(
                QColor('#10B981') if r['is_allowance']
                else QColor('#EF4444')
            )
            self.allowances_table.setItem(row, 4, dir_item)
            self.allowances_table.setRowHeight(row, 40)

        h = self.allowances_table.horizontalHeader().height()
        self.allowances_table.setMinimumHeight(h + len(records) * 40 + 5)

    def _display_payroll(self, payrolls: List[Dict]):
        self.payroll_table.setRowCount(len(payrolls))
        for row, p in enumerate(payrolls):
            self.payroll_table.setItem(
                row, 0, QTableWidgetItem(p['month_year'])
            )
            self.payroll_table.setItem(
                row, 1, QTableWidgetItem(f"{p['basic_salary']:,.2f}")
            )
            self.payroll_table.setItem(
                row, 2,
                QTableWidgetItem(f"{p['total_allowances']:,.2f}")
            )
            self.payroll_table.setItem(
                row, 3,
                QTableWidgetItem(f"{p['total_deductions']:,.2f}")
            )
            loan_item = QTableWidgetItem(f"{p['loan_deduction']:,.2f}")
            loan_item.setForeground(QColor('#EF4444'))
            self.payroll_table.setItem(row, 4, loan_item)

            net_item = QTableWidgetItem(f"{p['net_salary']:,.2f}")
            net_item.setForeground(QColor('#10B981'))
            net_item.setFont(QFont("Cairo", 10, QFont.Weight.Bold))
            self.payroll_table.setItem(row, 5, net_item)

            status_item = QTableWidgetItem(p['payment_status'])
            status_item.setForeground(
                QColor('#10B981') if p['payment_status'] == 'مسلم'
                else QColor('#F59E0B')
            )
            self.payroll_table.setItem(row, 6, status_item)
            self.payroll_table.setItem(
                row, 7, QTableWidgetItem(p['payment_date_str'])
            )
            self.payroll_table.setRowHeight(row, 40)

        h = self.payroll_table.horizontalHeader().height()
        self.payroll_table.setMinimumHeight(h + len(payrolls) * 40 + 5)

    def print_statement(self):
        if self.permission_service \
           and not self.permission_service.can_print("كشف حساب موظف"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        if not self.selected_employee_id:
            QMessageBox.warning(self, "تنبيه", "اختر موظفاً")
            return
        QMessageBox.information(
            self, "طباعة", "سيتم تنفيذها في مرحلة التقارير"
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())

    def refresh(self):
        self.info_card.setVisible(False)
        self.loans_summary_card.setVisible(False)
        self.loans_card.setVisible(False)
        self.allowances_card.setVisible(False)
        self.payroll_card.setVisible(False)
        self.selected_employee_id = None
        self.selected_employee_data = {}
        self.print_btn.setEnabled(False)
        self.search_employees()