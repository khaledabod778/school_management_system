"""
واجهة إرسال الإشعارات الجماعية.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional
import qtawesome as qta
from datetime import datetime

from app.database.session import session_scope
from app.database.models import Parent, Grade, Section, Student
from app.services.notification_service import NotificationService
from sqlalchemy import select

from app.views.widgets.custom_widgets import GradientButton, QLineEditPlus


class BulkNotificationsPage(QWidget):
    """صفحة إرسال الإشعارات الجماعية."""
    
    def __init__(self, user, academic_year, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)
        
        title = QLabel("إرسال الإشعارات الجماعية")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        # الفئة المستهدفة
        target_card = QFrame()
        target_card.setObjectName("targetCard")
        target_card.setStyleSheet("""
            QFrame#targetCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 10px 15px;
            }
        """)
        
        target_layout = QVBoxLayout(target_card)
        
        target_title = QLabel("الفئة المستهدفة")
        target_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0F172A; padding-bottom: 10px;")
        target_layout.addWidget(target_title)
        
        self.target_combo = QComboBox()
        self.target_combo.addItems([
            "جميع أولياء الأمور",
            "أولياء أمور صف معين",
            "أولياء أمور شعبة معينة",
            "أولياء أمور الطلاب المتعثرين في الرسوم",
            "أولياء أمور الطلاب الغائبين",
        ])
        target_layout.addWidget(self.target_combo)
        
        main_layout.addWidget(target_card)
        
        # محتوى الإشعار
        content_card = QFrame()
        content_card.setObjectName("contentCard")
        content_card.setStyleSheet("""
            QFrame#contentCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 10px 15px;
            }
        """)
        
        content_layout = QVBoxLayout(content_card)
        
        content_title = QLabel("محتوى الإشعار")
        content_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0F172A; padding-bottom: 10px;")
        content_layout.addWidget(content_title)
        
        content_layout.addWidget(QLabel("عنوان الإشعار:"))
        self.title_input = QLineEditPlus("أدخل عنوان الإشعار")
        content_layout.addWidget(self.title_input)
        
        content_layout.addWidget(QLabel(""))
        content_layout.addWidget(QLabel("نص الإشعار:"))
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("أدخل نص الإشعار...")
        self.message_input.setMaximumHeight(120)
        content_layout.addWidget(self.message_input)
        
        content_layout.addWidget(QLabel(""))
        # وقت الإرسال
        timing_layout = QHBoxLayout()
        
        self.send_now_radio = QRadioButton("إرسال فوري")
        self.send_now_radio.setChecked(True)
        timing_layout.addWidget(self.send_now_radio)
        
        self.schedule_radio = QRadioButton("جدولة")
        timing_layout.addWidget(self.schedule_radio)
        
        self.schedule_datetime = QDateTimeEdit()
        self.schedule_datetime.setCalendarPopup(True)
        self.schedule_datetime.setDateTime(QDateTime.currentDateTime().addDays(1))
        self.schedule_datetime.setEnabled(False)
        timing_layout.addWidget(self.schedule_datetime)
        
        timing_layout.addStretch()
        
        self.send_now_radio.toggled.connect(
            lambda checked: self.schedule_datetime.setEnabled(not checked)
        )
        
        content_layout.addLayout(timing_layout)
        
        main_layout.addWidget(content_card)
        
        # أزرار
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        preview_btn = QPushButton("معاينة")
        preview_btn.setIcon(qta.icon('fa5s.eye'))
        preview_btn.setStyleSheet("""
            QPushButton {
                background: #EEF2FF;
                color: #0D47A1;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
            }
        """)
        preview_btn.clicked.connect(self.preview_notification)
        buttons_layout.addWidget(preview_btn)
        
        send_btn = GradientButton("إرسال", 'fa5s.paper-plane')
        send_btn.clicked.connect(self.send_notification)
        buttons_layout.addWidget(send_btn)
        
        main_layout.addLayout(buttons_layout)
        
        main_layout.addStretch()
    
    def load_data(self):
        """تحميل البيانات."""
        pass
    
    def preview_notification(self):
        """معاينة الإشعار."""
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال عنوان الإشعار")
            return
        
        preview = QMessageBox(self)
        preview.setIcon(QMessageBox.Icon.Information)
        preview.setWindowTitle("معاينة الإشعار")
        preview.setText(f"العنوان: {self.title_input.text()}\n\n")
        preview.setInformativeText(self.message_input.toPlainText())
        preview.exec()
    
    def send_notification(self):
        """إرسال الإشعار."""
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال عنوان الإشعار")
            return
        
        if not self.message_input.toPlainText().strip():
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال نص الإشعار")
            return
        
        reply = QMessageBox.question(
            self, "تأكيد",
            "هل تريد إرسال هذا الإشعار؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                service = NotificationService(self.user)
                
                scheduled_at = None
                if self.schedule_radio.isChecked():
                    scheduled_at = self.schedule_datetime.dateTime().toPython()
                
                service.create_notification(
                    title=self.title_input.text().strip(),
                    message=self.message_input.toPlainText().strip(),
                    notification_type='عام',
                    target_type='all',
                    scheduled_at=scheduled_at
                )
                
                QMessageBox.information(self, "نجاح", "تم إرسال الإشعار بنجاح")
                
                # مسح الحقول
                self.title_input.clear()
                self.message_input.clear()
                
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل الإرسال: {str(e)}")