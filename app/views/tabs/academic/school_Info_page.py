"""
واجهة إعدادات بيانات المدرسة - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Optional
import qtawesome as qta

from app.core.config import config_manager
from app.database.session import session_scope
from app.database.models import SchoolInfo
from app.services.academic_factory import AcademicFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    PageHeader, Card, GradientButton, QLineEditPlus, QSpinBoxEN
)
from app.views.widgets.dialogs import SuccessDialog, ErrorDialog
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select


class SchoolInfoPage(QWidget):
    """صفحة إعدادات بيانات المدرسة - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ منع الحفظ قبل اكتمال التحميل
        self._is_loaded = False
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل الإعدادات في الخلفية
        QTimer.singleShot(100, self.load_data)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # رأس الصفحة
        title = QLabel("بيانات المدرسة")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("بيانات المدرسة والهوية المطبوعة")
        subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(subtitle)
    
        card = QFrame()
        card.setObjectName("filterCard")
        card.setStyleSheet("""
            QFrame#filterCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        # اسم المدرسة
        row0 = QHBoxLayout()

        row0.addWidget(self._create_label("اسم المدرسة (عربي):"))
        self.school_name_ar_input = QLineEditPlus("أدخل اسم المدرسة بالعربية")
        row0.addWidget(self.school_name_ar_input)
        row0.addSpacing(30)
        row0.addWidget(self._create_label("اسم المدرسة (إنجليزي):"))
        self.school_name_en_input = QLineEditPlus("Enter school name in English")
        row0.addWidget(self.school_name_en_input)

        layout.addLayout(row0)

        # المدير والترخيص
        row4 = QHBoxLayout()
        
        row4.addWidget(self._create_label("المدير العام:"))
        self.principal_input = QLineEditPlus()
        row4.addWidget(self.principal_input)
        row4.addSpacing(30)
        row4.addWidget(self._create_label("رقم الترخيص:"))
        self.license_input = QLineEditPlus()
        row4.addWidget(self.license_input)
        
        layout.addLayout(row4)
        
        # الهواتف
        row5 = QHBoxLayout()
        
        row5.addWidget(self._create_label("الهاتف الرئيسي:"))
        self.phone_primary_input = QLineEditPlus()
        row5.addWidget(self.phone_primary_input)
        row5.addSpacing(30)
        row5.addWidget(self._create_label("الهاتف الثانوي:"))
        self.phone_secondary_input = QLineEditPlus()
        row5.addWidget(self.phone_secondary_input)
        
        layout.addLayout(row5)

        # البريد الإلكتروني
        row6 = QHBoxLayout()
        row6.addWidget(self._create_label("البريد الإلكتروني:"))
        self.email_input = QLineEditPlus()
        row6.addWidget(self.email_input)
        
        layout.addLayout(row6)

        row7 = QHBoxLayout()
        # العنوان
        row7.addWidget(self._create_label("العنوان التفصيلي:"))
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)
        row7.addWidget(self.address_input)
        row7.addSpacing(30)
        # الشروط والأحكام
        row7.addWidget(self._create_label("الشروط والأحكام المطبوعة:"))
        self.terms_input = QTextEdit()
        self.terms_input.setMaximumHeight(80)
        row7.addWidget(self.terms_input)
        
        layout.addLayout(row7)

        layout.addStretch()
        
        # زر الحفظ
        self.save_btn = GradientButton("حفظ الإعدادات", "fa5s.save")
        self.save_btn.clicked.connect(self.save_school_info)
        self.save_btn.setEnabled(False)  # ✅ معطّل حتى اكتمال التحميل
        layout.addWidget(self.save_btn)
        
        main_layout.addWidget(card)
            
    def _create_label(self, text: str) -> QLabel:
        """إنشاء تسمية."""
        label = QLabel(text)
        label.setStyleSheet("color: #475569; font-weight: 600; font-size: 12px;")
        return label
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_data(self):
        self.loading_overlay.show_loading("جاري تحميل الإعدادات...")

        def _fetch():
            if AcademicFactory.is_remote():
                service = AcademicFactory.get_service()
                return service.get_school_info()
            else:
                from app.database.session import session_scope
                from app.database.models import SchoolInfo
                from sqlalchemy import select
                with session_scope() as session:
                    info = session.execute(select(SchoolInfo).limit(1)).scalar_one_or_none()
                    if not info:
                        return None
                    return {
                        'school_name_ar': info.school_name_ar or '',
                        'school_name_en': info.school_name_en or '',
                        'principal_name': info.principal_name or '',
                        'license_number': info.license_number or '',
                        'phone_primary': info.phone_primary or '',
                        'phone_secondary': info.phone_secondary or '',
                        'email': info.email or '',
                        'address_detail': info.address_detail or '',
                        'terms_and_conditions': info.terms_and_conditions or '',
                    }

        def _ok(data):
            try:
                if data:
                    self.school_name_ar_input.setText(data.get('school_name_ar', ''))
                    self.school_name_en_input.setText(data.get('school_name_en', ''))
                    self.principal_input.setText(data.get('principal_name', ''))
                    self.license_input.setText(data.get('license_number', ''))
                    self.phone_primary_input.setText(data.get('phone_primary', ''))
                    self.phone_secondary_input.setText(data.get('phone_secondary', ''))
                    self.email_input.setText(data.get('email', ''))
                    self.address_input.setText(data.get('address_detail', ''))
                    self.terms_input.setText(data.get('terms_and_conditions', ''))
                self._is_loaded = True
                self.save_btn.setEnabled(True)
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            ErrorDialog("خطأ", f"فشل: {m}", self).exec()
            self._is_loaded = True
            self.save_btn.setEnabled(True)

        run_async(_fetch, on_result=_ok, on_error=_err)

    # ============================================================
    # ✅ حفظ الإعدادات (بدون تغيير جوهري)
    # ============================================================
    
    def save_school_info(self):
        if not self._is_loaded:
            QMessageBox.warning(self, "تنبيه", "انتظر التحميل")
            return
        if (self.permission_service
                and not self.permission_service.can_add("التهيئة الأكاديمية")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return
        if not self.school_name_ar_input.text().strip():
            ErrorDialog("تنبيه", "أدخل اسم المدرسة", self).exec()
            return
        payload = {
            'school_name_ar': self.school_name_ar_input.text().strip(),
            'school_name_en': self.school_name_en_input.text().strip() or None,
            'principal_name': self.principal_input.text().strip() or None,
            'license_number': self.license_input.text().strip() or None,
            'phone_primary': self.phone_primary_input.text().strip() or None,
            'phone_secondary': self.phone_secondary_input.text().strip() or None,
            'email': self.email_input.text().strip() or None,
            'address_detail': self.address_input.toPlainText().strip() or None,
            'terms_and_conditions': self.terms_input.toPlainText().strip() or None,
        }
        try:
            if AcademicFactory.is_remote():
                AcademicFactory.get_service().update_school_info(payload)
            else:
                from app.database.session import session_scope
                from app.database.models import SchoolInfo
                from sqlalchemy import select
                with session_scope() as session:
                    info = session.execute(select(SchoolInfo).limit(1)).scalar_one_or_none()
                    if not info:
                        info = SchoolInfo()
                        session.add(info)
                    for k, v in payload.items():
                        setattr(info, k, v)
            SuccessDialog("نجاح", "تم الحفظ", self).exec()
        except Exception as e:
            ErrorDialog("خطأ", f"فشل: {e}", self).exec()

    # ============================================================
    # ✅ الأحداث
    # ============================================================
    
    def resizeEvent(self, event):
        """تحديث حجم طبقة التحميل."""
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())
    
    def refresh(self):
        """إعادة تحميل الإعدادات."""
        self._is_loaded = False
        self.save_btn.setEnabled(False)
        self.load_data()