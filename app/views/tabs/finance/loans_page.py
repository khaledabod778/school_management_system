"""
واجهة السلف المالية للموظفين.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Optional, List, Dict
import qtawesome as qta
from datetime import date
from decimal import Decimal

from app.database.session import session_scope
from app.database.models import Employee, EmployeeLoan
from app.services.finance_extras_factory import FinanceExtrasFactory
from app.services.hr_users_factory import HrUsersFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    KPICard, PageHeader, Card, QDateEditEN, QDoubleSpinBoxEN,
    QLineEditPlus, SearchBox, ModernTable, Badge,
    GradientButton, IconButton,
)
from app.views.widgets.dialogs import (
    ConfirmationDialog, SuccessDialog, ErrorDialog, ModernDialog,
)
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class LoansPage(QWidget):
    """صفحة السلف المالية."""

    def __init__(self, user, academic_year,
                 permission_service: Optional[PermissionService] = None,
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        self.academic_year_id = academic_year.id if academic_year else None
        self.year_start = academic_year.start_date if academic_year else None
        self.year_end = academic_year.end_date if academic_year else None

        self.all_loans: List[Dict] = []
        self.current_filtered_loans: List[Dict] = []

        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self.filter_loans)

        self.active_value_label = None
        self.total_value_label = None
        self.monthly_value_label = None
        self.completed_value_label = None

        self.setup_ui()
        self.loading_overlay = LoadingOverlay(self)
        QTimer.singleShot(100, self.load_data)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)

        title = QLabel("السلف المالية للموظفين")
        title.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #0F172A;"
        )
        main_layout.addWidget(title)

        subtitle = QLabel("إدارة سلف الموظفين والخصومات الشهرية")
        subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(subtitle)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        self.active_loans_card = KPICard(
            "السلف النشطة", "0", "fa5s.hand-holding-usd", "#1976D3"
        )
        stats_layout.addWidget(self.active_loans_card)

        self.total_amount_card = KPICard(
            "إجمالي السلف", "0 ر.ي", "fa5s.coins", "#F59E0B"
        )
        stats_layout.addWidget(self.total_amount_card)

        self.monthly_deduction_card = KPICard(
            "الخصم الشهري", "0 ر.ي", "fa5s.calendar-minus", "#10B981"
        )
        stats_layout.addWidget(self.monthly_deduction_card)

        self.completed_loans_card = KPICard(
            "سلف منتهية", "0", "fa5s.check-circle", "#10B981"
        )
        stats_layout.addWidget(self.completed_loans_card)

        main_layout.addWidget(self._create_widget(stats_layout))
        self._find_kpi_value_labels()

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

        self.search_box = SearchBox("بحث عن موظف...")
        self.search_box.textChanged.connect(self._on_search_text_changed)
        filter_layout.addWidget(self.search_box)

        filter_layout.addWidget(QLabel("الحالة:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["جميع الحالات", "مستمرة", "منتهية"])
        self.status_filter.currentIndexChanged.connect(self.filter_loans)
        filter_layout.addWidget(self.status_filter)

        filter_layout.addWidget(QLabel("من:"))
        self.date_from = QDateEditEN(QDate.currentDate().addMonths(-1))
        self.date_from.dateChanged.connect(self.filter_loans)
        filter_layout.addWidget(self.date_from)

        filter_layout.addWidget(QLabel("إلى:"))
        self.date_to = QDateEditEN()
        self.date_to.dateChanged.connect(self.filter_loans)
        filter_layout.addWidget(self.date_to)

        filter_layout.addStretch()

        add_btn = GradientButton("إضافة سلفة", "fa5s.plus")
        add_btn.clicked.connect(self.add_loan)
        filter_layout.addWidget(add_btn)

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
        self.count_label = QLabel("إجمالي السلف: 0")
        self.count_label.setObjectName("count_label")
        toolbar.addWidget(self.count_label)
        toolbar.addStretch()

        edit_btn = IconButton('fa5s.edit', "تعديل", color='#1976D3')
        edit_btn.clicked.connect(self.edit_loan)
        toolbar.addWidget(edit_btn)

        delete_btn = IconButton('fa5s.trash', "حذف", color='#EF4444')
        delete_btn.clicked.connect(self.delete_loan)
        toolbar.addWidget(delete_btn)

        print_btn = IconButton('fa5s.print', "طباعة", color='#10B981')
        print_btn.clicked.connect(self.print_loan)
        toolbar.addWidget(print_btn)

        card_layout.addLayout(toolbar)

        self.table = ModernTable()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "الموظف", "المبلغ الكلي", "القسط الشهري", "الحالة",
            "تاريخ السلفة", "السبب", "المتبقي",
        ])
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 150)
        self.table.setColumnWidth(6, 100)
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

    def _create_widget(self, layout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def _find_kpi_value_labels(self):
        try:
            cards = [
                (self.active_loans_card, 'active'),
                (self.total_amount_card, 'total'),
                (self.monthly_deduction_card, 'monthly'),
                (self.completed_loans_card, 'completed'),
            ]
            for card, key in cards:
                labels = card.findChildren(QLabel)
                value_label = None
                for lbl in labels:
                    if lbl.text() in ("0", "0 ر.ي"):
                        value_label = lbl
                        break
                if key == 'active':
                    self.active_value_label = value_label
                elif key == 'total':
                    self.total_value_label = value_label
                elif key == 'monthly':
                    self.monthly_value_label = value_label
                elif key == 'completed':
                    self.completed_value_label = value_label
        except Exception as e:
            print(f"خطأ: {e}")

    # ============================================================
    # LOAD
    # ============================================================

    def load_data(self):
        self.loading_overlay.show_loading("جاري التحميل...")

        year_start = self.year_start
        year_end = self.year_end
        ayid = self.academic_year_id

        def _fetch():
            if FinanceExtrasFactory.is_remote():
                return FinanceExtrasFactory.get_service().list_loans(ayid)

            # Local - same output format
            if not year_start:
                ys = date.today().replace(month=1, day=1)
            else:
                ys = year_start
            if not year_end:
                ye = date.today().replace(month=12, day=31)
            else:
                ye = year_end

            with session_scope() as session:
                loans_q = session.execute(
                    select(EmployeeLoan)
                    .options(joinedload(EmployeeLoan.employee))
                    .where(
                        EmployeeLoan.loan_date >= ys,
                        EmployeeLoan.loan_date <= ye,
                    )
                    .order_by(EmployeeLoan.loan_date.desc())
                ).unique().scalars().all()

                loans_data = []
                active = 0
                completed = 0
                total_amt = 0.0
                monthly = 0.0

                for l in loans_q:
                    total_loan = float(l.total_loan_amount or 0)
                    monthly_ded = float(l.monthly_deduction or 0)
                    remaining = float(
                        getattr(l, 'remaining_amount', None) or 0
                    )

                    loans_data.append({
                        'id': l.id,
                        'employee_id': l.employee_id,
                        'employee_name': (
                            l.employee.full_name if l.employee else ''
                        ),
                        'total_loan_amount': total_loan,
                        'monthly_deduction': monthly_ded,
                        'remaining_amount': remaining,
                        'status': l.status or '',
                        'loan_date': (
                            l.loan_date.isoformat()
                            if l.loan_date else None
                        ),
                        'loan_date_str': (
                            l.loan_date.strftime("%Y/%m/%d")
                            if l.loan_date else ''
                        ),
                        'reason': l.reason or '',
                    })

                    if l.status == 'مستمرة':
                        active += 1
                        monthly += monthly_ded
                    elif l.status == 'منتهية':
                        completed += 1

                    total_amt += total_loan

                return {
                    'loans': loans_data,
                    'stats': {
                        'active': active,
                        'completed': completed,
                        'total_amount': total_amt,
                        'monthly_deduction': monthly,
                    },
                }

        def _ok(data):
            try:
                self.all_loans = data.get('loans', [])
                self.current_filtered_loans = list(self.all_loans)
                self._update_stats_display(data.get('stats', {}))
                self.display_loans(self.all_loans)
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            print(f"فشل: {m}")
            self.all_loans = []
            self.current_filtered_loans = []
            self.display_loans([])

        run_async(_fetch, on_result=_ok, on_error=_err)

    # ============================================================
    # DISPLAY
    # ============================================================

    def display_loans(self, loans: List[Dict]):
        self.table.setRowCount(len(loans))

        for row, loan in enumerate(loans):
            self.table.setItem(
                row, 0, QTableWidgetItem(loan['employee_name'])
            )
            self.table.setItem(
                row, 1,
                QTableWidgetItem(f"{loan['total_loan_amount']:,.2f}")
            )
            self.table.setItem(
                row, 2,
                QTableWidgetItem(f"{loan['monthly_deduction']:,.2f}")
            )

            status_item = QTableWidgetItem(loan['status'])
            if loan['status'] == 'مستمرة':
                status_item.setForeground(QColor('#F59E0B'))
            else:
                status_item.setForeground(QColor('#10B981'))
            self.table.setItem(row, 3, status_item)

            self.table.setItem(
                row, 4, QTableWidgetItem(loan['loan_date_str'])
            )
            self.table.setItem(
                row, 5, QTableWidgetItem(loan['reason'])
            )

            remaining_item = QTableWidgetItem(
                f"{loan['remaining_amount']:,.2f}"
            )
            remaining_item.setForeground(QColor('#EF4444'))
            self.table.setItem(row, 6, remaining_item)

            self.table.setRowHeight(row, 35)

        self.count_label.setText(f"إجمالي السلف: {len(loans)}")

    def _update_stats_display(self, stats: Dict):
        try:
            if self.active_value_label:
                self.active_value_label.setText(str(stats.get('active', 0)))
            if self.total_value_label:
                self.total_value_label.setText(
                    f"{stats.get('total_amount', 0):,.0f} ر.ي"
                )
            if self.monthly_value_label:
                self.monthly_value_label.setText(
                    f"{stats.get('monthly_deduction', 0):,.0f} ر.ي"
                )
            if self.completed_value_label:
                self.completed_value_label.setText(
                    str(stats.get('completed', 0))
                )
        except Exception as e:
            print(f"خطأ: {e}")

    # ============================================================
    # FILTER
    # ============================================================

    def _on_search_text_changed(self):
        self._search_timer.stop()
        self._search_timer.start()

    def filter_loans(self):
        search_text = self.search_box.text().lower().strip()
        status = self.status_filter.currentText()
        date_from = self.date_from.date().toPython()
        date_to = self.date_to.date().toPython()

        filtered = []
        for loan in self.all_loans:
            if search_text and search_text not in \
               loan['employee_name'].lower():
                continue
            if status != "جميع الحالات" and loan['status'] != status:
                continue

            loan_date = loan.get('loan_date')
            if isinstance(loan_date, str):
                try:
                    loan_date = date.fromisoformat(loan_date)
                except Exception:
                    loan_date = date.today()
            elif loan_date is None:
                loan_date = date.today()

            if loan_date < date_from or loan_date > date_to:
                continue

            filtered.append(loan)

        self.current_filtered_loans = filtered
        self.display_loans(filtered)

    # ============================================================
    # HELPERS
    # ============================================================

    def _get_selected_loan_id(self) -> Optional[int]:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.current_filtered_loans):
            return None
        return self.current_filtered_loans[row]['id']

    # ============================================================
    # CRUD
    # ============================================================

    def add_loan(self):
        if self.permission_service \
           and not self.permission_service.can_add("السلف المالية"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        dlg = LoanDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            SuccessDialog("نجاح", "تم الإضافة", self).exec()

    def edit_loan(self):
        if self.permission_service \
           and not self.permission_service.can_edit("السلف المالية"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        lid = self._get_selected_loan_id()
        if not lid:
            ErrorDialog("تنبيه", "اختر سلفة", self).exec()
            return

        def _fetch():
            if FinanceExtrasFactory.is_remote():
                data = FinanceExtrasFactory.get_service().get_loan(lid)
                if data and isinstance(data.get('loan_date'), str):
                    try:
                        data['loan_date'] = date.fromisoformat(
                            data['loan_date']
                        )
                    except Exception:
                        pass
                return data
            with session_scope() as session:
                l = session.get(EmployeeLoan, lid)
                if not l:
                    return None
                return {
                    'id': l.id,
                    'employee_id': l.employee_id,
                    'total_loan_amount': float(l.total_loan_amount or 0),
                    'monthly_deduction': float(l.monthly_deduction or 0),
                    'loan_date': l.loan_date,
                    'reason': l.reason or '',
                    'status': l.status or '',
                }

        def _ok(data):
            if not data:
                ErrorDialog("خطأ", "السلفة غير موجودة", self).exec()
                return
            dlg = LoanDialog(loan_data=data, parent=self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self.load_data()
                SuccessDialog("نجاح", "تم التحديث", self).exec()

        def _err(m):
            ErrorDialog("خطأ", str(m), self).exec()

        run_async(_fetch, on_result=_ok, on_error=_err)

    def delete_loan(self):
        if self.permission_service \
           and not self.permission_service.can_delete("السلف المالية"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        lid = self._get_selected_loan_id()
        if not lid:
            ErrorDialog("تنبيه", "اختر سلفة", self).exec()
            return

        loan = next(
            (l for l in self.current_filtered_loans if l['id'] == lid),
            None,
        )
        if not loan:
            return

        if ConfirmationDialog(
            "حذف سلفة",
            f"حذف سلفة الموظف {loan['employee_name']}؟",
            self,
        ).exec() != QDialog.DialogCode.Accepted:
            return

        def _do():
            if FinanceExtrasFactory.is_remote():
                FinanceExtrasFactory.get_service().delete_loan(lid)
            else:
                with session_scope() as session:
                    obj = session.get(EmployeeLoan, lid)
                    if obj:
                        session.delete(obj)
                        session.commit()

        def _ok(_):
            SuccessDialog("نجاح", "تم الحذف", self).exec()
            self.load_data()

        def _err(m):
            ErrorDialog("خطأ", str(m), self).exec()

        run_async(_do, on_result=_ok, on_error=_err)

    def print_loan(self):
        if self.permission_service \
           and not self.permission_service.can_print("السلف المالية"):
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


# ============================================================
# DIALOG
# ============================================================

class LoanDialog(ModernDialog):
    """نافذة إضافة/تعديل سلفة."""

    def __init__(self, loan_data: Optional[dict] = None, parent=None):
        super().__init__(
            "تعديل سلفة" if loan_data else "إضافة سلفة جديدة",
            "fa5s.hand-holding-usd", parent, width=450, height=700,
        )

        self.loan_data = loan_data
        self.loan_id = loan_data['id'] if loan_data else None
        self.employees_data: List[Dict] = []
        self.selected_employee_id: Optional[int] = None

        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self._search_employees_now)

        self.setup_form()
        QTimer.singleShot(50, self._load_initial_data)

    def setup_form(self):
        self.add_widget(self._create_label("البحث عن موظف:"))
        search_layout = QHBoxLayout()
        self.employee_search = QLineEditPlus(placeholder="ابحث بالاسم...")
        self.employee_search.textChanged.connect(
            self._on_search_text_changed
        )
        search_layout.addWidget(self.employee_search)
        self.add_widget(self._create_widget(search_layout))

        self.employees_list = QListWidget()
        self.employees_list.setMaximumHeight(100)
        self.add_widget(self.employees_list)

        self.add_widget(self._create_label("المبلغ الكلي:"))
        self.total_amount_input = QDoubleSpinBoxEN()
        self.total_amount_input.setStyleSheet("""
            QDoubleSpinBox {
                border: 2px solid #1976D3;
                border-radius: 8px;
                padding: 8px;
                font-weight: 700;
                font-size: 16px;
                color: #0D47A1;
                background: #EEF2FF;
            }
        """)
        self.add_widget(self.total_amount_input)

        self.add_widget(self._create_label("القسط الشهري:"))
        self.monthly_deduction_input = QDoubleSpinBoxEN()
        self.add_widget(self.monthly_deduction_input)

        self.add_widget(self._create_label("تاريخ السلفة:"))
        self.date_input = QDateEditEN()
        self.add_widget(self.date_input)

        self.add_widget(self._create_label("السبب:"))
        self.reason_input = QTextEdit()
        self.reason_input.setMaximumHeight(60)
        self.add_widget(self.reason_input)

        self.add_button("إلغاء", self.reject, "default")
        self.add_button("حفظ", self.save_loan, "primary")

        self.employees_list.itemClicked.connect(self.select_employee)

    def _create_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            "color: #475569; font-weight: 600; font-size: 12px;"
        )
        return label

    def _create_widget(self, layout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def _load_initial_data(self):
        if self.loan_data:
            self.total_amount_input.setValue(
                self.loan_data['total_loan_amount']
            )
            self.monthly_deduction_input.setValue(
                self.loan_data['monthly_deduction']
            )

            d = self.loan_data['loan_date']
            if d:
                if isinstance(d, str):
                    try:
                        d = date.fromisoformat(d)
                    except Exception:
                        d = None
                if d:
                    self.date_input.setDate(QDate(d.year, d.month, d.day))

            self.reason_input.setText(self.loan_data['reason'])
            self.selected_employee_id = self.loan_data['employee_id']
            self._load_employee_info(self.loan_data['employee_id'])
        else:
            self._search_employees_now()

    def _load_employee_info(self, employee_id: int):
        """تحميل اسم الموظف - Local أو Remote."""
        def _fetch():
            # ✅ Remote
            if HrUsersFactory.is_remote():
                from app.services.auth_factory import AuthFactory
                client = AuthFactory.get_api_client()
                data = client.get(f"/api/hr/employees/{employee_id}")
                return {
                    'id': data['id'],
                    'full_name': data['full_name'],
                }

            # ✅ Local
            with session_scope() as session:
                emp = session.get(Employee, employee_id)
                if not emp:
                    return None
                return {
                    'id': emp.id,
                    'full_name': emp.full_name or '',
                }

        def _ok(data):
            if data:
                self.employee_search.setText(data['full_name'])

        def _err(m):
            print(f"فشل تحميل الموظف: {m}")

        run_async(_fetch, on_result=_ok, on_error=_err)

    def _on_search_text_changed(self):
        self._search_timer.stop()
        self._search_timer.start()

    def _search_employees_now(self):
        """البحث عن الموظفين - Local أو Remote."""
        search_text = self.employee_search.text().strip()

        def _fetch():
            # ✅ Remote
            if HrUsersFactory.is_remote():
                from app.services.auth_factory import AuthFactory
                client = AuthFactory.get_api_client()
                params = {}
                if search_text:
                    params['search'] = search_text
                employees = client.get(
                    "/api/hr/employees/", params=params
                )
                return [
                    {
                        'id': e['id'],
                        'full_name': e['full_name'],
                    }
                    for e in employees[:20]
                ]

            # ✅ Local
            with session_scope() as session:
                query = select(Employee)
                if search_text:
                    query = query.where(
                        Employee.full_name.ilike(f"%{search_text}%")
                    )
                emps = session.execute(query.limit(20)).scalars().all()
                return [
                    {'id': e.id, 'full_name': e.full_name or ''}
                    for e in emps
                ]

        def _ok(data):
            self.employees_data = data
            self.employees_list.clear()
            for e in data:
                item = QListWidgetItem(e['full_name'])
                item.setData(Qt.ItemDataRole.UserRole, e['id'])
                self.employees_list.addItem(item)

        def _err(m):
            print(f"فشل البحث: {m}")

        run_async(_fetch, on_result=_ok, on_error=_err)

    def select_employee(self, item: QListWidgetItem):
        self.selected_employee_id = item.data(Qt.ItemDataRole.UserRole)

    def save_loan(self):
        if not self.selected_employee_id:
            ErrorDialog("تنبيه", "اختر موظفاً", self).exec()
            return
        if self.total_amount_input.value() <= 0:
            ErrorDialog("تنبيه", "أدخل مبلغاً صحيحاً", self).exec()
            return
        if self.monthly_deduction_input.value() <= 0:
            ErrorDialog("تنبيه", "أدخل قسطاً صحيحاً", self).exec()
            return

        d = self.date_input.date()
        date_iso = date(d.year(), d.month(), d.day()).isoformat()

        payload = {
            'employee_id': self.selected_employee_id,
            'total_loan_amount': float(self.total_amount_input.value()),
            'monthly_deduction': float(
                self.monthly_deduction_input.value()
            ),
            'loan_date': date_iso,
            'reason': self.reason_input.toPlainText().strip() or None,
        }

        try:
            if FinanceExtrasFactory.is_remote():
                service = FinanceExtrasFactory.get_service()
                if self.loan_id:
                    service.update_loan(self.loan_id, payload)
                else:
                    service.create_loan(payload)
            else:
                self._save_local(payload)
            self.accept()
        except Exception as e:
            ErrorDialog("خطأ", str(e), self).exec()

    def _save_local(self, payload):
        with session_scope() as session:
            if self.loan_id:
                l = session.get(EmployeeLoan, self.loan_id)
            else:
                l = EmployeeLoan()
                session.add(l)

            l.employee_id = payload['employee_id']
            l.total_loan_amount = Decimal(
                str(payload['total_loan_amount'])
            )
            l.monthly_deduction = Decimal(
                str(payload['monthly_deduction'])
            )
            l.loan_date = date.fromisoformat(payload['loan_date'])
            l.reason = payload['reason']
            l.status = 'مستمرة'
            if not self.loan_id:
                l.remaining_amount = Decimal(
                    str(payload['total_loan_amount'])
                )
            session.commit()