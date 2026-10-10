"""
واجهة الإشعارات والتنبيهات - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta
from datetime import datetime

from app.database.session import session_scope
from app.database.models import (
    Notification, NotificationLog, Grade, Section, Parent, Student
)
from app.services.notifications_factory import NotificationsFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    PageHeader, Card, QLineEditPlus, SearchBox, ModernTable, Badge,
    GradientButton, IconButton
)
from app.views.widgets.dialogs import ErrorDialog, ModernDialog
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select, func


class NotificationsPage(QWidget):
    """صفحة الإشعارات - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, 
                 permission_service: Optional[PermissionService] = None, 
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        # ✅ تعريف permission_service (كان مفقوداً)
        self.permission_service = permission_service
        
        # ✅ تخزين البيانات قبل فقدان الجلسة
        self.user_id = user.id if user else None
        self.academic_year_id = academic_year.id if academic_year else None
        
        # ✅ dicts بدلاً من ORM
        self.all_notifications: List[Dict] = []
        self.current_filtered_notifications: List[Dict] = []
        
        # ✅ debounce للبحث
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self.filter_notifications)
        
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
        title = QLabel("الإشعارات والتنبيهات")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("عرض وإدارة الإشعارات")
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
        
        self.search_box = SearchBox("بحث في الإشعارات...")
        self.search_box.textChanged.connect(self._on_search_text_changed)
        filter_layout.addWidget(self.search_box)
        
        filter_layout.addWidget(QLabel("النوع:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems([
            "جميع الأنواع", "حضور", "غياب", "واجبات",
            "سلوك", "نتائج", "رسوم", "عام"
        ])
        self.type_filter.currentIndexChanged.connect(self.filter_notifications)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addStretch()
        
        send_btn = GradientButton("إرسال إشعار", "fa5s.paper-plane")
        send_btn.clicked.connect(self.send_notification)
        filter_layout.addWidget(send_btn)
        
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
        
        self.count_label = QLabel("إجمالي الإشعارات: 0")
        toolbar.addWidget(self.count_label)
        
        toolbar.addStretch()
        
        view_btn = IconButton('fa5s.eye', 'عرض', color='#1976D3')
        view_btn.clicked.connect(self.view_notification)
        toolbar.addWidget(view_btn)
        
        delete_btn = IconButton('fa5s.trash', 'حذف', color='#EF4444')
        delete_btn.clicked.connect(self.delete_notification)
        toolbar.addWidget(delete_btn)
        
        card_layout.addLayout(toolbar)
        
        # الجدول
        self.table = ModernTable()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "العنوان", "النوع", "الوصف", "تاريخ الإنشاء", "الحالة"
        ])
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 80)
        self.table.setColumnWidth(2, 250)
        self.table.setColumnWidth(3, 130)
        self.table.setColumnWidth(4, 80)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.view_notification)
        card_layout.addWidget(self.table)
        
        main_layout.addWidget(table_card)
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_data(self):
        """تحميل الإشعارات - Local أو Remote."""
        if self._is_loading:
            return

        self._is_loading = True
        self.loading_overlay.show_loading("جاري تحميل الإشعارات...")

        def _fetch_data():
            # ✅ Remote
            if NotificationsFactory.is_remote():
                return NotificationsFactory.get_service() \
                    .list_notifications(limit=500)

            # Local (الكود القديم)
            with session_scope() as session:
                notifications = session.execute(
                    select(Notification)
                    .order_by(Notification.created_at.desc())
                    .limit(500)
                ).scalars().all()

                notifications_data = []
                for n in notifications:
                    if getattr(n, 'is_sent', False):
                        status = 'مرسل'
                    elif getattr(n, 'is_scheduled', False):
                        status = 'مجدول'
                    else:
                        status = 'مسودة'

                    message = n.message or ''
                    message_short = (
                        message[:100] + "..."
                        if len(message) > 100 else message
                    )

                    notifications_data.append({
                        'id': n.id,
                        'title': n.title or '',
                        'notification_type': n.notification_type or '',
                        'message': message,
                        'message_short': message_short,
                        'created_at_str': (
                            n.created_at.strftime("%Y/%m/%d %H:%M")
                            if n.created_at else ''
                        ),
                        'sent_at_str': (
                            n.sent_at.strftime("%Y/%m/%d %H:%M")
                            if getattr(n, 'sent_at', None) else ''
                        ),
                        'is_sent': bool(getattr(n, 'is_sent', False)),
                        'is_scheduled': bool(getattr(n, 'is_scheduled', False)),
                        'status_display': status,
                    })

                return notifications_data

        def _on_result(data):
            try:
                self.all_notifications = data
                self.current_filtered_notifications = list(self.all_notifications)
                self.display_notifications(self.all_notifications)
            except Exception as e:
                print(f"خطأ: {str(e)}")
            finally:
                self._is_loading = False
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self._is_loading = False
            self.loading_overlay.hide_loading()
            print(f"فشل التحميل: {error_msg}")
            self.all_notifications = []
            self.current_filtered_notifications = []
            self.display_notifications([])

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)

    # ============================================================
    # ✅ عرض البيانات
    # ============================================================
    
    def display_notifications(self, notifications: List[Dict]):
        """عرض الإشعارات."""
        self.table.setRowCount(len(notifications))
        
        type_colors = {
            'حضور': '#10B981',
            'غياب': '#EF4444',
            'واجبات': '#1976D3',
            'سلوك': '#F59E0B',
            'نتائج': '#42A5F5',
            'رسوم': '#10B981',
            'عام': '#64748B',
        }
        
        for row, notification in enumerate(notifications):
            self.table.setItem(
                row, 0, QTableWidgetItem(notification['title'])
            )
            
            type_item = QTableWidgetItem(notification['notification_type'])
            type_item.setForeground(QColor(
                type_colors.get(notification['notification_type'], '#64748B')
            ))
            self.table.setItem(row, 1, type_item)
            
            self.table.setItem(
                row, 2, QTableWidgetItem(notification['message_short'])
            )
            self.table.setItem(
                row, 3, QTableWidgetItem(notification['created_at_str'])
            )
            
            # الحالة
            status_item = QTableWidgetItem(notification['status_display'])
            if notification['is_sent']:
                status_item.setForeground(QColor('#10B981'))
            elif notification['is_scheduled']:
                status_item.setForeground(QColor('#F59E0B'))
            else:
                status_item.setForeground(QColor('#64748B'))
            self.table.setItem(row, 4, status_item)
            
            self.table.setRowHeight(row, 35)
        
        self.count_label.setText(f"إجمالي الإشعارات: {len(notifications)}")
    
    # ============================================================
    # ✅ الفلترة
    # ============================================================
    
    def _on_search_text_changed(self):
        """عند تغيير نص البحث - debounce."""
        self._search_timer.stop()
        self._search_timer.start()
    
    def filter_notifications(self):
        """تصفية الإشعارات."""
        search_text = (
            self.search_box.text().lower().strip() 
            if self.search_box.text() else ""
        )
        type_filter = self.type_filter.currentText()
        
        filtered = []
        for notification in self.all_notifications:
            # فلتر البحث
            if search_text:
                title = notification['title'].lower()
                message = notification['message'].lower()
                if search_text not in title and search_text not in message:
                    continue
            
            # فلتر النوع
            if type_filter != "جميع الأنواع" and \
               notification['notification_type'] != type_filter:
                continue
            
            filtered.append(notification)
        
        self.current_filtered_notifications = filtered
        self.display_notifications(filtered)
    
    # ============================================================
    # ✅ الحصول على الإشعار المحدد
    # ============================================================
    
    def _get_selected_notification_id(self) -> Optional[int]:
        """الحصول على ID الإشعار المحدد."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
        
        if current_row >= len(self.current_filtered_notifications):
            return None
        
        return self.current_filtered_notifications[current_row]['id']
    
    # ============================================================
    # ✅ عرض التفاصيل
    # ============================================================
    
    def view_notification(self):
        """عرض تفاصيل الإشعار - Local أو Remote."""
        notification_id = self._get_selected_notification_id()
        if not notification_id:
            QMessageBox.warning(self, "تنبيه", "اختر إشعاراً")
            return

        def _fetch():
            if NotificationsFactory.is_remote():
                return NotificationsFactory.get_service() \
                    .get_notification(notification_id)

            with session_scope() as session:
                n = session.get(Notification, notification_id)
                if not n:
                    return None
                if getattr(n, 'is_sent', False):
                    status = 'مرسل'
                elif getattr(n, 'is_scheduled', False):
                    status = 'مجدول'
                else:
                    status = 'مسودة'
                return {
                    'id': n.id,
                    'title': n.title or '',
                    'message': n.message or '',
                    'notification_type': n.notification_type or '',
                    'created_at_str': (
                        n.created_at.strftime("%Y/%m/%d %H:%M")
                        if n.created_at else ''
                    ),
                    'sent_at_str': (
                        n.sent_at.strftime("%Y/%m/%d %H:%M")
                        if getattr(n, 'sent_at', None) else ''
                    ),
                    'status_display': status,
                }

        def _ok(data):
            if not data:
                QMessageBox.warning(self, "تنبيه", "الإشعار غير موجود")
                return
            NotificationDetailsDialog(data, parent=self).exec()

        def _err(m):
            QMessageBox.critical(self, "خطأ", f"فشل: {m}")

        run_async(_fetch, on_result=_ok, on_error=_err)

    # ============================================================
    # ✅ حذف الإشعار
    # ============================================================
    
    def delete_notification(self):
        """حذف إشعار - Local أو Remote."""
        notification_id = self._get_selected_notification_id()
        if not notification_id:
            QMessageBox.warning(self, "تنبيه", "اختر إشعاراً")
            return

        notification = next(
            (n for n in self.current_filtered_notifications
             if n['id'] == notification_id),
            None
        )
        if not notification:
            return

        reply = QMessageBox.question(
            self, "حذف إشعار",
            f"حذف: {notification['title']}؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        def _do():
            if NotificationsFactory.is_remote():
                NotificationsFactory.get_service() \
                    .delete_notification(notification_id)
            else:
                with session_scope() as session:
                    n = session.get(Notification, notification_id)
                    if n:
                        logs = session.query(NotificationLog).filter(
                            NotificationLog.notification_id == notification_id
                        ).all()
                        for log in logs:
                            session.delete(log)
                        session.delete(n)
                        session.commit()

        def _ok(_):
            QMessageBox.information(self, "نجاح", "تم الحذف")
            self.load_data()

        def _err(m):
            QMessageBox.critical(self, "خطأ", f"فشل: {m}")

        run_async(_do, on_result=_ok, on_error=_err)
        
    # ============================================================
    # ✅ إرسال إشعار جديد
    # ============================================================
    
    def send_notification(self):
        """فتح نافذة إرسال إشعار."""
        dialog = SendNotificationDialog(
            self.user_id, self.academic_year_id, parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            QMessageBox.information(self, "نجاح", "تم إرسال الإشعار بنجاح")
    
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
# ✅ نافذة تفاصيل الإشعار (مع dicts)
# ============================================================

class NotificationDetailsDialog(ModernDialog):
    """نافذة تفاصيل الإشعار."""
    
    def __init__(self, notification_data: Dict, parent=None):
        super().__init__(
            "تفاصيل الإشعار",
            "fa5s.bell",
            parent,
            width=450,
            height=300
        )
        
        # ✅ dict بدلاً من ORM
        d = notification_data
        
        title_label = QLabel(d.get('title', ''))
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #0F172A;"
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_widget(title_label)
        
        type_badge = Badge(d.get('notification_type', ''), '#1976D3')
        self.add_widget(type_badge)
        
        message_label = QLabel(d.get('message', ''))
        message_label.setWordWrap(True)
        message_label.setStyleSheet(
            "color: #475569; font-size: 13px; line-height: 1.6;"
        )
        self.add_widget(message_label)
        
        # ✅ معلومات إضافية
        info_text = (
            f"<b>تاريخ الإنشاء:</b> {d.get('created_at_str', '')}<br/>"
            f"<b>الحالة:</b> {d.get('status_display', '')}<br/>"
        )
        if d.get('sent_at_str'):
            info_text += f"<b>تاريخ الإرسال:</b> {d['sent_at_str']}<br/>"
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #64748B; font-size: 11px;")
        self.add_widget(info_label)
        
        self.add_button("إغلاق", self.accept, "primary")


# ============================================================
# ✅ نافذة إرسال إشعار (مع تحميل غير متزامن)
# ============================================================

class SendNotificationDialog(ModernDialog):
    """نافذة إرسال إشعار جماعي مع خيارات ديناميكية."""
    
    def __init__(self, user_id: int, academic_year_id: int, parent=None):
        super().__init__(
            "إرسال إشعار جماعي",
            "fa5s.paper-plane",
            parent,
            width=550,
            height=700
        )
        
        # ✅ تخزين IDs فقط
        self.user_id = user_id
        self.academic_year_id = academic_year_id
        
        # ✅ dicts
        self.grades_data: List[Dict] = []
        self.sections_data: List[Dict] = []
        self.parents_data: List[Dict] = []
        self.selected_parent_ids: List[int] = []
        
        # ✅ debounce للبحث
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        
        # ✅ LoadingOverlay
        self.dialog_loading = LoadingOverlay(self)
        
        # ✅ منع الإرسال قبل التحميل
        self._is_loaded = False
        
        self.setup_ui()
        
        # ✅ تحميل أولي
        QTimer.singleShot(100, self._load_initial_data)
    
    def setup_ui(self):
        """إعداد النموذج."""
        # الفئة المستهدفة
        self.add_widget(self._create_label("الفئة المستهدفة:"))
        self.target_type_combo = QComboBox()
        self.target_type_combo.addItems([
            "جميع أولياء الأمور",
            "أولياء أمور صف معين",
            "أولياء أمور شعبة معينة",
            "أولياء أمور الطلاب المتعثرين في الرسوم",
            "أولياء أمور الطلاب الغائبين",
            "تحديد يدوي من القائمة",
        ])
        self.target_type_combo.currentIndexChanged.connect(
            self._on_target_type_changed
        )
        self.add_widget(self.target_type_combo)
        
        # منطقة الخيارات الديناميكية
        self.options_widget = QWidget()
        self.options_layout = QVBoxLayout(self.options_widget)
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        self.options_layout.setSpacing(10)
        self.add_widget(self.options_widget)
        
        # العنوان
        self.add_widget(self._create_label("عنوان الإشعار:"))
        self.title_input = QLineEditPlus("أدخل عنوان الإشعار")
        self.add_widget(self.title_input)
        
        # نص الإشعار
        self.add_widget(self._create_label("نص الإشعار:"))
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("أدخل نص الإشعار...")
        self.message_input.setMaximumHeight(100)
        self.add_widget(self.message_input)
        
        # وقت الإرسال
        self.add_widget(self._create_label("وقت الإرسال:"))
        timing_layout = QHBoxLayout()
        
        self.send_now_radio = QRadioButton("إرسال فوري")
        self.send_now_radio.setChecked(True)
        timing_layout.addWidget(self.send_now_radio)
        
        self.schedule_radio = QRadioButton("جدولة")
        timing_layout.addWidget(self.schedule_radio)
        
        self.schedule_datetime = QDateTimeEdit()
        self.schedule_datetime.setCalendarPopup(True)
        self.schedule_datetime.setDateTime(
            QDateTime.currentDateTime().addDays(1)
        )
        self.schedule_datetime.setEnabled(False)
        timing_layout.addWidget(self.schedule_datetime)
        
        timing_layout.addStretch()
        
        self.send_now_radio.toggled.connect(
            lambda checked: self.schedule_datetime.setEnabled(not checked)
        )
        
        self.add_widget(self._create_widget(timing_layout))
        
        # الأزرار
        self.add_button("إلغاء", self.reject, "default")
        self.add_button("إرسال", self.send_notification, "primary")
    
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
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def _load_initial_data(self):
        """تحميل الصفوف - Local أو Remote."""
        self.dialog_loading.show_loading("جاري التحميل...")

        def _fetch_data():
            if NotificationsFactory.is_remote():
                return NotificationsFactory.get_service().list_grades()
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
                self.grades_data = data
                self._is_loaded = True
            finally:
                self.dialog_loading.hide_loading()

        def _on_error(error_msg):
            self.dialog_loading.hide_loading()
            print(f"فشل التحميل: {error_msg}")

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)

    def _clear_options(self):
        """مسح الخيارات الديناميكية."""
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _on_target_type_changed(self):
        """عند تغيير الفئة المستهدفة."""
        self._clear_options()
        
        target = self.target_type_combo.currentText()
        
        if target == "أولياء أمور صف معين":
            self._create_grade_selector()
        elif target == "أولياء أمور شعبة معينة":
            self._create_grade_section_selector()
        elif target == "تحديد يدوي من القائمة":
            self._create_parent_selector()
    
    def _create_grade_selector(self):
        """إنشاء محدد الصف."""
        self.options_layout.addWidget(self._create_label("اختر الصف:"))
        
        self.grade_combo = QComboBox()
        for grade in self.grades_data:
            self.grade_combo.addItem(grade['name'], grade['id'])
        
        self.options_layout.addWidget(self.grade_combo)
    
    def _create_grade_section_selector(self):
        """إنشاء محدد الصف والشعبة."""
        self.options_layout.addWidget(self._create_label("اختر الصف:"))
        
        self.grade_combo = QComboBox()
        for grade in self.grades_data:
            self.grade_combo.addItem(grade['name'], grade['id'])
        self.grade_combo.currentIndexChanged.connect(self._load_sections)
        
        self.options_layout.addWidget(self.grade_combo)
        
        self.options_layout.addWidget(self._create_label("اختر الشعبة:"))
        
        self.section_combo = QComboBox()
        self.options_layout.addWidget(self.section_combo)
        
        # ✅ تحميل الشعب الأولية
        self._load_sections()
    
    def _create_parent_selector(self):
        """إنشاء محدد أولياء الأمور."""
        self.options_layout.addWidget(
            self._create_label("اختر أولياء الأمور:")
        )
        
        self.parents_list = QListWidget()
        self.parents_list.setMaximumHeight(150)
        self.parents_list.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )
        self.parents_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #F1F5F9;
            }
        """)
        
        self.options_layout.addWidget(self.parents_list)
        
        # ✅ تحميل أولياء الأمور (Async)
        self._load_parents()
    
    def _load_sections(self):
        """تحميل الشعب حسب الصف - Local أو Remote."""
        if not hasattr(self, 'section_combo'):
            return

        grade_id = self.grade_combo.currentData()
        if not grade_id:
            return

        def _fetch_data():
            if NotificationsFactory.is_remote():
                return NotificationsFactory.get_service() \
                    .list_sections(grade_id)
            with session_scope() as session:
                sections = session.execute(
                    select(Section)
                    .where(Section.grade_id == grade_id)
                    .order_by(Section.section_name)
                ).scalars().all()
                return [
                    {'id': s.id, 'name': s.section_name or ''}
                    for s in sections
                ]

        def _on_result(data):
            try:
                self.section_combo.blockSignals(True)
                self.section_combo.clear()
                for section in data:
                    self.section_combo.addItem(
                        section['name'], section['id']
                    )
                self.section_combo.blockSignals(False)
            except Exception as e:
                print(f"خطأ: {str(e)}")

        run_async(_fetch_data, on_result=_on_result)

    def _load_parents(self):
        """تحميل أولياء الأمور - Local أو Remote."""
        def _fetch_data():
            if NotificationsFactory.is_remote():
                return NotificationsFactory.get_service() \
                    .list_parents(limit=50)
            with session_scope() as session:
                parents = session.execute(
                    select(Parent).filter(
                        Parent.deleted_at.is_(None)
                    ).order_by(Parent.full_name).limit(50)
                ).scalars().all()
                return [
                    {
                        'id': p.id,
                        'full_name': p.full_name or '',
                        'phone': p.primary_phone or '',
                    }
                    for p in parents
                ]

        def _on_result(data):
            try:
                self.parents_data = data
                self.parents_list.clear()
                for parent in data:
                    item = QListWidgetItem(
                        f"{parent['full_name']} - {parent['phone']}"
                    )
                    item.setData(Qt.ItemDataRole.UserRole, parent['id'])
                    self.parents_list.addItem(item)
            except Exception as e:
                print(f"خطأ: {str(e)}")

        run_async(_fetch_data, on_result=_on_result)

    # ============================================================
    # ✅ تحديد المستهدفين
    # ============================================================
    
    def _resolve_target_type(self) -> tuple:
        """يُرجع (target_type, extra_params)."""
        target = self.target_type_combo.currentText()

        if target == "جميع أولياء الأمور":
            return 'all', {}
        elif target == "أولياء أمور صف معين":
            return 'by_grade', {
                'grade_id': self.grade_combo.currentData()
            }
        elif target == "أولياء أمور شعبة معينة":
            return 'by_section', {
                'section_id': self.section_combo.currentData()
            }
        elif target == "تحديد يدوي من القائمة":
            ids = [
                item.data(Qt.ItemDataRole.UserRole)
                for item in self.parents_list.selectedItems()
            ]
            return 'by_parent_ids', {'parent_ids': ids}
        else:
            # للمتعثرين/الغائبين - fallback: all
            return 'all', {}

    # ============================================================
    # ✅ الإرسال (Async)
    # ============================================================
    
    def send_notification(self):
        """إرسال الإشعار - Local أو Remote."""
        if not self._is_loaded:
            QMessageBox.warning(self, "تنبيه", "انتظر التحميل")
            return
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "تنبيه", "أدخل العنوان")
            return
        if not self.message_input.toPlainText().strip():
            QMessageBox.warning(self, "تنبيه", "أدخل النص")
            return

        target_type, extra = self._resolve_target_type()

        title = self.title_input.text().strip()
        message = self.message_input.toPlainText().strip()
        scheduled_at = None
        if self.schedule_radio.isChecked():
            dt = self.schedule_datetime.dateTime().toPython()
            scheduled_at = dt.isoformat()

        self.dialog_loading.show_loading("جاري التحضير...")

        def _send():
            # ✅ Remote
            if NotificationsFactory.is_remote():
                service = NotificationsFactory.get_service()
                # 1. حلّ المستهدفين
                resolve_payload = {'target_type': target_type}
                resolve_payload.update(extra)
                resolved = service.resolve_targets(resolve_payload)
                count = resolved.get('count', 0)
                if count == 0:
                    raise Exception("لا يوجد مستهدفون")

                # 2. أرسل
                send_payload = {
                    'title': title,
                    'message': message,
                    'notification_type': 'عام',
                    'target_type': target_type,
                    'scheduled_at': scheduled_at,
                }
                send_payload.update(extra)
                result = service.send_notification(send_payload)
                return result.get('sent_count', count)

            # Local
            from app.database.session import session_scope
            from app.database.models import (
                Notification, NotificationLog, Parent, Student
            )
            with session_scope() as session:
                # حلّ المستهدفين
                parent_ids = []
                if target_type == 'all':
                    rows = session.execute(
                        select(Parent.id).filter(
                            Parent.deleted_at.is_(None)
                        )
                    ).scalars().all()
                    parent_ids = list(rows)
                elif target_type == 'by_grade':
                    gid = extra.get('grade_id')
                    rows = session.execute(
                        select(Student.parent_id).filter(
                            Student.grade_id == gid,
                            Student.parent_id.isnot(None)
                        ).distinct()
                    ).scalars().all()
                    parent_ids = [x for x in rows if x]
                elif target_type == 'by_section':
                    sid = extra.get('section_id')
                    rows = session.execute(
                        select(Student.parent_id).filter(
                            Student.section_id == sid,
                            Student.parent_id.isnot(None)
                        ).distinct()
                    ).scalars().all()
                    parent_ids = [x for x in rows if x]
                elif target_type == 'by_parent_ids':
                    parent_ids = list(set(extra.get('parent_ids', [])))

                if not parent_ids:
                    raise Exception("لا يوجد مستهدفون")

                # أنشئ الإشعار
                is_sent = scheduled_at is None
                is_scheduled = scheduled_at is not None
                scheduled_dt = None
                if scheduled_at:
                    try:
                        scheduled_dt = datetime.fromisoformat(scheduled_at)
                    except Exception:
                        pass

                notif = Notification(
                    title=title,
                    message=message,
                    notification_type='عام',
                    is_sent=is_sent,
                    is_scheduled=is_scheduled,
                    sent_at=datetime.now() if is_sent else None,
                )
                session.add(notif)
                session.flush()

                for pid in parent_ids:
                    session.add(NotificationLog(
                        notification_id=notif.id,
                        parent_id=pid,
                        is_read=False,
                    ))
                session.commit()
                return len(parent_ids)

        def _on_result(count):
            self.dialog_loading.hide_loading()
            self.accept()

        def _on_error(error_msg):
            self.dialog_loading.hide_loading()
            QMessageBox.critical(
                self, "خطأ", f"فشل الإرسال:\n{error_msg}"
            )

        run_async(_send, on_result=_on_result, on_error=_on_error)

    # ============================================================
    # ✅ الأحداث
    # ============================================================
    
    def resizeEvent(self, event):
        """تحديث حجم طبقة التحميل."""
        super().resizeEvent(event)
        if hasattr(self, 'dialog_loading'):
            self.dialog_loading.setGeometry(self.rect())