"""
واجهة سجل العمليات - Audit Log - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta
from datetime import date, datetime, timedelta

from app.database.session import session_scope
from app.database.models import SystemAuditLog, User
from app.services.audit_log_factory import AuditLogFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    PageHeader, Card, QDateEditEN, SearchBox, ModernTable, Badge,
    GradientButton, IconButton
)
from app.views.widgets.dialogs import ErrorDialog, ModernDialog
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload


class AuditLogPage(QWidget):
    """صفحة سجل العمليات - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, 
                 permission_service: Optional[PermissionService] = None, 
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ dicts بدلاً من ORM
        self.all_logs: List[Dict] = []
        self.current_filtered_logs: List[Dict] = []
        
        # ✅ debounce للبحث
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self.filter_logs)
        
        # ✅ منع التحميل المزدوج
        self._is_loading = False
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل أولي
        QTimer.singleShot(100, self.load_data)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)

        # رأس الصفحة
        title = QLabel("سجل العمليات")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("مراقبة وتتبع جميع عمليات النظام")
        subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
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
        
        # بحث
        self.search_box = SearchBox("بحث في السجل...")
        self.search_box.textChanged.connect(self._on_search_text_changed)
        filter_layout.addWidget(self.search_box)
        
        # فلتر المستخدم
        filter_layout.addWidget(QLabel("المستخدم:"))
        self.user_filter = QComboBox()
        self.user_filter.addItem("جميع المستخدمين", None)
        self.user_filter.currentIndexChanged.connect(self.filter_logs)
        filter_layout.addWidget(self.user_filter)
        
        # فلتر نوع العملية
        filter_layout.addWidget(QLabel("نوع العملية:"))
        self.operation_filter = QComboBox()
        self.operation_filter.addItems([
            "جميع العمليات", "إضافة", "تعديل", "حذف",
            "تسجيل دخول", "تسجيل خروج", "إلغاء"
        ])
        self.operation_filter.currentIndexChanged.connect(self.filter_logs)
        filter_layout.addWidget(self.operation_filter)
        
        # فلتر الوحدة
        filter_layout.addWidget(QLabel("الوحدة:"))
        self.module_filter = QComboBox()
        self.module_filter.addItem("جميع الوحدات", None)
        self.module_filter.currentIndexChanged.connect(self.filter_logs)
        filter_layout.addWidget(self.module_filter)
        
        # فلتر التاريخ
        filter_layout.addWidget(QLabel("من:"))
        self.date_from = QDateEditEN(QDate.currentDate().addDays(-7))
        self.date_from.dateChanged.connect(self.filter_logs)
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("إلى:"))
        self.date_to = QDateEditEN()
        self.date_to.dateChanged.connect(self.filter_logs)
        filter_layout.addWidget(self.date_to)
        
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
        
        self.count_label = QLabel("إجمالي السجلات: 0")
        self.count_label.setObjectName("count_label")
        toolbar.addWidget(self.count_label)
        
        toolbar.addStretch()
        
        # أزرار
        view_btn = IconButton('fa5s.eye', "عرض التفاصيل", color='#1976D3')
        view_btn.clicked.connect(self.view_details)
        toolbar.addWidget(view_btn)
        
        # ✅ تفعيل زر التصدير
        export_btn = IconButton('fa5s.file-export', "تصدير", color='#10B981')
        export_btn.clicked.connect(self.export_logs)
        toolbar.addWidget(export_btn)
        
        # ✅ تفعيل زر الطباعة
        print_btn = IconButton('fa5s.print', "طباعة", color='#F59E0B')
        print_btn.clicked.connect(self.print_logs)
        toolbar.addWidget(print_btn)
        
        card_layout.addLayout(toolbar)
        
        # الجدول
        self.table = ModernTable()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "التاريخ والوقت", "المستخدم", "نوع العملية", "الوحدة",
            "رقم السجل", "الوصف", "عنوان IP", "الجهاز"
        ])
        self.table.setColumnWidth(0, 130)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 70)
        self.table.setColumnWidth(5, 200)
        self.table.setColumnWidth(6, 100)
        self.table.setColumnWidth(7, 100)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.view_details)
        card_layout.addWidget(self.table)
        
        main_layout.addWidget(table_card)
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_data(self):
        """تحميل البيانات - Local أو Remote."""
        if self._is_loading:
            return

        self._is_loading = True
        self.loading_overlay.show_loading("جاري تحميل السجل...")

        def _fetch_data():
            # ✅ Remote
            if AuditLogFactory.is_remote():
                service = AuditLogFactory.get_service()
                return service.list_logs(limit=10000)

            # Local (الكود القديم)
            with session_scope() as session:
                # المستخدمون
                users = session.execute(
                    select(User).order_by(User.username)
                ).scalars().all()
                users_data = [
                    {'id': u.id, 'username': u.username or ''}
                    for u in users
                ]

                # الوحدات الفريدة
                modules = session.execute(
                    select(SystemAuditLog.module_name)
                    .distinct()
                    .order_by(SystemAuditLog.module_name)
                ).scalars().all()
                modules_data = [m for m in modules if m]

                # السجلات
                logs = session.execute(
                    select(SystemAuditLog)
                    .options(joinedload(SystemAuditLog.user))
                    .order_by(SystemAuditLog.created_at.desc())
                    .limit(10000)
                ).unique().scalars().all()

                logs_data = []
                for log in logs:
                    try:
                        display_operation = log.display_operation
                    except Exception:
                        op_map = {
                            'create': 'إضافة', 'update': 'تعديل',
                            'delete': 'حذف', 'login': 'تسجيل دخول',
                            'logout': 'تسجيل خروج', 'cancel': 'إلغاء',
                        }
                        display_operation = op_map.get(
                            log.operation_type, log.operation_type or ''
                        )

                    logs_data.append({
                        'id': log.id,
                        'user_id': log.user_id,
                        'username': (
                            log.user.username if log.user else 'غير معروف'
                        ),
                        'display_operation': display_operation,
                        'operation_type': log.operation_type or '',
                        'module_name': log.module_name or '',
                        'record_id': log.record_id,
                        'old_values': log.old_values or '',
                        'new_values': log.new_values or '',
                        'ip_address': log.ip_address or '',
                        'device_name': log.device_name or '',
                        'created_at_str': (
                            log.created_at.strftime("%Y/%m/%d %H:%M:%S")
                            if log.created_at else ''
                        ),
                        'created_at_date': (
                            log.created_at.date()
                            if log.created_at else None
                        ),
                    })

                return {
                    'users': users_data,
                    'modules': modules_data,
                    'logs': logs_data,
                }

        def _on_result(data):
            try:
                # فلتر المستخدمين
                self.user_filter.blockSignals(True)
                self.user_filter.clear()
                self.user_filter.addItem("جميع المستخدمين", None)
                for u in data['users']:
                    self.user_filter.addItem(u['username'], u['id'])
                self.user_filter.blockSignals(False)

                # فلتر الوحدات
                self.module_filter.blockSignals(True)
                self.module_filter.clear()
                self.module_filter.addItem("جميع الوحدات", None)
                for m in data['modules']:
                    self.module_filter.addItem(m, m)
                self.module_filter.blockSignals(False)

                # السجلات
                self.all_logs = data['logs']
                self.current_filtered_logs = list(self.all_logs)
                self.display_logs(self.all_logs)
            except Exception as e:
                print(f"خطأ: {str(e)}")
            finally:
                self._is_loading = False
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self._is_loading = False
            self.loading_overlay.hide_loading()
            ErrorDialog("خطأ", f"فشل التحميل:\n{error_msg}", self).exec()

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)

    # ============================================================
    # ✅ عرض البيانات
    # ============================================================
    
    def display_logs(self, logs: List[Dict]):
        """عرض السجلات."""
        self.table.setRowCount(len(logs))
        
        operation_colors = {
            'إضافة': '#10B981',
            'تعديل': '#1976D3',
            'حذف': '#EF4444',
            'تسجيل دخول': '#10B981',
            'تسجيل خروج': '#F59E0B',
            'إلغاء': '#EF4444',
        }
        
        for row, log in enumerate(logs):
            # التاريخ
            self.table.setItem(
                row, 0, QTableWidgetItem(log['created_at_str'])
            )
            
            # المستخدم
            self.table.setItem(
                row, 1, QTableWidgetItem(log['username'])
            )
            
            # نوع العملية
            operation_item = QTableWidgetItem(log['display_operation'])
            operation_item.setForeground(QColor(
                operation_colors.get(log['display_operation'], '#64748B')
            ))
            self.table.setItem(row, 2, operation_item)
            
            # الوحدة
            self.table.setItem(
                row, 3, QTableWidgetItem(log['module_name'])
            )
            
            # رقم السجل
            self.table.setItem(
                row, 4, 
                QTableWidgetItem(str(log['record_id'] or ""))
            )
            
            # الوصف (مختصر)
            description = ""
            if log['old_values']:
                old_short = log['old_values'][:50]
                description += f"قبل: {old_short}... "
            if log['new_values']:
                new_short = log['new_values'][:50]
                description += f"بعد: {new_short}..."
            self.table.setItem(
                row, 5, QTableWidgetItem(description)
            )
            
            # IP
            self.table.setItem(
                row, 6, QTableWidgetItem(log['ip_address'])
            )
            
            # الجهاز
            self.table.setItem(
                row, 7, QTableWidgetItem(log['device_name'])
            )

            self.table.setRowHeight(row, 35)
        
        self.count_label.setText(f"إجمالي السجلات: {len(logs)}")
    
    # ============================================================
    # ✅ الفلترة
    # ============================================================
    
    def _on_search_text_changed(self):
        """عند تغيير نص البحث - debounce."""
        self._search_timer.stop()
        self._search_timer.start()
    
    def filter_logs(self):
        """تصفية السجلات."""
        search_text = self.search_box.text().lower().strip()
        user_id = self.user_filter.currentData()
        operation = self.operation_filter.currentText()
        module = self.module_filter.currentData()
        date_from = self.date_from.date().toPython()
        date_to = self.date_to.date().toPython()
        
        filtered = []
        for log in self.all_logs:
            # فلتر البحث
            if search_text:
                username = log['username'].lower()
                module_name = log['module_name'].lower()
                op_name = log['display_operation'].lower()
                
                if search_text not in username and \
                   search_text not in module_name and \
                   search_text not in op_name:
                    continue
            
            # فلتر المستخدم
            if user_id and log['user_id'] != user_id:
                continue
            
            # فلتر نوع العملية
            if operation != "جميع العمليات" and \
               log['display_operation'] != operation:
                continue
            
            # فلتر الوحدة
            if module and log['module_name'] != module:
                continue
            
            # فلتر التاريخ
            log_date = log['created_at_date']
            if log_date:
                # ✅ دعم str (من JSON) و date (من Local)
                if isinstance(log_date, str):
                    try:
                        log_date = date.fromisoformat(log_date)
                    except Exception:
                        log_date = None
                if log_date and (log_date < date_from or log_date > date_to):
                    continue
            
            filtered.append(log)
        
        self.current_filtered_logs = filtered
        self.display_logs(filtered)
    
    # ============================================================
    # ✅ عرض التفاصيل
    # ============================================================
    
    def view_details(self):
        """عرض تفاصيل السجل."""
        # ✅ استخدام current_filtered_logs بدلاً من all_logs
        current_row = self.table.currentRow()
        if current_row < 0:
            ErrorDialog("تنبيه", "يرجى اختيار سجل", self).exec()
            return
        
        if current_row >= len(self.current_filtered_logs):
            ErrorDialog("تنبيه", "السجل غير موجود", self).exec()
            return
        
        log = self.current_filtered_logs[current_row]
        
        dialog = AuditLogDetailsDialog(log, parent=self)
        dialog.exec()
    
    # ============================================================
    # ✅ التصدير
    # ============================================================
    
    def export_logs(self):
        """تصدير السجلات إلى ملف Excel/CSV."""
        if not self.current_filtered_logs:
            ErrorDialog(
                "تنبيه",
                "لا توجد سجلات للتصدير",
                self
            ).exec()
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "حفظ التقرير",
            f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    "التاريخ والوقت", "المستخدم", "نوع العملية",
                    "الوحدة", "رقم السجل", "عنوان IP", "الجهاز"
                ])
                
                # Data
                for log in self.current_filtered_logs:
                    writer.writerow([
                        log['created_at_str'],
                        log['username'],
                        log['display_operation'],
                        log['module_name'],
                        str(log['record_id'] or ''),
                        log['ip_address'],
                        log['device_name'],
                    ])
            
            QMessageBox.information(
                self, "نجاح",
                f"تم تصدير {len(self.current_filtered_logs)} سجل بنجاح\n\n"
                f"📁 {file_path}"
            )
        except Exception as e:
            ErrorDialog(
                "خطأ",
                f"فشل التصدير:\n{str(e)}",
                self
            ).exec()
    
    # ============================================================
    # ✅ الطباعة
    # ============================================================
    
    def print_logs(self):
        """طباعة السجلات."""
        if self.permission_service and not self.permission_service.can_print("الإعدادات"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للطباعة في سجل العمليات"
            )
            return
        
        if not self.current_filtered_logs:
            ErrorDialog(
                "تنبيه",
                "لا توجد سجلات للطباعة",
                self
            ).exec()
            return
        
        QMessageBox.information(
            self, "طباعة",
            f"سيتم تنفيذ طباعة {len(self.current_filtered_logs)} سجل\n"
            "في مرحلة التقارير"
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
# ✅ نافذة تفاصيل سجل (مع dicts)
# ============================================================

class AuditLogDetailsDialog(ModernDialog):
    """نافذة تفاصيل سجل."""
    
    def __init__(self, log_data: Dict, parent=None):
        super().__init__(
            "تفاصيل العملية",
            "fa5s.history",
            parent,
            width=500,
            height=600
        )
        
        # ✅ dict بدلاً من ORM
        d = log_data
        
        # عرض التفاصيل
        details_widget = QWidget()
        details_layout = QGridLayout(details_widget)
        details_layout.setSpacing(10)
        
        details = [
            ("التاريخ:", d.get('created_at_str', '')),
            ("المستخدم:", d.get('username', 'غير معروف')),
            ("نوع العملية:", d.get('display_operation', '')),
            ("الوحدة:", d.get('module_name', '')),
            ("رقم السجل:", str(d.get('record_id') or '')),
            ("عنوان IP:", d.get('ip_address', '')),
            ("الجهاز:", d.get('device_name', '')),
        ]
        
        for row, (label, value) in enumerate(details):
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #64748B; font-weight: 600;")
            details_layout.addWidget(label_widget, row, 0)
            
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #0F172A; font-weight: 500;")
            value_widget.setWordWrap(True)
            details_layout.addWidget(value_widget, row, 1)
        
        self.add_widget(details_widget)
        
        # القيم القديمة والجديدة
        old_values = d.get('old_values', '')
        if old_values:
            self.add_widget(self._create_label("القيم القديمة:"))
            old_text = QTextEdit()
            old_text.setText(old_values)
            old_text.setReadOnly(True)
            old_text.setMaximumHeight(60)
            self.add_widget(old_text)
        
        new_values = d.get('new_values', '')
        if new_values:
            self.add_widget(self._create_label("القيم الجديدة:"))
            new_text = QTextEdit()
            new_text.setText(new_values)
            new_text.setReadOnly(True)
            new_text.setMaximumHeight(60)
            self.add_widget(new_text)
        
        self.add_button("إغلاق", self.accept, "primary")
    
    def _create_label(self, text: str) -> QLabel:
        """إنشاء تسمية."""
        label = QLabel(text)
        label.setStyleSheet(
            "color: #475569; font-weight: 600; font-size: 12px;"
        )
        return label