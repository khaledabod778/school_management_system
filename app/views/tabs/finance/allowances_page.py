"""
واجهة البدلات والخصومات.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Optional, List, Dict
import qtawesome as qta
from datetime import date
from decimal import Decimal

from app.database.session import session_scope
from app.database.models import Employee, EmployeeAllowanceDeduction
from app.services.finance_extras_factory import FinanceExtrasFactory
from app.services.hr_users_factory import HrUsersFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    PageHeader, Card, QDateEditEN, QDoubleSpinBoxEN,
    QLineEditPlus, SearchBox, ModernTable, GradientButton, IconButton,
)
from app.views.widgets.dialogs import (
    ConfirmationDialog, SuccessDialog, ErrorDialog, ModernDialog,
)
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class AllowancesPage(QWidget):
    """صفحة البدلات والخصومات."""

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

        self.all_records: List[Dict] = []
        self.current_filtered_records: List[Dict] = []

        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self.filter_records)

        self.setup_ui()
        self.loading_overlay = LoadingOverlay(self)
        QTimer.singleShot(100, self.load_data)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)

        title = QLabel("البدلات والخصومات")
        title.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #0F172A;"
        )
        main_layout.addWidget(title)

        subtitle = QLabel("إدارة بدلات وخصومات الموظفين")
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

        self.search_box = SearchBox("بحث عن موظف...")
        self.search_box.textChanged.connect(self._on_search_text_changed)
        filter_layout.addWidget(self.search_box)

        filter_layout.addWidget(QLabel("النوع:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems([
            "جميع الأنواع", "بدل", "حافز", "مكافأة", "خصم", "غياب",
        ])
        self.type_filter.currentIndexChanged.connect(self.filter_records)
        filter_layout.addWidget(self.type_filter)

        filter_layout.addWidget(QLabel("من:"))
        self.date_from = QDateEditEN(QDate.currentDate().addMonths(-1))
        self.date_from.dateChanged.connect(self.filter_records)
        filter_layout.addWidget(self.date_from)

        filter_layout.addWidget(QLabel("إلى:"))
        self.date_to = QDateEditEN()
        self.date_to.dateChanged.connect(self.filter_records)
        filter_layout.addWidget(self.date_to)

        filter_layout.addStretch()

        add_btn = GradientButton("إضافة", "fa5s.plus")
        add_btn.clicked.connect(self.add_allowance)
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
        self.count_label = QLabel("إجمالي السجلات: 0")
        self.count_label.setObjectName("count_label")
        toolbar.addWidget(self.count_label)
        toolbar.addStretch()

        edit_btn = IconButton('fa5s.edit', "تعديل", color='#1976D3')
        edit_btn.clicked.connect(self.edit_record)
        toolbar.addWidget(edit_btn)

        delete_btn = IconButton('fa5s.trash', "حذف", color='#EF4444')
        delete_btn.clicked.connect(self.delete_record)
        toolbar.addWidget(delete_btn)

        print_btn = IconButton('fa5s.print', "طباعة", color='#10B981')
        print_btn.clicked.connect(self.print_record)
        toolbar.addWidget(print_btn)

        card_layout.addLayout(toolbar)

        self.table = ModernTable()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "الموظف", "النوع", "المبلغ", "التاريخ", "السبب",
        ])
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 100)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.edit_record)
        card_layout.addWidget(self.table)

        main_layout.addWidget(table_card)

    def _create_widget(self, layout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    # ============================================================
    # LOAD DATA
    # ============================================================

    def load_data(self):
        self.loading_overlay.show_loading("جاري التحميل...")

        year_start = self.year_start
        year_end = self.year_end
        ayid = self.academic_year_id

        def _fetch():
            if FinanceExtrasFactory.is_remote():
                return FinanceExtrasFactory.get_service() \
                    .list_allowances(ayid)

            if not year_start:
                year_start_local = date.today().replace(month=1, day=1)
            else:
                year_start_local = year_start

            if not year_end:
                year_end_local = date.today().replace(month=12, day=31)
            else:
                year_end_local = year_end

            with session_scope() as session:
                records_q = session.execute(
                    select(EmployeeAllowanceDeduction)
                    .options(joinedload(
                        EmployeeAllowanceDeduction.employee
                    ))
                    .where(
                        EmployeeAllowanceDeduction.date >= year_start_local,
                        EmployeeAllowanceDeduction.date <= year_end_local,
                    )
                    .order_by(EmployeeAllowanceDeduction.date.desc())
                ).unique().scalars().all()

                return [
                    {
                        'id': r.id,
                        'employee_id': r.employee_id,
                        'employee_name': (
                            r.employee.full_name if r.employee else ''
                        ),
                        'type': r.type or '',
                        'amount': float(r.amount or 0),
                        'date': r.date,
                        'date_str': (
                            r.date.strftime("%Y/%m/%d")
                            if r.date else ''
                        ),
                        'reason': r.reason or '',
                        'is_allowance': r.type in [
                            'بدل', 'حافز', 'مكافأة',
                        ],
                    }
                    for r in records_q
                ]

        def _ok(data):
            try:
                self.all_records = data or []
                self.current_filtered_records = list(self.all_records)
                self.display_records(self.all_records)
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            print(f"فشل: {m}")
            self.all_records = []
            self.current_filtered_records = []
            self.display_records([])

        run_async(_fetch, on_result=_ok, on_error=_err)

    # ============================================================
    # DISPLAY
    # ============================================================

    def display_records(self, records: List[Dict]):
        self.table.setRowCount(len(records))

        for row, record in enumerate(records):
            self.table.setItem(
                row, 0, QTableWidgetItem(record['employee_name'])
            )

            type_item = QTableWidgetItem(record['type'])
            if record['is_allowance']:
                type_item.setForeground(QColor('#10B981'))
            else:
                type_item.setForeground(QColor('#EF4444'))
            self.table.setItem(row, 1, type_item)

            amount_item = QTableWidgetItem(f"{record['amount']:,.2f}")
            amount_item.setForeground(
                QColor('#10B981') if record['is_allowance']
                else QColor('#EF4444')
            )
            self.table.setItem(row, 2, amount_item)

            self.table.setItem(
                row, 3, QTableWidgetItem(record['date_str'])
            )
            self.table.setItem(
                row, 4, QTableWidgetItem(record['reason'])
            )

            self.table.setRowHeight(row, 35)

        self.count_label.setText(f"إجمالي السجلات: {len(records)}")

    # ============================================================
    # FILTER
    # ============================================================

    def _on_search_text_changed(self):
        self._search_timer.stop()
        self._search_timer.start()

    def filter_records(self):
        search_text = self.search_box.text().lower().strip()
        type_filter = self.type_filter.currentText()
        date_from = self.date_from.date().toPython()
        date_to = self.date_to.date().toPython()

        filtered = []
        for record in self.all_records:
            if search_text and search_text not in \
               record['employee_name'].lower():
                continue

            if type_filter != "جميع الأنواع" \
               and record['type'] != type_filter:
                continue

            record_date = record['date']
            if isinstance(record_date, str):
                try:
                    record_date = date.fromisoformat(record_date)
                except Exception:
                    record_date = date.today()

            if record_date < date_from or record_date > date_to:
                continue

            filtered.append(record)

        self.current_filtered_records = filtered
        self.display_records(filtered)

    # ============================================================
    # HELPERS
    # ============================================================

    def _get_selected_record_id(self) -> Optional[int]:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.current_filtered_records):
            return None
        return self.current_filtered_records[row]['id']

    # ============================================================
    # CRUD
    # ============================================================

    def add_allowance(self):
        if self.permission_service \
           and not self.permission_service.can_add("البدلات والخصومات"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        dlg = AllowanceDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            SuccessDialog("نجاح", "تم الإضافة", self).exec()

    def edit_record(self):
        if self.permission_service \
           and not self.permission_service.can_edit("البدلات والخصومات"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        rid = self._get_selected_record_id()
        if not rid:
            ErrorDialog("تنبيه", "يرجى اختيار سجل", self).exec()
            return

        def _fetch():
            if FinanceExtrasFactory.is_remote():
                data = FinanceExtrasFactory.get_service() \
                    .get_allowance(rid)
                if data and data.get('date') \
                   and isinstance(data['date'], str):
                    try:
                        data['date'] = date.fromisoformat(data['date'])
                    except Exception:
                        pass
                return data
            with session_scope() as session:
                r = session.get(EmployeeAllowanceDeduction, rid)
                if not r:
                    return None
                return {
                    'id': r.id,
                    'employee_id': r.employee_id,
                    'type': r.type or '',
                    'amount': float(r.amount or 0),
                    'date': r.date,
                    'reason': r.reason or '',
                }

        def _ok(data):
            if not data:
                ErrorDialog("خطأ", "السجل غير موجود", self).exec()
                return
            dlg = AllowanceDialog(record_data=data, parent=self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self.load_data()
                SuccessDialog("نجاح", "تم التحديث", self).exec()

        def _err(m):
            ErrorDialog("خطأ", str(m), self).exec()

        run_async(_fetch, on_result=_ok, on_error=_err)

    def delete_record(self):
        if self.permission_service \
           and not self.permission_service.can_delete("البدلات والخصومات"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        rid = self._get_selected_record_id()
        if not rid:
            ErrorDialog("تنبيه", "اختر سجلاً", self).exec()
            return

        rec = next(
            (r for r in self.current_filtered_records if r['id'] == rid),
            None,
        )
        if not rec:
            return

        if ConfirmationDialog(
            "حذف سجل",
            f"حذف {rec['type']} للموظف {rec['employee_name']}؟",
            self,
        ).exec() != QDialog.DialogCode.Accepted:
            return

        def _do():
            if FinanceExtrasFactory.is_remote():
                FinanceExtrasFactory.get_service().delete_allowance(rid)
            else:
                with session_scope() as session:
                    obj = session.get(EmployeeAllowanceDeduction, rid)
                    if obj:
                        session.delete(obj)
                        session.commit()

        def _ok(_):
            SuccessDialog("نجاح", "تم الحذف", self).exec()
            self.load_data()

        def _err(m):
            ErrorDialog("خطأ", str(m), self).exec()

        run_async(_do, on_result=_ok, on_error=_err)

    def print_record(self):
        if self.permission_service \
           and not self.permission_service.can_print("البدلات والخصومات"):
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

class AllowanceDialog(ModernDialog):
    """نافذة إضافة/تعديل بدل أو خصم."""

    def __init__(self, record_data: Optional[dict] = None, parent=None):
        super().__init__(
            "تعديل سجل" if record_data else "إضافة بدل/خصم",
            "fa5s.coins", parent, width=450, height=600,
        )

        self.record_data = record_data
        self.record_id = record_data['id'] if record_data else None
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

        self.add_widget(self._create_label("النوع:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "بدل", "حافز", "مكافأة", "خصم", "غياب",
        ])
        self.add_widget(self.type_combo)

        self.add_widget(self._create_label("المبلغ:"))
        self.amount_input = QDoubleSpinBoxEN()
        self.add_widget(self.amount_input)

        self.add_widget(self._create_label("السبب:"))
        self.reason_input = QTextEdit()
        self.reason_input.setMaximumHeight(60)
        self.add_widget(self.reason_input)

        self.add_widget(self._create_label("التاريخ:"))
        self.date_input = QDateEditEN()
        self.add_widget(self.date_input)

        self.add_button("إلغاء", self.reject, "default")
        self.add_button("حفظ", self.save_record, "primary")

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
        if self.record_data:
            self.type_combo.setCurrentText(self.record_data['type'])
            self.amount_input.setValue(self.record_data['amount'])
            self.reason_input.setText(self.record_data['reason'])

            d = self.record_data['date']
            if d:
                if isinstance(d, str):
                    try:
                        d = date.fromisoformat(d)
                    except Exception:
                        d = None
                if d:
                    self.date_input.setDate(QDate(d.year, d.month, d.day))

            self.selected_employee_id = self.record_data['employee_id']
            self._load_employee_info(self.record_data['employee_id'])
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

    def save_record(self):
        if not self.selected_employee_id:
            ErrorDialog("تنبيه", "اختر موظفاً", self).exec()
            return
        if self.amount_input.value() <= 0:
            ErrorDialog("تنبيه", "أدخل مبلغاً صحيحاً", self).exec()
            return

        d = self.date_input.date()
        date_iso = date(d.year(), d.month(), d.day()).isoformat()

        payload = {
            'employee_id': self.selected_employee_id,
            'type': self.type_combo.currentText(),
            'amount': float(self.amount_input.value()),
            'reason': self.reason_input.toPlainText().strip() or None,
            'date': date_iso,
        }

        try:
            if FinanceExtrasFactory.is_remote():
                service = FinanceExtrasFactory.get_service()
                if self.record_id:
                    service.update_allowance(self.record_id, payload)
                else:
                    service.create_allowance(payload)
            else:
                self._save_local(payload)
            self.accept()
        except Exception as e:
            ErrorDialog("خطأ", str(e), self).exec()

    def _save_local(self, payload):
        with session_scope() as session:
            if self.record_id:
                r = session.get(
                    EmployeeAllowanceDeduction, self.record_id
                )
            else:
                r = EmployeeAllowanceDeduction()
                session.add(r)

            r.employee_id = payload['employee_id']
            r.type = payload['type']
            r.amount = Decimal(str(payload['amount']))
            r.reason = payload['reason']
            r.date = date.fromisoformat(payload['date'])
            session.commit()