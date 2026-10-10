"""
واجهة إعدادات النظام - تصميم فاخر.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Optional
import qtawesome as qta

from app.core.config import config_manager
from app.database.session import session_scope
from app.database.models import SchoolInfo
from app.views.widgets.custom_widgets import (
    PageHeader, Card, GradientButton, QLineEditPlus, QSpinBoxEN
)
from app.views.widgets.dialogs import SuccessDialog, ErrorDialog
from sqlalchemy import select


class SettingsPage(QWidget):
    """صفحة إعدادات النظام."""
    
    def __init__(self, user, academic_year, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)
        
        header = PageHeader(
            "إعدادات النظام",
            "إعدادات المدرسة والهوية المطبوعة"
        )
        main_layout.addWidget(header)
        
        # منطقة التمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # تبويبات الإعدادات
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                background: white;
                padding: 15px;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin-right: 5px;
                font-weight: 600;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                color: #1976D3;
                border-bottom: 3px solid #1976D3;
            }
        """)
        
        # تبويب بيانات المدرسة
        school_tab = self._create_school_tab()
        tabs.addTab(school_tab, "بيانات المدرسة")
        
        # تبويب الإعدادات العامة
        general_tab = self._create_general_tab()
        tabs.addTab(general_tab, "الإعدادات العامة")
        
        # تبويب النسخ الاحتياطي
        backup_tab = self._create_backup_tab()
        tabs.addTab(backup_tab, "النسخ الاحتياطي")
        
        scroll_layout.addWidget(tabs)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
    
    def _create_school_tab(self) -> QWidget:
        """إنشاء تبويب بيانات المدرسة."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # اسم المدرسة
        layout.addWidget(self._create_label("اسم المدرسة (عربي):"))
        self.school_name_ar_input = QLineEditPlus("أدخل اسم المدرسة بالعربية")
        layout.addWidget(self.school_name_ar_input)
        
        layout.addWidget(self._create_label("اسم المدرسة (إنجليزي):"))
        self.school_name_en_input = QLineEditPlus("Enter school name in English")
        layout.addWidget(self.school_name_en_input)
        
        # المدير والترخيص
        row1 = QHBoxLayout()
        
        row1.addWidget(self._create_label("المدير العام:"))
        self.principal_input = QLineEditPlus()
        row1.addWidget(self.principal_input)
        
        row1.addWidget(self._create_label("رقم الترخيص:"))
        self.license_input = QLineEditPlus()
        row1.addWidget(self.license_input)
        
        layout.addLayout(row1)
        
        # الهواتف
        row2 = QHBoxLayout()
        
        row2.addWidget(self._create_label("الهاتف الرئيسي:"))
        self.phone_primary_input = QLineEditPlus()
        row2.addWidget(self.phone_primary_input)
        
        row2.addWidget(self._create_label("الهاتف الثانوي:"))
        self.phone_secondary_input = QLineEditPlus()
        row2.addWidget(self.phone_secondary_input)
        
        layout.addLayout(row2)
        
        # البريد الإلكتروني
        layout.addWidget(self._create_label("البريد الإلكتروني:"))
        self.email_input = QLineEditPlus()
        layout.addWidget(self.email_input)
        
        # العنوان
        layout.addWidget(self._create_label("العنوان التفصيلي:"))
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)
        layout.addWidget(self.address_input)
        
        # الشروط والأحكام
        layout.addWidget(self._create_label("الشروط والأحكام المطبوعة:"))
        self.terms_input = QTextEdit()
        self.terms_input.setMaximumHeight(80)
        layout.addWidget(self.terms_input)
        
        # زر الحفظ
        save_btn = GradientButton("حفظ الإعدادات", "fa5s.save")
        save_btn.clicked.connect(self.save_school_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        return widget
    
    def _create_general_tab(self) -> QWidget:
        """إنشاء تبويب الإعدادات العامة."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # اللغة
        layout.addWidget(self._create_label("اللغة:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["العربية", "English"])
        layout.addWidget(self.language_combo)
        
        # الثيم
        layout.addWidget(self._create_label("المظهر:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["فاتح", "داكن"])
        layout.addWidget(self.theme_combo)
        
        # المزامنة
        sync_group = QGroupBox("إعدادات المزامنة")
        sync_layout = QVBoxLayout(sync_group)
        
        self.sync_enabled_checkbox = QCheckBox("تفعيل المزامنة التلقائية")
        self.sync_enabled_checkbox.setChecked(config_manager.app_config.sync_enabled)
        sync_layout.addWidget(self.sync_enabled_checkbox)
        
        sync_interval_layout = QHBoxLayout()
        sync_interval_layout.addWidget(QLabel("فترة المزامنة (ثانية):"))
        self.sync_interval_spin = QSpinBoxEN(10, 3600)
        self.sync_interval_spin.setValue(config_manager.app_config.sync_interval)
        sync_interval_layout.addWidget(self.sync_interval_spin)
        sync_interval_layout.addStretch()
        sync_layout.addLayout(sync_interval_layout)
        
        layout.addWidget(sync_group)
        
        # النسخ الاحتياطي
        backup_group = QGroupBox("إعدادات النسخ الاحتياطي")
        backup_layout = QVBoxLayout(backup_group)
        
        self.backup_enabled_checkbox = QCheckBox("تفعيل النسخ الاحتياطي التلقائي")
        self.backup_enabled_checkbox.setChecked(config_manager.app_config.backup_enabled)
        backup_layout.addWidget(self.backup_enabled_checkbox)
        
        backup_interval_layout = QHBoxLayout()
        backup_interval_layout.addWidget(QLabel("التكرار:"))
        self.backup_interval_combo = QComboBox()
        self.backup_interval_combo.addItems(["يومي", "أسبوعي", "شهري"])
        backup_interval_layout.addWidget(self.backup_interval_combo)
        backup_interval_layout.addStretch()
        backup_layout.addLayout(backup_interval_layout)
        
        layout.addWidget(backup_group)
        
        # زر الحفظ
        save_btn = GradientButton("حفظ الإعدادات", "fa5s.save")
        save_btn.clicked.connect(self.save_general_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        return widget
    
    def _create_backup_tab(self) -> QWidget:
        """إنشاء تبويب النسخ الاحتياطي."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # أزرار النسخ الاحتياطي
        buttons_layout = QHBoxLayout()
        
        create_backup_btn = GradientButton("إنشاء نسخة احتياطية", "fa5s.download")
        create_backup_btn.clicked.connect(self.create_backup)
        buttons_layout.addWidget(create_backup_btn)
        
        restore_btn = GradientButton("استعادة نسخة", "fa5s.upload")
        restore_btn.setObjectName("warningButton")
        restore_btn.clicked.connect(self.restore_backup)
        buttons_layout.addWidget(restore_btn)
        
        layout.addLayout(buttons_layout)
        
        # سجل النسخ الاحتياطية
        layout.addWidget(self._create_label("سجل النسخ الاحتياطية:"))
        
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(4)
        self.backup_table.setHorizontalHeaderLabels([
            "اسم الملف", "الحجم", "التاريخ", "المستخدم"
        ])
        self.backup_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.backup_table)
        
        return widget
    
    def _create_label(self, text: str) -> QLabel:
        """إنشاء تسمية."""
        label = QLabel(text)
        label.setStyleSheet("color: #475569; font-weight: 600; font-size: 12px;")
        return label
    
    def load_settings(self):
        """تحميل الإعدادات."""
        try:
            with session_scope() as session:
                school_info = session.execute(
                    select(SchoolInfo).limit(1)
                ).scalar_one_or_none()
                
                if school_info:
                    self.school_name_ar_input.setText(school_info.school_name_ar)
                    self.school_name_en_input.setText(school_info.school_name_en or "")
                    self.principal_input.setText(school_info.principal_name or "")
                    self.license_input.setText(school_info.license_number or "")
                    self.phone_primary_input.setText(school_info.phone_primary or "")
                    self.phone_secondary_input.setText(school_info.phone_secondary or "")
                    self.email_input.setText(school_info.email or "")
                    self.address_input.setText(school_info.address_detail or "")
                    self.terms_input.setText(school_info.terms_and_conditions or "")
        except Exception as e:
            print(f"خطأ في تحميل الإعدادات: {str(e)}")
    
    def save_school_settings(self):
        """حفظ إعدادات المدرسة."""
        if not self.school_name_ar_input.text().strip():
            ErrorDialog("تنبيه", "يرجى إدخال اسم المدرسة", self).exec()
            return
        
        try:
            with session_scope() as session:
                school_info = session.execute(
                    select(SchoolInfo).limit(1)
                ).scalar_one_or_none()
                
                if not school_info:
                    school_info = SchoolInfo()
                    session.add(school_info)
                
                school_info.school_name_ar = self.school_name_ar_input.text().strip()
                school_info.school_name_en = self.school_name_en_input.text().strip() or None
                school_info.principal_name = self.principal_input.text().strip() or None
                school_info.license_number = self.license_input.text().strip() or None
                school_info.phone_primary = self.phone_primary_input.text().strip() or None
                school_info.phone_secondary = self.phone_secondary_input.text().strip() or None
                school_info.email = self.email_input.text().strip() or None
                school_info.address_detail = self.address_input.toPlainText().strip() or None
                school_info.terms_and_conditions = self.terms_input.toPlainText().strip() or None
                
                SuccessDialog("نجاح", "تم حفظ الإعدادات بنجاح", self).exec()
        
        except Exception as e:
            ErrorDialog("خطأ", f"فشل حفظ الإعدادات: {str(e)}", self).exec()
    
    def save_general_settings(self):
        """حفظ الإعدادات العامة."""
        try:
            config_manager.update_app_config(
                language='ar' if self.language_combo.currentText() == "العربية" else 'en',
                theme='light' if self.theme_combo.currentText() == "فاتح" else 'dark',
                sync_enabled=self.sync_enabled_checkbox.isChecked(),
                sync_interval=self.sync_interval_spin.value(),
                backup_enabled=self.backup_enabled_checkbox.isChecked(),
                backup_interval=self.backup_interval_combo.currentText()
            )
            
            SuccessDialog("نجاح", "تم حفظ الإعدادات بنجاح", self).exec()
        except Exception as e:
            ErrorDialog("خطأ", f"فشل حفظ الإعدادات: {str(e)}", self).exec()
    
    def create_backup(self):
        """إنشاء نسخة احتياطية."""
        # سيتم تنفيذها في مرحلة النسخ الاحتياطي
        SuccessDialog("نجاح", "سيتم تنفيذ النسخ الاحتياطي في المرحلة القادمة", self).exec()
    
    def restore_backup(self):
        """استعادة نسخة احتياطية."""
        # سيتم تنفيذها في مرحلة النسخ الاحتياطي
        pass