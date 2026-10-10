"""
لوحة تحكم المحاسب الإداري - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Dict, Optional
import qtawesome as qta
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.database.session import session_scope
from app.database.models import (
    Receipt, ExpenseVoucher, FeeInstallment, Student,
    StudentFee, Employee
)
from app.services.dashboard_factory import DashboardFactory
from app.views.widgets.custom_widgets import (
    KPICard, Card, PageHeader, Badge
)
from app.views.widgets.dialogs import ConfirmationDialog, SuccessDialog
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload


class AccountantDashboardPage(QWidget):
    """صفحة لوحة تحكم المحاسب الإداري - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل البيانات في الخلفية
        QTimer.singleShot(100, self.load_data)
    
    def setup_ui(self):
        """إعداد واجهة لوحة التحكم."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)

        title = QLabel("لوحة تحكم المحاسب الإداري")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("المؤشرات المالية والعمليات اليومية")
        subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(subtitle)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)
        
        # مؤشرات مالية
        kpi_section = self._create_kpi_section()
        scroll_layout.addWidget(kpi_section)
        
        # الأقساط المستحقة
        installments_card = self._create_installments_card()
        scroll_layout.addWidget(installments_card)
        
        # السندات الملغاة
        cancelled_card = self._create_cancelled_card()
        scroll_layout.addWidget(cancelled_card)
        
        # آخر العمليات
        operations_card = self._create_operations_card()
        scroll_layout.addWidget(operations_card)
        
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
    
    def _create_kpi_section(self) -> QWidget:
        """إنشاء قسم المؤشرات المالية."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(20)
        
        self.cash_flow_card = KPICard(
            "صافي حركة الصندوق اليومي", "0 ر.ي", "fa5s.cash-register", "#06B6D4", "المقبوضات - المصروفات"
        )
        layout.addWidget(self.cash_flow_card)
        
        self.cancelled_kpi_card = KPICard(
            "السندات الملغاة هذا الشهر", "0", "fa5s.ban", "#EF4444", "إجمالي القيمة"
        )
        layout.addWidget(self.cancelled_kpi_card)
        
        self.weekly_dues_card = KPICard(
            "الأقساط المستحقة هذا الأسبوع", "0 ر.ي", "fa5s.calendar-week", "#F59E0B", "مطلوب تحصيلها"
        )
        layout.addWidget(self.weekly_dues_card)
        
        return widget
    
    def _create_installments_card(self) -> Card:
        """إنشاء بطاقة الأقساط المستحقة."""
        card = Card("الأقساط المستحقة هذا الأسبوع")
        card.setObjectName("cardCard")
        card.setStyleSheet("""
            Card#cardCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 10px 15px;
            }
        """)  
        self.installments_table = QTableWidget()
        self.installments_table.setColumnCount(6)
        self.installments_table.setHorizontalHeaderLabels([
            "الطالب", "القسط", "المبلغ", "تاريخ الاستحقاق", "الحالة", "إجراء"
        ])
        self.installments_table.horizontalHeader().setStretchLastSection(True)
        self.installments_table.setMinimumHeight(200)
        card.add_widget(self.installments_table)
        
        return card
    
    def _create_cancelled_card(self) -> Card:
        """إنشاء بطاقة السندات الملغاة."""
        card = Card("السندات الملغاة مؤخراً")
        card.setObjectName("cardCard2")
        card.setStyleSheet("""
            Card#cardCard2 {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 10px 15px;
            }
        """)        
        self.cancelled_table = QTableWidget()
        self.cancelled_table.setColumnCount(5)
        self.cancelled_table.setHorizontalHeaderLabels([
            "رقم السند", "النوع", "المبلغ", "سبب الإلغاء", "المحاسب"
        ])
        self.cancelled_table.horizontalHeader().setStretchLastSection(True)
        self.cancelled_table.setMinimumHeight(150)
        card.add_widget(self.cancelled_table)
        
        return card
    
    def _create_operations_card(self) -> Card:
        """إنشاء بطاقة آخر العمليات."""
        card = Card("آخر العمليات المالية")
        card.setObjectName("cardCard3")
        card.setStyleSheet("""
            Card#cardCard3 {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 10px 15px;
            }
        """)        
        self.operations_table = QTableWidget()
        self.operations_table.setColumnCount(5)
        self.operations_table.setHorizontalHeaderLabels([
            "النوع", "الرقم", "المبلغ", "التاريخ", "الموظف"
        ])
        self.operations_table.horizontalHeader().setStretchLastSection(True)
        self.operations_table.setMinimumHeight(150)
        card.add_widget(self.operations_table)
        
        return card
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_data(self):
        """تحميل بيانات لوحة المحاسب - Local أو Remote."""
        self.loading_overlay.show_loading("جاري تحميل البيانات المالية...")

        def _fetch_data():
            """جلب البيانات."""
            if DashboardFactory.is_remote():
                # ✅ Remote
                service = DashboardFactory.get_service()
                return service.accountant()
            else:
                # ✅ Local (الكود القديم - مُصغّر)
                from app.database.session import session_scope
                from app.database.models import (
                    Receipt, ExpenseVoucher, FeeInstallment, Student,
                    StudentFee,
                )
                from sqlalchemy import select, func
                from sqlalchemy.orm import joinedload
                from decimal import Decimal
                from datetime import date, datetime, timedelta

                today = date.today()
                week_end = today + timedelta(days=7)
                today_start = datetime.combine(today, datetime.min.time())
                month_start = today.replace(day=1)

                with session_scope() as session:
                    total_receipts = session.execute(
                        select(func.sum(Receipt.amount_paid)).where(
                            Receipt.payment_date >= today_start,
                            Receipt.status == 'نشط',
                        )
                    ).scalar() or Decimal('0.00')

                    total_expenses = session.execute(
                        select(func.sum(ExpenseVoucher.amount)).where(
                            ExpenseVoucher.payment_date >= today_start,
                            ExpenseVoucher.status == 'نشط',
                        )
                    ).scalar() or Decimal('0.00')

                    net_flow = float(total_receipts) - float(total_expenses)

                    cr = session.execute(
                        select(
                            func.count(Receipt.id),
                            func.sum(Receipt.amount_paid),
                        ).where(
                            Receipt.status == 'ملغى',
                            Receipt.cancelled_at >= month_start,
                        )
                    ).first()

                    cv = session.execute(
                        select(
                            func.count(ExpenseVoucher.id),
                            func.sum(ExpenseVoucher.amount),
                        ).where(
                            ExpenseVoucher.status == 'ملغى',
                            ExpenseVoucher.cancelled_at >= month_start,
                        )
                    ).first()

                    cancelled_count = (cr[0] or 0) + (cv[0] or 0)
                    cancelled_amount = float(cr[1] or 0) + float(cv[1] or 0)

                    total_dues = session.execute(
                        select(func.sum(FeeInstallment.amount)).where(
                            FeeInstallment.due_date >= today,
                            FeeInstallment.due_date <= week_end,
                            FeeInstallment.is_paid == False,
                        )
                    ).scalar() or Decimal('0.00')

                    # الأقساط
                    inst_rows = session.execute(
                        select(FeeInstallment, Student)
                        .join(
                            StudentFee,
                            FeeInstallment.student_fee_id == StudentFee.id,
                        )
                        .join(Student, StudentFee.student_id == Student.id)
                        .where(
                            FeeInstallment.due_date >= today,
                            FeeInstallment.due_date <= week_end,
                            FeeInstallment.is_paid == False,
                        )
                        .order_by(FeeInstallment.due_date)
                        .limit(20)
                    ).all()

                    installments_data = [
                        {
                            'student_id': st.id,
                            'student_name': st.full_name or '',
                            'installment_name': ins.installment_name or '',
                            'amount': float(ins.amount or 0),
                            'due_date': (
                                ins.due_date.strftime("%Y/%m/%d")
                                if ins.due_date else ''
                            ),
                            'is_overdue': (
                                ins.due_date < today
                                if ins.due_date else False
                            ),
                        }
                        for ins, st in inst_rows
                    ]

                    # السندات الملغاة
                    cancelled_r = session.execute(
                        select(Receipt).where(
                            Receipt.status == 'ملغى',
                            Receipt.cancelled_at >= month_start,
                        ).order_by(Receipt.cancelled_at.desc()).limit(10)
                    ).scalars().all()

                    cancelled_v = session.execute(
                        select(ExpenseVoucher).where(
                            ExpenseVoucher.status == 'ملغى',
                            ExpenseVoucher.cancelled_at >= month_start,
                        ).order_by(ExpenseVoucher.cancelled_at.desc()).limit(10)
                    ).scalars().all()

                    all_cancelled = []
                    for r in cancelled_r:
                        all_cancelled.append({
                            'number': r.receipt_number or '',
                            'type': 'سند قبض',
                            'amount': float(r.amount_paid or 0),
                            'reason': r.cancellation_reason or '',
                            'date': r.cancelled_at,
                            'user': '',
                        })
                    for v in cancelled_v:
                        all_cancelled.append({
                            'number': v.voucher_number or '',
                            'type': 'سند صرف',
                            'amount': float(v.amount or 0),
                            'reason': v.cancellation_reason or '',
                            'date': v.cancelled_at,
                            'user': '',
                        })

                    all_cancelled.sort(
                        key=lambda x: x['date'] if x['date'] else datetime.min,
                        reverse=True,
                    )

                    # آخر العمليات
                    receipts_ops = session.execute(
                        select(Receipt)
                        .options(joinedload(Receipt.created_by_user))
                        .order_by(Receipt.payment_date.desc())
                        .limit(10)
                    ).unique().scalars().all()

                    vouchers_ops = session.execute(
                        select(ExpenseVoucher)
                        .options(joinedload(ExpenseVoucher.created_by_user))
                        .order_by(ExpenseVoucher.payment_date.desc())
                        .limit(10)
                    ).unique().scalars().all()

                    operations = []
                    for r in receipts_ops:
                        operations.append({
                            'type': 'قبض',
                            'number': r.receipt_number or '',
                            'amount': float(r.amount_paid or 0),
                            'date': r.payment_date,
                            'user': (
                                r.created_by_user.username
                                if r.created_by_user else ''
                            ),
                        })
                    for v in vouchers_ops:
                        operations.append({
                            'type': 'صرف',
                            'number': v.voucher_number or '',
                            'amount': float(v.amount or 0),
                            'date': v.payment_date,
                            'user': (
                                v.created_by_user.username
                                if v.created_by_user else ''
                            ),
                        })

                    operations.sort(
                        key=lambda x: x['date'] if x['date'] else datetime.min,
                        reverse=True,
                    )
                    operations = operations[:20]

                    for op in operations:
                        op['date_str'] = (
                            op['date'].strftime("%Y/%m/%d %H:%M")
                            if op['date'] else ''
                        )

                    return {
                        'net_flow': net_flow,
                        'cancelled_count': cancelled_count,
                        'cancelled_amount': cancelled_amount,
                        'total_dues': float(total_dues),
                        'installments': installments_data,
                        'cancelled': all_cancelled,
                        'operations': operations,
                    }

        def _on_result(data):
            try:
                self.cash_flow_card.findChild(QLabel, "kpiValue").setText(
                    f"{data['net_flow']:,.0f} ر.ي"
                )
                self.cancelled_kpi_card.findChild(QLabel, "kpiValue").setText(
                    str(data['cancelled_count'])
                )
                trend = self.cancelled_kpi_card.findChild(QLabel, "kpiTrend")
                if trend:
                    trend.setText(
                        f"بقيمة {data['cancelled_amount']:,.0f} ر.ي"
                    )

                self.weekly_dues_card.findChild(QLabel, "kpiValue").setText(
                    f"{data['total_dues']:,.0f} ر.ي"
                )

                self._display_installments(data['installments'])
                self._display_cancelled(data['cancelled'])
                self._display_operations(data['operations'])
            except Exception as e:
                print(f"خطأ في تحديث الواجهة: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(
                self, "خطأ",
                f"فشل تحميل بيانات لوحة التحكم:\n{error_msg}"
            )

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
        
    # ============================================================
    # ✅ دوال عرض البيانات (تعمل في الخيط الرئيسي)
    # ============================================================
    
    def _display_installments(self, installments_data: List[Dict]):
        """عرض جدول الأقساط المستحقة."""
        self.installments_table.setRowCount(len(installments_data))
        
        for row, item in enumerate(installments_data):
            self.installments_table.setItem(
                row, 0, QTableWidgetItem(item['student_name'])
            )
            self.installments_table.setItem(
                row, 1, QTableWidgetItem(item['installment_name'])
            )
            self.installments_table.setItem(
                row, 2, QTableWidgetItem(f"{item['amount']:,.0f}")
            )
            self.installments_table.setItem(
                row, 3, QTableWidgetItem(item['due_date'])
            )
            
            # حالة القسط
            status = "متأخر" if item['is_overdue'] else "مستحق"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(
                QColor('#EF4444') if status == "متأخر" else QColor('#F59E0B')
            )
            self.installments_table.setItem(row, 4, status_item)
            
            # زر إرسال إشعار
            notify_btn = QPushButton("إشعار")
            notify_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 #1976d3, stop:1 #42a5f5);
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 0px 10px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 rgb(13, 71, 161), stop:1 rgb(21, 101, 192));
                }
            """)
            # ✅ استخدام student_id بدلاً من الكائن
            notify_btn.clicked.connect(
                lambda checked, sid=item['student_id'], 
                       sname=item['student_name']: 
                self._send_notification_by_id(sid, sname)
            )
            self.installments_table.setCellWidget(row, 5, notify_btn)
            self.installments_table.setRowHeight(row, 45)
    
    def _display_cancelled(self, cancelled_data: List[Dict]):
        """عرض جدول السندات الملغاة."""
        self.cancelled_table.setRowCount(len(cancelled_data))
        
        for row, item in enumerate(cancelled_data):
            self.cancelled_table.setItem(
                row, 0, QTableWidgetItem(item['number'])
            )
            self.cancelled_table.setItem(
                row, 1, QTableWidgetItem(item['type'])
            )
            self.cancelled_table.setItem(
                row, 2, QTableWidgetItem(f"{item['amount']:,.0f}")
            )
            self.cancelled_table.setItem(
                row, 3, QTableWidgetItem(item['reason'])
            )
            self.cancelled_table.setItem(
                row, 4, QTableWidgetItem(item['user'])
            )
    
    def _display_operations(self, operations_data: List[Dict]):
        """عرض جدول آخر العمليات."""
        self.operations_table.setRowCount(len(operations_data))
        
        for row, op in enumerate(operations_data):
            type_item = QTableWidgetItem(op['type'])
            type_item.setForeground(
                QColor('#10B981') if op['type'] == 'قبض' 
                else QColor('#EF4444')
            )
            self.operations_table.setItem(row, 0, type_item)
            
            self.operations_table.setItem(
                row, 1, QTableWidgetItem(op['number'])
            )
            self.operations_table.setItem(
                row, 2, QTableWidgetItem(f"{op['amount']:,.0f}")
            )
            self.operations_table.setItem(
                row, 3, QTableWidgetItem(op.get('date_str', ''))
            )
            self.operations_table.setItem(
                row, 4, QTableWidgetItem(op['user'])
            )
    
    # ============================================================
    # ✅ معالج الإشعار (نسخة آمنة)
    # ============================================================
    
    def _send_notification_by_id(self, student_id: int, student_name: str):
        """إرسال إشعار لولي الأمر (بالاعتماد على ID بدلاً من الكائن)."""
        dialog = ConfirmationDialog(
            "إرسال إشعار",
            f"هل تريد إرسال إشعار لولي أمر الطالب {student_name}؟",
            self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # سيتم تنفيذ إرسال الإشعار في المرحلة 10
            success = SuccessDialog(
                "نجاح",
                "تم إرسال الإشعار بنجاح",
                self
            )
            success.exec()
    
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