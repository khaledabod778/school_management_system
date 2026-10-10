"""
واجهة سندات الصرف والمصروفات العامة.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Dict, Optional
import qtawesome as qta
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.database.session import session_scope
from app.database.models import ExpenseVoucher, User, AcademicYear
from app.services.finance_extras_factory import FinanceExtrasFactory
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
from sqlalchemy import select, func


class ExpensesPage(QWidget):
    """صفحة سندات الصرف والمصروفات."""

    def __init__(self, user, academic_year,
                 permission_service: Optional[PermissionService] = None,
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        self.academic_year_id = academic_year.id if academic_year else None
        self.all_vouchers: List[Dict] = []
        self.filtered_vouchers: List[Dict] = []

        self.setup_ui()
        self.loading_overlay = LoadingOverlay(self)
        QTimer.singleShot(100, self.load_data)

    # ============================================================
    # UI
    # ============================================================

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)

        title = QLabel("سندات الصرف والمصروفات العامة")
        title.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #0F172A;"
        )
        main_layout.addWidget(title)

        subtitle = QLabel("إدارة المشتريات والفعاليات والأنشطة المدرسية")
        subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(subtitle)

        # KPI
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        self.today_expenses_card = KPICard(
            "مصروفات اليوم", "0 ر.ي", "fa5s.calendar-day", "#EF4444"
        )
        stats_layout.addWidget(self.today_expenses_card)

        self.month_expenses_card = KPICard(
            "مصروفات الشهر", "0 ر.ي", "fa5s.calendar-alt", "#F59E0B"
        )
        stats_layout.addWidget(self.month_expenses_card)

        self.total_expenses_card = KPICard(
            "إجمالي المصروفات", "0 ر.ي", "fa5s.chart-pie", "#1976D3"
        )
        stats_layout.addWidget(self.total_expenses_card)

        self.categories_card = KPICard(
            "فئات المصروفات", "5", "fa5s.tags", "#10B981"
        )
        stats_layout.addWidget(self.categories_card)

        main_layout.addWidget(self._create_widget(stats_layout))

        # Filters
        filter_card = QFrame()
        filter_card.setObjectName("filterCard")
        filter_layout = QHBoxLayout(filter_card)

        self.search_box = SearchBox("بحث برقم السند أو المستفيد...")
        self.search_box.textChanged.connect(self.filter_vouchers)
        filter_layout.addWidget(self.search_box)

        filter_layout.addWidget(QLabel("الفئة:"))
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "جميع الفئات", "مشتريات مواد", "صيانة وتشغيل",
            "فعاليات واحتفالات", "أنشطة مدرسية", "أخرى",
        ])
        self.category_filter.currentIndexChanged.connect(self.filter_vouchers)
        filter_layout.addWidget(self.category_filter)

        filter_layout.addWidget(QLabel("من:"))
        self.date_from = QDateEditEN(QDate.currentDate().addMonths(-1))
        self.date_from.dateChanged.connect(self.filter_vouchers)
        filter_layout.addWidget(self.date_from)

        filter_layout.addWidget(QLabel("إلى:"))
        self.date_to = QDateEditEN()
        self.date_to.dateChanged.connect(self.filter_vouchers)
        filter_layout.addWidget(self.date_to)

        filter_layout.addStretch()

        add_btn = GradientButton("إضافة سند صرف", "fa5s.plus")
        add_btn.clicked.connect(self.add_voucher)
        filter_layout.addWidget(add_btn)

        main_layout.addWidget(filter_card)

        # Table
        table_card = QFrame()
        table_card.setObjectName("tableCard")
        card_layout = QVBoxLayout(table_card)

        toolbar = QHBoxLayout()
        self.count_label = QLabel("إجمالي السندات: 0")
        self.count_label.setObjectName("count_label")
        toolbar.addWidget(self.count_label)
        toolbar.addStretch()

        edit_btn = IconButton('fa5s.edit', color='#1976D3', size=38)
        edit_btn.setToolTip("تعديل")
        edit_btn.clicked.connect(self.edit_voucher)
        toolbar.addWidget(edit_btn)

        cancel_btn = IconButton('fa5s.ban', color='#F59E0B', size=38)
        cancel_btn.setToolTip("إلغاء سند")
        cancel_btn.clicked.connect(self.cancel_voucher)
        toolbar.addWidget(cancel_btn)

        print_btn = IconButton('fa5s.print', color='#10B981', size=38)
        print_btn.setToolTip("طباعة")
        print_btn.clicked.connect(self.print_voucher)
        toolbar.addWidget(print_btn)

        card_layout.addLayout(toolbar)

        self.table = ModernTable()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "رقم السند", "المستفيد", "الفئة", "المبلغ",
            "التاريخ", "طريقة الدفع", "رقم الفاتورة", "المحاسب",
            "الحالة", "الملاحظات",
        ])
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 130)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 100)
        self.table.setColumnWidth(7, 100)
        self.table.setColumnWidth(8, 70)
        self.table.setColumnWidth(9, 150)
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

    # ============================================================
    # LOAD DATA
    # ============================================================

    def load_data(self):
        """تحميل السندات - Local أو Remote."""
        self.loading_overlay.show_loading("جاري التحميل...")

        ayid = self.academic_year_id
        year_obj = self.academic_year

        def _fetch():
            if FinanceExtrasFactory.is_remote():
                return FinanceExtrasFactory.get_service().list_expenses(ayid)

            # Local
            with session_scope() as session:
                if year_obj and year_obj.start_date:
                    year_start = datetime.combine(
                        year_obj.start_date, datetime.min.time()
                    )
                else:
                    year_start = datetime.now() - timedelta(days=365)

                if year_obj and year_obj.end_date:
                    year_end = datetime.combine(
                        year_obj.end_date, datetime.max.time()
                    )
                else:
                    year_end = datetime.now()

                vouchers = session.execute(
                    select(ExpenseVoucher)
                    .where(
                        ExpenseVoucher.payment_date >= year_start,
                        ExpenseVoucher.payment_date <= year_end,
                    )
                    .order_by(ExpenseVoucher.payment_date.desc())
                ).scalars().all()

                today = date.today()
                month_start = today.replace(day=1)
                today_start = datetime.combine(today, datetime.min.time())
                month_start_dt = datetime.combine(
                    month_start, datetime.min.time()
                )

                return {
                    'vouchers': [
                        {
                            'id': v.id,
                            'voucher_number': v.voucher_number or '',
                            'expense_category': v.expense_category or '',
                            'beneficiary_name': v.beneficiary_name or '',
                            'amount': float(v.amount or 0),
                            'payment_date_str': (
                                v.payment_date.strftime("%Y/%m/%d %H:%M")
                                if v.payment_date else ''
                            ),
                            'payment_method': v.payment_method or '',
                            'invoice_number': v.invoice_number or '',
                            'created_by': (
                                v.created_by_user.username
                                if v.created_by_user else ''
                            ),
                            'status': v.status or 'نشط',
                            'notes': v.notes or '',
                        }
                        for v in vouchers
                    ],
                    'stats': {
                        'today_total': float(session.query(
                            func.sum(ExpenseVoucher.amount)
                        ).filter(
                            ExpenseVoucher.status == 'نشط',
                            ExpenseVoucher.payment_date >= today_start,
                        ).scalar() or 0),
                        'month_total': float(session.query(
                            func.sum(ExpenseVoucher.amount)
                        ).filter(
                            ExpenseVoucher.status == 'نشط',
                            ExpenseVoucher.payment_date >= month_start_dt,
                        ).scalar() or 0),
                        'total_all': float(session.query(
                            func.sum(ExpenseVoucher.amount)
                        ).filter(
                            ExpenseVoucher.status == 'نشط'
                        ).scalar() or 0),
                    },
                }

        def _ok(data):
            try:
                self.all_vouchers = data['vouchers']
                self.filtered_vouchers = list(self.all_vouchers)
                self.display_vouchers(self.all_vouchers)
                self._update_stats_from_data(data['stats'])
            except Exception as e:
                print(f"خطأ في تحديث الواجهة: {e}")
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            print(f"فشل التحميل: {m}")
            self.all_vouchers = []
            self.filtered_vouchers = []
            self.display_vouchers([])

        run_async(_fetch, on_result=_ok, on_error=_err)

    def _update_stats_from_data(self, stats: dict):
        try:
            labels_today = self.today_expenses_card.findChildren(QLabel)
            labels_month = self.month_expenses_card.findChildren(QLabel)
            labels_total = self.total_expenses_card.findChildren(QLabel)
            if len(labels_today) >= 3:
                labels_today[2].setText(
                    f"{stats['today_total']:,.0f} ر.ي"
                )
            if len(labels_month) >= 3:
                labels_month[2].setText(
                    f"{stats['month_total']:,.0f} ر.ي"
                )
            if len(labels_total) >= 3:
                labels_total[2].setText(
                    f"{stats['total_all']:,.0f} ر.ي"
                )
        except Exception as e:
            print(f"خطأ في تحديث الإحصائيات: {e}")

    # ============================================================
    # DISPLAY
    # ============================================================

    def display_vouchers(self, vouchers: List[Dict]):
        self.table.setRowCount(len(vouchers))

        category_colors = {
            'مشتريات مواد': '#1976D3',
            'صيانة وتشغيل': '#F59E0B',
            'فعاليات واحتفالات': '#EC4899',
            'أنشطة مدرسية': '#10B981',
            'أخرى': '#64748B',
        }

        for row, v in enumerate(vouchers):
            self.table.setItem(row, 0, QTableWidgetItem(v['voucher_number']))
            self.table.setItem(
                row, 1, QTableWidgetItem(v['beneficiary_name'])
            )

            cat_item = QTableWidgetItem(v['expense_category'])
            cat_item.setForeground(QColor(
                category_colors.get(v['expense_category'], '#64748B')
            ))
            self.table.setItem(row, 2, cat_item)

            amount_item = QTableWidgetItem(f"{v['amount']:,.2f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            amount_item.setForeground(QColor('#EF4444'))
            amount_item.setFont(QFont("Cairo", 10, QFont.Weight.Bold))
            self.table.setItem(row, 3, amount_item)

            self.table.setItem(
                row, 4, QTableWidgetItem(v['payment_date_str'])
            )
            self.table.setItem(
                row, 5, QTableWidgetItem(v['payment_method'])
            )
            self.table.setItem(
                row, 6, QTableWidgetItem(v.get('invoice_number', ''))
            )
            self.table.setItem(
                row, 7, QTableWidgetItem(v.get('created_by', ''))
            )

            status_item = QTableWidgetItem(v['status'])
            status_item.setForeground(
                QColor('#10B981') if v['status'] == 'نشط'
                else QColor('#EF4444')
            )
            self.table.setItem(row, 8, status_item)
            self.table.setItem(
                row, 9, QTableWidgetItem(v.get('notes', ''))
            )

            self.table.setRowHeight(row, 35)

        self.count_label.setText(f"إجمالي السندات: {len(vouchers)}")

    # ============================================================
    # FILTER
    # ============================================================

    def filter_vouchers(self):
        search = self.search_box.text().lower()
        category = self.category_filter.currentText()
        date_from = self.date_from.date().toPython()
        date_to = self.date_to.date().toPython()

        filtered = []
        for v in self.all_vouchers:
            if search and (
                search not in v['voucher_number'].lower()
                and search not in v['beneficiary_name'].lower()
            ):
                continue

            if category != "جميع الفئات" \
               and v['expense_category'] != category:
                continue

            pdate_str = (v['payment_date_str'] or '').split(' ')[0]
            pdate_str = pdate_str.replace('/', '-')
            try:
                vdate = date.fromisoformat(pdate_str)
            except Exception:
                vdate = date.today()

            if vdate < date_from or vdate > date_to:
                continue

            filtered.append(v)

        self.filtered_vouchers = filtered
        self.display_vouchers(filtered)

    # ============================================================
    # CRUD
    # ============================================================

    def add_voucher(self):
        if self.permission_service \
           and not self.permission_service.can_add("سندات الصرف"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        dialog = ExpenseVoucherDialog(self.user, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            SuccessDialog("نجاح", "تم إضافة السند", self).exec()

    def edit_voucher(self):
        if self.permission_service \
           and not self.permission_service.can_edit("سندات الصرف"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        row = self.table.currentRow()
        if row < 0 or row >= len(self.filtered_vouchers):
            ErrorDialog("تنبيه", "يرجى اختيار سند", self).exec()
            return

        vid = self.filtered_vouchers[row]['id']

        def _fetch():
            if FinanceExtrasFactory.is_remote():
                return FinanceExtrasFactory.get_service().get_expense(vid)
            # Local
            with session_scope() as session:
                v = session.get(ExpenseVoucher, vid)
                if not v:
                    return None
                return {
                    'id': v.id,
                    'voucher_number': v.voucher_number or '',
                    'expense_category': v.expense_category or '',
                    'beneficiary_name': v.beneficiary_name or '',
                    'amount': float(v.amount or 0),
                    'payment_method': v.payment_method or 'نقداً',
                    'invoice_number': v.invoice_number or '',
                    'notes': v.notes or '',
                    'status': v.status or 'نشط',
                }

        def _ok(data):
            if not data:
                ErrorDialog("خطأ", "السند غير موجود", self).exec()
                return
            dialog = ExpenseVoucherDialog(
                self.user, voucher_data=data, parent=self
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_data()
                SuccessDialog("نجاح", "تم التحديث", self).exec()

        def _err(m):
            ErrorDialog("خطأ", str(m), self).exec()

        run_async(_fetch, on_result=_ok, on_error=_err)

    def cancel_voucher(self):
        if self.permission_service \
           and not self.permission_service.can_cancel("سندات الصرف"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        row = self.table.currentRow()
        if row < 0 or row >= len(self.filtered_vouchers):
            ErrorDialog("تنبيه", "يرجى اختيار سند", self).exec()
            return

        v = self.filtered_vouchers[row]
        vid = v['id']

        if v['status'] == 'ملغى':
            ErrorDialog("تنبيه", "السند ملغى مسبقاً", self).exec()
            return

        dlg = ConfirmationDialog(
            "إلغاء سند", f"هل تريد إلغاء السند: {v['voucher_number']}؟",
            self,
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        def _do():
            if FinanceExtrasFactory.is_remote():
                FinanceExtrasFactory.get_service().cancel_expense(
                    vid, "إلغاء يدوي"
                )
            else:
                with session_scope() as session:
                    obj = session.get(ExpenseVoucher, vid)
                    if obj:
                        obj.status = 'ملغى'
                        obj.cancelled_at = datetime.now()
                        obj.cancellation_reason = "إلغاء يدوي"

        def _ok(_):
            SuccessDialog("نجاح", "تم الإلغاء", self).exec()
            self.load_data()

        def _err(m):
            ErrorDialog("خطأ", str(m), self).exec()

        run_async(_do, on_result=_ok, on_error=_err)

    def print_voucher(self):
        if self.permission_service \
           and not self.permission_service.can_print("سندات الصرف"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return
        QMessageBox.information(
            self, "طباعة", "سيتم تنفيذها في مرحلة التقارير"
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())


# ============================================================
# DIALOG
# ============================================================

class ExpenseVoucherDialog(ModernDialog):
    """نافذة إضافة/تعديل سند صرف."""

    def __init__(self, user: User, voucher=None,
                 voucher_data: Optional[dict] = None, parent=None):
        super().__init__(
            "تعديل سند صرف"
            if (voucher or voucher_data) else "إضافة سند صرف جديد",
            "fa5s.file-invoice", parent, width=550, height=700,
        )
        self.user = user
        self.voucher = voucher
        self.voucher_data = voucher_data or {}
        self.voucher_id = (
            voucher.id if voucher
            else (voucher_data.get('id') if voucher_data else None)
        )

        self.setup_form()

        if voucher:
            self._load_from_orm(voucher)
        elif voucher_data:
            self._load_from_dict(voucher_data)
        else:
            # احصل على رقم من السيرفر
            if FinanceExtrasFactory.is_remote():
                try:
                    num = FinanceExtrasFactory.get_service() \
                        .get_next_voucher_number()
                    self.voucher_number_input.setText(num)
                except Exception:
                    pass

    def setup_form(self):
        self.add_widget(self._create_label("رقم السند:"))
        self.voucher_number_input = QLineEdit()
        self.voucher_number_input.setReadOnly(True)
        self.voucher_number_input.setText(self._gen_number())
        self.voucher_number_input.setStyleSheet("""
            QLineEdit {
                background: #F1F5F9;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px;
                font-weight: 700;
                color: #EF4444;
            }
        """)
        self.add_widget(self.voucher_number_input)

        self.add_widget(self._create_label("فئة المصروف:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            'مشتريات مواد', 'صيانة وتشغيل', 'فعاليات واحتفالات',
            'أنشطة مدرسية', 'أخرى',
        ])
        self.add_widget(self.category_combo)

        self.add_widget(self._create_label("اسم المستفيد / الجهة:"))
        self.beneficiary_input = QLineEditPlus(
            placeholder="اسم المستفيد أو الجهة"
        )
        self.add_widget(self.beneficiary_input)

        self.add_widget(self._create_label("المبلغ:"))
        self.amount_input = QDoubleSpinBoxEN()
        self.amount_input.setStyleSheet("""
            QDoubleSpinBox {
                border: 2px solid #EF4444;
                border-radius: 8px;
                padding: 8px;
                font-weight: 700;
                font-size: 16px;
                color: #DC2626;
                background: #FEF2F2;
            }
        """)
        self.add_widget(self.amount_input)

        pay_layout = QHBoxLayout()
        pay_layout.addWidget(self._create_label("طريقة الدفع:"))
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems([
            'نقداً', 'تحويل بنكي', 'كريمي/حاسب', 'شيك',
        ])
        pay_layout.addWidget(self.payment_method_combo, 1)
        self.add_widget(self._create_widget(pay_layout))

        inv_layout = QHBoxLayout()
        inv_layout.addWidget(self._create_label("رقم الفاتورة:"))
        self.invoice_input = QLineEditPlus(placeholder="رقم الفاتورة")
        inv_layout.addWidget(self.invoice_input, 1)
        self.add_widget(self._create_widget(inv_layout))

        self.add_widget(self._create_label("البيان والملاحظات:"))
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.add_widget(self.notes_input)

        self.add_button("إلغاء", self.reject, "default")
        self.add_button("حفظ", self.save_voucher, "primary")

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

    def _gen_number(self) -> str:
        return f"EXP-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def _load_from_orm(self, v):
        self.voucher_number_input.setText(v.voucher_number or '')
        self.category_combo.setCurrentText(v.expense_category or '')
        self.beneficiary_input.setText(v.beneficiary_name or '')
        self.amount_input.setValue(float(v.amount or 0))
        self.payment_method_combo.setCurrentText(
            v.payment_method or 'نقداً'
        )
        self.invoice_input.setText(v.invoice_number or "")
        self.notes_input.setText(v.notes or "")

    def _load_from_dict(self, d):
        self.voucher_number_input.setText(d.get('voucher_number', ''))
        self.category_combo.setCurrentText(
            d.get('expense_category', '')
        )
        self.beneficiary_input.setText(d.get('beneficiary_name', ''))
        self.amount_input.setValue(d.get('amount', 0))
        self.payment_method_combo.setCurrentText(
            d.get('payment_method', 'نقداً')
        )
        self.invoice_input.setText(d.get('invoice_number', ''))
        self.notes_input.setText(d.get('notes', ''))

    def save_voucher(self):
        if not self.beneficiary_input.text().strip():
            ErrorDialog("تنبيه", "أدخل اسم المستفيد", self).exec()
            return
        if self.amount_input.value() <= 0:
            ErrorDialog("تنبيه", "أدخل مبلغاً صحيحاً", self).exec()
            return

        payload = {
            'expense_category': self.category_combo.currentText(),
            'beneficiary_name': self.beneficiary_input.text().strip(),
            'amount': float(self.amount_input.value()),
            'payment_method': self.payment_method_combo.currentText(),
            'invoice_number': self.invoice_input.text().strip() or None,
            'notes': self.notes_input.toPlainText().strip() or None,
        }

        try:
            if FinanceExtrasFactory.is_remote():
                service = FinanceExtrasFactory.get_service()
                if self.voucher_id:
                    service.update_expense(self.voucher_id, payload)
                else:
                    service.create_expense(payload)
            else:
                self._save_local(payload)

            self.accept()
        except Exception as e:
            ErrorDialog("خطأ", str(e), self).exec()

    def _save_local(self, payload):
        with session_scope() as session:
            if self.voucher:
                obj = session.get(ExpenseVoucher, self.voucher.id)
            elif self.voucher_id:
                obj = session.get(ExpenseVoucher, self.voucher_id)
            else:
                obj = ExpenseVoucher()
                session.add(obj)

            obj.voucher_number = self.voucher_number_input.text()
            obj.expense_category = payload['expense_category']
            obj.beneficiary_name = payload['beneficiary_name']
            obj.amount = Decimal(str(payload['amount']))
            obj.payment_method = payload['payment_method']
            obj.invoice_number = payload['invoice_number']
            obj.notes = payload['notes']
            obj.created_by_user_id = self.user.id
            obj.status = 'نشط'
            session.commit()