"""
واجهة سندات القبض - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Dict, Optional
import qtawesome as qta
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.database.session import session_scope
from app.database.models import (
    Student, Receipt, FeeInstallment, StudentFee, AcademicYear, User, Grade, Section
)
from app.services.finance_factory import FinanceFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    PageHeader, Card, QDateEditEN, QDoubleSpinBoxEN, QLineEditPlus, 
    SearchBox, ModernTable, Badge, GradientButton, IconButton, KPICard
)
from app.views.widgets.dialogs import (
    ConfirmationDialog, SuccessDialog, ErrorDialog, ModernDialog
)
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload


class ReceiptsPage(QWidget):
    """صفحة سندات القبض - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ تخزين ID قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        self.user_id = user.id if user else None
        
        # ✅ dicts بدلاً من ORM objects
        self.all_receipts: List[Dict] = []
        self.current_filtered_receipts: List[Dict] = []
        
        # ✅ debounce للبحث
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self.filter_receipts)
        
        # ✅ مراجع لبطاقات KPI
        self.today_value_label = None
        self.month_value_label = None
        self.total_value_label = None
        self.cancelled_value_label = None
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل البيانات في الخلفية
        QTimer.singleShot(100, self.load_data)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)
        
        # رأس الصفحة
        title = QLabel("سندات القبض والدفعات المالية")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("إدارة سندات القبض والمدفوعات من الطلاب")
        subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(subtitle)
        
        # بطاقات إحصائية
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.today_receipts_card = KPICard(
            "مقبوضات اليوم", "0 ر.ي", "fa5s.calendar-day", "#1976D3"
        )
        stats_layout.addWidget(self.today_receipts_card)
        
        self.month_receipts_card = KPICard(
            "مقبوضات الشهر", "0 ر.ي", "fa5s.calendar-alt", "#10B981"
        )
        stats_layout.addWidget(self.month_receipts_card)
        
        self.total_receipts_card = KPICard(
            "إجمالي المقبوضات", "0 ر.ي", "fa5s.coins", "#F59E0B"
        )
        stats_layout.addWidget(self.total_receipts_card)
        
        self.cancelled_card = KPICard(
            "سندات ملغاة", "0", "fa5s.ban", "#EF4444"
        )
        stats_layout.addWidget(self.cancelled_card)
        
        main_layout.addWidget(self._create_widget(stats_layout))
        
        # ✅ اكتشاف مراجع القيم في KPICard
        self._find_kpi_value_labels()
        
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
        
        # بحث
        self.search_box = SearchBox("بحث برقم السند أو اسم الطالب...")
        self.search_box.textChanged.connect(self._on_search_text_changed)
        filter_layout.addWidget(self.search_box)
        
        # فلتر التاريخ
        filter_layout.addWidget(QLabel("من:"))
        self.date_from = QDateEditEN(QDate.currentDate().addMonths(-1))
        self.date_from.dateChanged.connect(self.filter_receipts)
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("إلى:"))
        self.date_to = QDateEditEN()
        self.date_to.dateChanged.connect(self.filter_receipts)
        filter_layout.addWidget(self.date_to)
        
        # فلتر الحالة
        filter_layout.addWidget(QLabel("الحالة:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["جميع الحالات", "نشط", "ملغى"])
        self.status_filter.currentIndexChanged.connect(self.filter_receipts)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch()
        
        # زر إضافة سند
        add_btn = GradientButton("إضافة سند", "fa5s.plus")
        add_btn.clicked.connect(self.add_receipt)
        filter_layout.addWidget(add_btn)
        
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
        
        self.count_label = QLabel("إجمالي السندات: 0")
        self.count_label.setObjectName("count_label")
        toolbar.addWidget(self.count_label)
        
        toolbar.addStretch()
        
        # أزرار العمليات
        edit_btn = IconButton('fa5s.edit', "تعديل", color='#1976D3')
        edit_btn.clicked.connect(self.edit_receipt)
        toolbar.addWidget(edit_btn)
        
        cancel_btn = IconButton('fa5s.ban', "إلغاء سند", color='#F59E0B')
        cancel_btn.clicked.connect(self.cancel_receipt)
        toolbar.addWidget(cancel_btn)
        
        print_btn = IconButton('fa5s.print', "طباعة", color='#10B981')
        print_btn.clicked.connect(self.print_receipt)
        toolbar.addWidget(print_btn)
        
        card_layout.addLayout(toolbar)
        
        # الجدول
        self.table = ModernTable()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "رقم السند", "اسم الطالب", "القسط", "المبلغ",
            "التاريخ", "طريقة الدفع", "الموظف", "الحالة", "الملاحظات"
        ])
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 180)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 130)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 100)
        self.table.setColumnWidth(7, 70)
        self.table.setColumnWidth(8, 150)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)        
        self.table.doubleClicked.connect(self.edit_receipt)
        card_layout.addWidget(self.table)
        
        main_layout.addWidget(table_card)
    
    def _create_widget(self, layout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    def _find_kpi_value_labels(self):
        """✅ البحث عن مراجع قيم KPI بشكل آمن."""
        try:
            cards = [
                (self.today_receipts_card, 'today'),
                (self.month_receipts_card, 'month'),
                (self.total_receipts_card, 'total'),
                (self.cancelled_card, 'cancelled'),
            ]
            
            for card, key in cards:
                # البحث عن label بقيمة (يحتوي على "0")
                labels = card.findChildren(QLabel)
                value_label = None
                for lbl in labels:
                    if lbl.text() == "0 ر.ي" or lbl.text() == "0":
                        value_label = lbl
                        break
                    if "font-size: 24px" in lbl.styleSheet() or \
                       "font-size: 22px" in lbl.styleSheet() or \
                       "font-size: 20px" in lbl.styleSheet():
                        value_label = lbl
                
                if key == 'today':
                    self.today_value_label = value_label
                elif key == 'month':
                    self.month_value_label = value_label
                elif key == 'total':
                    self.total_value_label = value_label
                elif key == 'cancelled':
                    self.cancelled_value_label = value_label
        except Exception as e:
            print(f"خطأ في البحث عن مراجع KPI: {str(e)}")
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_data(self):
        self.loading_overlay.show_loading("جاري التحميل...")
        ayid = self.academic_year_id

        def _fetch():
            if FinanceFactory.is_remote():
                return FinanceFactory.get_service().list_receipts(
                    academic_year_id=ayid
                )
            else:
                from app.database.session import session_scope
                from app.database.models import Receipt, Student
                from sqlalchemy import select, func
                from sqlalchemy.orm import joinedload
                from datetime import date as _date, datetime as _dt
                with session_scope() as session:
                    receipts = session.execute(
                        select(Receipt)
                        .options(
                            joinedload(Receipt.student),
                            joinedload(Receipt.installment),
                            joinedload(Receipt.created_by_user),
                        )
                        .join(Student, Receipt.student_id == Student.id)
                        .where(Student.academic_year_id == ayid)
                        .order_by(Receipt.payment_date.desc())
                    ).unique().scalars().all()

                    today = _date.today()
                    month_start = today.replace(day=1)
                    today_start = _dt.combine(today, _dt.min.time())
                    month_start_dt = _dt.combine(month_start, _dt.min.time())

                    today_total = session.query(
                        func.sum(Receipt.amount_paid)
                    ).filter(
                        Receipt.status == 'نشط',
                        Receipt.payment_date >= today_start,
                    ).scalar() or 0

                    month_total = session.query(
                        func.sum(Receipt.amount_paid)
                    ).filter(
                        Receipt.status == 'نشط',
                        Receipt.payment_date >= month_start_dt,
                    ).scalar() or 0

                    total_all = session.query(
                        func.sum(Receipt.amount_paid)
                    ).filter(Receipt.status == 'نشط').scalar() or 0

                    cancelled = session.query(
                        func.count(Receipt.id)
                    ).filter(Receipt.status == 'ملغى').scalar() or 0

                    return {
                        'receipts': [
                            {
                                'id': r.id,
                                'receipt_number': r.receipt_number or '',
                                'student_id': r.student_id,
                                'student_name': r.student.full_name if r.student else '',
                                'installment_id': r.installment_id,
                                'installment_name': (
                                    r.installment.installment_name
                                    if r.installment else ''
                                ),
                                'amount_paid': float(r.amount_paid or 0),
                                'payment_date': r.payment_date,
                                'payment_date_str': (
                                    r.payment_date.strftime("%Y/%m/%d %H:%M")
                                    if r.payment_date else ''
                                ),
                                'payment_method': r.payment_method or '',
                                'created_by': (
                                    r.created_by_user.username
                                    if r.created_by_user else ''
                                ),
                                'status': r.status or 'نشط',
                                'notes': r.notes or '',
                            }
                            for r in receipts
                        ],
                        'stats': {
                            'today_total': float(today_total),
                            'month_total': float(month_total),
                            'total_all': float(total_all),
                            'cancelled_count': cancelled,
                        },
                    }

        def _ok(data):
            try:
                self.all_receipts = data['receipts']
                self.current_filtered_receipts = list(self.all_receipts)
                self._update_stats_display(data['stats'])
                self.display_receipts(self.all_receipts)
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            ErrorDialog("خطأ", f"فشل: {m}", self).exec()

        run_async(_fetch, on_result=_ok, on_error=_err)
        
    # ============================================================
    # ✅ عرض البيانات
    # ============================================================
    
    def display_receipts(self, receipts: List[Dict]):
        """عرض السندات في الجدول."""
        self.table.setRowCount(len(receipts))
        
        for row, receipt in enumerate(receipts):
            self.table.setItem(
                row, 0, QTableWidgetItem(receipt['receipt_number'])
            )
            self.table.setItem(
                row, 1, QTableWidgetItem(receipt['student_name'])
            )
            self.table.setItem(
                row, 2, QTableWidgetItem(receipt['installment_name'])
            )
            
            # المبلغ
            amount_item = QTableWidgetItem(f"{receipt['amount_paid']:,.2f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            amount_item.setForeground(QColor('#10B981'))
            amount_item.setFont(QFont("Cairo", 10, QFont.Weight.Bold))
            self.table.setItem(row, 3, amount_item)
            
            self.table.setItem(
                row, 4, QTableWidgetItem(receipt['payment_date_str'])
            )
            self.table.setItem(
                row, 5, QTableWidgetItem(receipt['payment_method'])
            )
            self.table.setItem(
                row, 6, QTableWidgetItem(receipt['created_by'])
            )
            
            # الحالة
            status_item = QTableWidgetItem(receipt['status'])
            if receipt['status'] == 'نشط':
                status_item.setForeground(QColor('#10B981'))
                status_item.setFont(QFont("Cairo", 9, QFont.Weight.Bold))
            else:
                status_item.setForeground(QColor('#EF4444'))
            self.table.setItem(row, 7, status_item)
            
            self.table.setItem(
                row, 8, QTableWidgetItem(receipt['notes'])
            )

            self.table.setRowHeight(row, 35)
        
        self.count_label.setText(f"إجمالي السندات: {len(receipts)}")
    
    def _update_stats_display(self, stats: Dict):
        """تحديث بطاقات الإحصائيات."""
        try:
            if self.today_value_label:
                self.today_value_label.setText(
                    f"{stats['today_total']:,.0f} ر.ي"
                )
            if self.month_value_label:
                self.month_value_label.setText(
                    f"{stats['month_total']:,.0f} ر.ي"
                )
            if self.total_value_label:
                self.total_value_label.setText(
                    f"{stats['total_all']:,.0f} ر.ي"
                )
            if self.cancelled_value_label:
                self.cancelled_value_label.setText(
                    str(stats['cancelled_count'])
                )
        except Exception as e:
            print(f"خطأ في تحديث الإحصائيات: {str(e)}")
    
    # ============================================================
    # ✅ الفلترة
    # ============================================================
    
    def _on_search_text_changed(self):
        """عند تغيير نص البحث - debounce."""
        self._search_timer.stop()
        self._search_timer.start()
    
    def filter_receipts(self):
        """تصفية السندات."""
        search_text = self.search_box.text().lower().strip()
        date_from = self.date_from.date().toPython()
        date_to = self.date_to.date().toPython()
        status = self.status_filter.currentText()
        
        filtered = []
        for receipt in self.all_receipts:
            # فلتر البحث
            if search_text:
                student_name = receipt['student_name'].lower()
                receipt_number = receipt['receipt_number'].lower()
                if search_text not in receipt_number and \
                   search_text not in student_name:
                    continue
            
            # فلتر التاريخ
            receipt_date = (
                receipt['payment_date'].date() 
                if receipt['payment_date'] else date.today()
            )
            if receipt_date < date_from or receipt_date > date_to:
                continue
            
            # فلتر الحالة
            if status != "جميع الحالات" and receipt['status'] != status:
                continue
            
            filtered.append(receipt)
        
        self.current_filtered_receipts = filtered
        self.display_receipts(filtered)
    
    # ============================================================
    # ✅ الحصول على السند المحدد
    # ============================================================
    
    def _get_selected_receipt_id(self) -> Optional[int]:
        """الحصول على ID السند المحدد."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
        
        if current_row >= len(self.current_filtered_receipts):
            return None
        
        return self.current_filtered_receipts[current_row]['id']
    
    # ============================================================
    # ✅ العمليات
    # ============================================================
    
    def add_receipt(self):
        if (self.permission_service
                and not self.permission_service.can_add("سندات القبض")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return
        dialog = ReceiptDialog(
            self.user_id, self.academic_year_id, parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            SuccessDialog("نجاح", "تم الحفظ", self).exec()

    def edit_receipt(self):
        if (self.permission_service
                and not self.permission_service.can_edit("سندات القبض")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return
        rid = self._get_selected_receipt_id()
        if not rid:
            ErrorDialog("تنبيه", "اختر سنداً", self).exec()
            return
        try:
            if FinanceFactory.is_remote():
                data = FinanceFactory.get_service().get_receipt(rid)
            else:
                from app.database.session import session_scope
                from app.database.models import Receipt
                with session_scope() as session:
                    r = session.get(Receipt, rid)
                    if not r:
                        return
                    data = {
                        'id': r.id,
                        'receipt_number': r.receipt_number or '',
                        'student_id': r.student_id,
                        'installment_id': r.installment_id,
                        'amount_paid': float(r.amount_paid or 0),
                        'payment_method': r.payment_method or '',
                        'reference_number': r.reference_number or '',
                        'notes': r.notes or '',
                        'status': r.status or 'نشط',
                    }
            dlg = ReceiptDialog(
                self.user_id, self.academic_year_id,
                receipt_data=data, parent=self,
            )
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self.load_data()
                SuccessDialog("نجاح", "تم التحديث", self).exec()
        except Exception as e:
            ErrorDialog("خطأ", f"فشل: {e}", self).exec()

    def cancel_receipt(self):
        if (self.permission_service
                and not self.permission_service.can_cancel("سندات القبض")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return
        rid = self._get_selected_receipt_id()
        if not rid:
            ErrorDialog("تنبيه", "اختر سنداً", self).exec()
            return
        receipt = next(
            (r for r in self.current_filtered_receipts if r['id'] == rid),
            None,
        )
        if not receipt:
            return
        if receipt['status'] == 'ملغى':
            ErrorDialog("تنبيه", "ملغى مسبقاً", self).exec()
            return

        dlg = CancelReceiptDialog(receipt['receipt_number'], parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        reason = dlg.get_reason()
        if not reason.strip():
            ErrorDialog("تنبيه", "أدخل السبب", self).exec()
            return

        def _do():
            if FinanceFactory.is_remote():
                FinanceFactory.get_service().cancel_receipt(rid, reason)
            else:
                from app.database.session import session_scope
                from app.database.models import Receipt, FeeInstallment
                from datetime import datetime
                with session_scope() as session:
                    r = session.get(Receipt, rid)
                    if not r:
                        return
                    r.status = 'ملغى'
                    r.cancellation_reason = reason
                    r.cancelled_at = datetime.now()
                    if r.installment_id:
                        inst = session.get(FeeInstallment, r.installment_id)
                        if inst:
                            inst.paid_amount = max(
                                Decimal('0'),
                                (inst.paid_amount or Decimal('0')) - r.amount_paid,
                            )
                            inst.is_paid = inst.paid_amount >= inst.amount

        try:
            _do()
            SuccessDialog("نجاح", "تم الإلغاء", self).exec()
            self.load_data()
        except Exception as e:
            ErrorDialog("خطأ", f"فشل: {e}", self).exec()

    def print_receipt(self):
        """طباعة سند."""
        if self.permission_service and not self.permission_service.can_print("سندات القبض"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للطباعة في سندات القبض"
            )
            return

        receipt_id = self._get_selected_receipt_id()
        if not receipt_id:
            ErrorDialog("تنبيه", "يرجى اختيار سند للطباعة", self).exec()
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


# ============================================================
# ✅ حوار إضافة/تعديل سند (Async)
# ============================================================

class ReceiptDialog(ModernDialog):
    """نافذة إضافة/تعديل سند قبض - مع تحميل غير متزامن."""
    
    def __init__(self, user_id: int, academic_year_id: int,
                 receipt_data: Optional[dict] = None, parent=None):
        super().__init__(
            "تعديل سند قبض" if receipt_data else "إضافة سند قبض جديد",
            "fa5s.receipt",
            parent,
            width=600,
            height=750
        )
        
        # ✅ تخزين IDs فقط
        self.user_id = user_id
        self.academic_year_id = academic_year_id
        self.receipt_data = receipt_data
        self.receipt_id = receipt_data['id'] if receipt_data else None
        
        # ✅ dicts
        self.selected_student_id: Optional[int] = None
        self.selected_student_data: Dict = {}
        self.students_data: List[Dict] = []
        self.installments_data: List[Dict] = []
        
        # ✅ debounce للبحث
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self._search_students_now)
        
        # ✅ LoadingOverlay للحوار
        self.dialog_loading = LoadingOverlay(self)
        
        self.setup_form()
        
        # ✅ تحميل أولي
        QTimer.singleShot(100, self._load_initial_data)
    
    def setup_form(self):
        """إعداد النموذج."""
        # البحث عن طالب
        self.add_widget(self._create_label("البحث عن طالب:"))
        
        search_layout = QHBoxLayout()
        self.student_search = QLineEditPlus(placeholder="ابحث بالاسم أو الرقم...")
        self.student_search.textChanged.connect(self._on_search_text_changed)
        search_layout.addWidget(self.student_search)
        
        search_btn = GradientButton("بحث", 'fa5s.search')
        search_btn.clicked.connect(self._search_students_now)
        search_layout.addWidget(search_btn)
        
        self.add_widget(self._create_widget(search_layout))
        
        # قائمة الطلاب
        self.students_list = QListWidget()
        self.students_list.setMaximumHeight(120)
        self.add_widget(self.students_list)
        
        # معلومات الطالب المختار
        self.student_info = QLabel("لم يتم اختيار طالب")
        self.student_info.setStyleSheet("""
            padding: 8px;
            background: #F8FAFC;
            border-radius: 8px;
            color: #64748B;
        """)
        self.add_widget(self.student_info)
        
        # الأقساط المتاحة
        self.add_widget(self._create_label("اختيار القسط:"))
        self.installments_combo = QComboBox()
        self.installments_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #1976D3;
            }
        """)
        self.installments_combo.currentIndexChanged.connect(
            self._on_installment_selected
        )
        self.add_widget(self.installments_combo)
        
        # رقم السند
        receipt_layout = QHBoxLayout()
        
        receipt_layout.addWidget(self._create_label("رقم السند:"))
        self.receipt_number_input = QLineEdit()
        self.receipt_number_input.setReadOnly(True)
        self.receipt_number_input.setText(self._generate_receipt_number())
        self.receipt_number_input.setStyleSheet("""
            QLineEdit {
                background: #F1F5F9;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px;
                font-weight: 700;
                color: #1976D3;
            }
        """)
        receipt_layout.addWidget(self.receipt_number_input)
        
        self.add_widget(self._create_widget(receipt_layout))
        
        # المبلغ
        amount_layout = QHBoxLayout()
        
        amount_layout.addWidget(self._create_label("المبلغ المدفوع:"))
        self.amount_input = QDoubleSpinBoxEN()
        self.amount_input.setStyleSheet("""
            QDoubleSpinBox {
                border: 2px solid #10B981;
                border-radius: 8px;
                padding: 8px;
                font-weight: 700;
                font-size: 16px;
                color: #059669;
                background: #ECFDF5;
            }
            QDoubleSpinBox:focus {
                border-color: #059669;
            }
        """)
        amount_layout.addWidget(self.amount_input)
        
        self.add_widget(self._create_widget(amount_layout))
        
        # طريقة الدفع
        payment_layout = QHBoxLayout()
        
        payment_layout.addWidget(self._create_label("طريقة الدفع:"))
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems([
            'نقداً', 'تحويل بنكي', 'كريمي/حاسب', 'شيك'
        ])
        payment_layout.addWidget(self.payment_method_combo)
        
        payment_layout.addWidget(self._create_label("رقم المرجع:"))
        self.reference_input = QLineEditPlus(placeholder="رقم الحوالة/الشيك...")
        payment_layout.addWidget(self.reference_input)
        
        self.add_widget(self._create_widget(payment_layout))
        
        # الملاحظات
        self.add_widget(self._create_label("ملاحظات:"))
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        self.add_widget(self.notes_input)
        
        # الأزرار
        self.add_button("إلغاء", self.reject, "default")
        self.add_button("حفظ", self.save_receipt, "primary")
        
        self.students_list.itemClicked.connect(self.select_student)
    
    def _create_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("color: #475569; font-weight: 600; font-size: 12px;")
        return label
    
    def _create_widget(self, layout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    def _generate_receipt_number(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"RCV-{timestamp}"
    
    # ============================================================
    # ✅ التحميل غير المتزامن للحوار
    # ============================================================
    
    def _load_initial_data(self):
        if self.receipt_data:
            self.receipt_number_input.setText(self.receipt_data['receipt_number'])
            self.amount_input.setValue(self.receipt_data['amount_paid'])
            self.payment_method_combo.setCurrentText(
                self.receipt_data['payment_method']
            )
            self.reference_input.setText(self.receipt_data['reference_number'])
            self.notes_input.setText(self.receipt_data['notes'])
            self.selected_student_id = self.receipt_data['student_id']
            self._load_student_info(self.receipt_data['student_id'])
        else:
            # ✅ احصل على رقم سند من السيرفر
            if FinanceFactory.is_remote():
                try:
                    num = FinanceFactory.get_service().get_next_receipt_number()
                    self.receipt_number_input.setText(num)
                except Exception:
                    pass
            self._search_students_now()

    def _load_student_info(self, student_id: int):
        """تحميل معلومات الطالب المحدد (Async)."""
        def _fetch_data():
            with session_scope() as session:
                student = session.execute(
                    select(Student)
                    .options(
                        joinedload(Student.grade),
                        joinedload(Student.section)
                    )
                    .where(Student.id == student_id)
                ).unique().scalar_one_or_none()
                
                if not student:
                    return None
                
                return {
                    'id': student.id,
                    'full_name': student.full_name or '',
                    'student_number': student.student_number or '',
                    'grade_name': student.grade.grade_name if student.grade else '',
                    'section_name': student.section.section_name if student.section else '',
                }
        
        def _on_result(data):
            if data:
                self.selected_student_data = data
                self.student_info.setText(
                    f"الطالب: {data['full_name']}\n"
                    f"الصف: {data['grade_name']} - شعبة: {data['section_name']}"
                )
                self.student_info.setStyleSheet("""
                    padding: 10px;
                    background: #ECFDF5;
                    border-radius: 8px;
                    color: #059669;
                    font-weight: 500;
                """)
                
                # تحميل الأقساط
                self._load_student_installments(data['id'])
        
        run_async(_fetch_data, on_result=_on_result)
    
    def _on_search_text_changed(self):
        self._search_timer.stop()
        self._search_timer.start()
    
    def _search_students_now(self):
        """البحث عن الطلاب (Async)."""
        search_text = self.student_search.text().strip()
        academic_year_id = self.academic_year_id
        
        def _fetch_data():
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
                
                students = session.execute(query.limit(20)).scalars().all()
                
                return [
                    {
                        'id': s.id,
                        'full_name': s.full_name or '',
                        'student_number': s.student_number or '',
                    }
                    for s in students
                ]
        
        def _on_result(data):
            self.students_data = data
            self.students_list.clear()
            
            for student in data:
                item = QListWidgetItem(
                    f"{student['full_name']} - {student['student_number']}"
                )
                item.setData(Qt.ItemDataRole.UserRole, student['id'])
                self.students_list.addItem(item)
        
        run_async(_fetch_data, on_result=_on_result)
    
    def select_student(self, item: QListWidgetItem):
        """اختيار طالب من القائمة."""
        student_id = item.data(Qt.ItemDataRole.UserRole)
        
        # البحث في القائمة المحفوظة
        student = next(
            (s for s in self.students_data if s['id'] == student_id),
            None
        )
        if not student:
            return
        
        self.selected_student_id = student_id
        self.selected_student_data = student
        
        # ✅ تحميل معلومات الطالب الكاملة (grade + section)
        self._load_student_info(student_id)
    
    def _load_student_installments(self, student_id: int):
        """تحميل أقساط الطالب (Async)."""
        academic_year_id = self.academic_year_id
        
        def _fetch_data():
            with session_scope() as session:
                # جلب StudentFee للطالب
                student_fee = session.execute(
                    select(StudentFee).where(
                        StudentFee.student_id == student_id,
                        StudentFee.academic_year_id == academic_year_id
                    )
                ).scalar_one_or_none()
                
                if not student_fee:
                    return []
                
                # جلب الأقساط غير المدفوعة
                installments = session.execute(
                    select(FeeInstallment).where(
                        FeeInstallment.student_fee_id == student_fee.id,
                        FeeInstallment.is_paid == False
                    ).order_by(FeeInstallment.installment_number)
                ).scalars().all()
                
                # ✅ تحويل إلى dicts
                return [
                    {
                        'id': inst.id,
                        'installment_number': inst.installment_number or 0,
                        'installment_name': inst.installment_name or '',
                        'amount': float(inst.amount or 0),
                        'paid_amount': float(inst.paid_amount or 0),
                        'remaining': float((inst.amount or 0) - (inst.paid_amount or 0)),
                    }
                    for inst in installments
                ]
        
        def _on_result(data):
            self.installments_data = data
            
            # ✅ blockSignals لتجنب استدعاء _on_installment_selected
            self.installments_combo.blockSignals(True)
            self.installments_combo.clear()
            
            self.installments_combo.addItem(
                "سداد المتأخرات والديون المرحّلة أولاً", None
            )
            
            for inst in data:
                self.installments_combo.addItem(
                    f"{inst['installment_name']} - المتبقي: "
                    f"{inst['remaining']:,.2f} ر.ي",
                    inst['id']
                )
            
            # ✅ إذا كنا في وضع التعديل، اختر القسط المرتبط
            if self.receipt_data and self.receipt_data.get('installment_id'):
                idx = self.installments_combo.findData(
                    self.receipt_data['installment_id']
                )
                if idx >= 0:
                    self.installments_combo.setCurrentIndex(idx)
            
            self.installments_combo.blockSignals(False)
            
            # استدعاء مرة واحدة لتحديث المبلغ
            self._on_installment_selected()
        
        run_async(_fetch_data, on_result=_on_result)
    
    def _on_installment_selected(self):
        """عند اختيار قسط."""
        installment_id = self.installments_combo.currentData()
        
        if not installment_id:
            return
        
        # ✅ البحث في البيانات المحفوظة (dicts)
        inst = next(
            (i for i in self.installments_data if i['id'] == installment_id),
            None
        )
        
        if inst:
            self.amount_input.setValue(inst['remaining'])
    
    def save_receipt(self):
        if not self.selected_student_id:
            ErrorDialog("تنبيه", "اختر طالباً", self).exec()
            return
        if self.amount_input.value() <= 0:
            ErrorDialog("تنبيه", "مبلغ غير صحيح", self).exec()
            return

        payload = {
            'student_id': self.selected_student_id,
            'installment_id': self.installments_combo.currentData(),
            'amount_paid': float(self.amount_input.value()),
            'payment_method': self.payment_method_combo.currentText(),
            'reference_number': self.reference_input.text().strip() or None,
            'notes': self.notes_input.toPlainText().strip() or None,
        }

        def _do():
            if FinanceFactory.is_remote():
                service = FinanceFactory.get_service()
                if self.receipt_id:
                    service.update_receipt(self.receipt_id, payload)
                else:
                    service.create_receipt(payload)
            else:
                self._save_local(payload)

        try:
            _do()
            self.accept()
        except Exception as e:
            ErrorDialog("خطأ", f"فشل: {e}", self).exec()

    def _save_local(self, payload):
        from app.database.session import session_scope
        from app.database.models import Receipt, FeeInstallment
        from sqlalchemy import select
        from datetime import datetime
        with session_scope() as session:
            if self.receipt_id:
                r = session.get(Receipt, self.receipt_id)
                if not r:
                    raise Exception("السند غير موجود")
                # أعد القسط القديم
                if r.installment_id:
                    old = session.get(FeeInstallment, r.installment_id)
                    if old:
                        old.paid_amount = max(
                            Decimal('0'),
                            (old.paid_amount or Decimal('0')) - r.amount_paid,
                        )
                        old.is_paid = old.paid_amount >= old.amount
            else:
                r = Receipt(
                    receipt_number=self.receipt_number_input.text(),
                    created_by_user_id=self.user_id,
                    status='نشط',
                )
                session.add(r)

            r.student_id = payload['student_id']
            r.installment_id = payload['installment_id']
            r.amount_paid = Decimal(str(payload['amount_paid']))
            r.payment_method = payload['payment_method']
            r.reference_number = payload['reference_number']
            r.notes = payload['notes']
            session.flush()

            if payload['installment_id']:
                inst = session.get(FeeInstallment, payload['installment_id'])
                if inst:
                    inst.paid_amount = (
                        inst.paid_amount or Decimal('0')
                    ) + Decimal(str(payload['amount_paid']))
                    if inst.paid_amount >= inst.amount:
                        inst.is_paid = True
            session.commit()
            

# ============================================================
# ✅ حوار إلغاء سند
# ============================================================

class CancelReceiptDialog(ModernDialog):
    """نافذة إلغاء سند."""
    
    def __init__(self, receipt_number: str, parent=None):
        super().__init__(
            "إلغاء سند",
            "fa5s.receipt",
            parent,
            width=400,
            height=350
        )
        
        info_label = QLabel(f"إلغاء السند رقم: {receipt_number}")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 700;
            color: #EF4444;
            padding: 10px;
        """)
        self.add_widget(info_label)
        
        self.add_widget(self._create_label("سبب الإلغاء:"))
        self.reason_input = QTextEdit()
        self.reason_input.setMaximumHeight(80)
        self.reason_input.setPlaceholderText("أدخل سبب الإلغاء...")
        self.add_widget(self.reason_input)
        
        self.add_button("تراجع", self.reject, "default")
        self.add_button("تأكيد الإلغاء", self.accept, "danger")
    
    def _create_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("color: #475569; font-weight: 600; font-size: 12px;")
        return label
    
    def get_reason(self) -> str:
        return self.reason_input.toPlainText().strip()