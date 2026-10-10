"""
واجهة الملف الشخصي للمستخدم - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Optional, Dict
import qtawesome as qta

from app.database.session import session_scope
from app.database.models import User
from app.services.auth_service import AuthService
from app.services.hr_users_factory import HrUsersFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    PageHeader, Card, GradientButton, AvatarLabel, QLineEditPlus
)
from app.views.widgets.dialogs import SuccessDialog, ErrorDialog
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select


class ProfilePage(QWidget):
    """صفحة الملف الشخصي - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, 
                 permission_service: Optional[PermissionService] = None, 
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        # ✅ تعريف permission_service (كان مفقوداً)
        self.permission_service = permission_service
        
        # ✅ تخزين ID المستخدم قبل فقدان الجلسة
        self.user_id = user.id if user else None
        
        # ✅ dicts لبيانات المستخدم
        self.user_data: Dict = {}
        
        # ✅ منع الحفظ قبل التحميل
        self._is_loaded = False
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل أولي
        QTimer.singleShot(100, self.load_user_data)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)
        
        # رأس الصفحة
        header_label = QLabel("الملف الشخصي")
        header_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(header_label)
        
        sub_label = QLabel("عرض وتعديل بياناتك الشخصية")
        sub_label.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(sub_label)

        # بطاقة الصورة والمعلومات الأساسية
        profile_card = Card()
        profile_card.setObjectName("styleCard")

        profile_layout = QHBoxLayout()
        
        # ✅ الصورة الرمزية (placeholder - سيتم تحديثه لاحقاً)
        self.avatar = AvatarLabel("؟", 80, '#1976D3')
        profile_layout.addWidget(self.avatar)
        
        # المعلومات
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        self.name_label = QLabel("جاري التحميل...")
        self.name_label.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #0F172A;"
        )
        info_layout.addWidget(self.name_label)
        
        self.role_label = QLabel("")
        self.role_label.setStyleSheet(
            "font-size: 14px; color: #1976D3; font-weight: 500;"
        )
        info_layout.addWidget(self.role_label)
        
        self.last_login_label = QLabel("")
        self.last_login_label.setStyleSheet(
            "font-size: 11px; color: #64748B;"
        )
        info_layout.addWidget(self.last_login_label)
        
        profile_layout.addLayout(info_layout)
        profile_layout.addStretch()
        
        profile_card.add_widget(self._create_widget(profile_layout))
        main_layout.addWidget(profile_card)

        layout_H = QHBoxLayout()
        
        # بطاقة تعديل البيانات
        edit_card = Card("تعديل البيانات الشخصية")
        edit_card.setObjectName("styleCard")

        edit_layout = QVBoxLayout()

        # رقم الهاتف
        edit_layout.addWidget(self._create_label("رقم الهاتف:"))
        self.phone_input = QLineEditPlus(placeholder="أدخل رقم الهاتف")
        edit_layout.addWidget(self.phone_input)

        label = QLabel("")
        label.setStyleSheet(
            "color: #475569; font-weight: 650; font-size: 8px;"
        )
        edit_layout.addWidget(label)
        
        # البريد الإلكتروني
        edit_layout.addWidget(self._create_label("البريد الإلكتروني:"))
        self.email_input = QLineEditPlus(placeholder="أدخل البريد الإلكتروني")
        edit_layout.addWidget(self.email_input)

        edit_layout.addStretch()
        # زر الحفظ
        self.save_btn = GradientButton("حفظ التغييرات", "fa5s.save")
        self.save_btn.clicked.connect(self.save_profile)
        self.save_btn.setEnabled(False)  # ✅ معطّل حتى التحميل
        edit_layout.addWidget(self.save_btn)

        edit_card.add_widget(self._create_widget(edit_layout))
        
        layout_H.addWidget(edit_card)
        
        # بطاقة تغيير كلمة المرور
        password_card = Card("تغيير كلمة المرور")
        password_card.setObjectName("styleCard")           
        
        password_card.add_widget(self._create_label("كلمة المرور الحالية:"))
        self.current_password_input = QLineEditPlus()
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_card.add_widget(self.current_password_input)
        
        password_card.add_widget(self._create_label("كلمة المرور الجديدة:"))
        self.new_password_input = QLineEditPlus()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_card.add_widget(self.new_password_input)
        
        password_card.add_widget(
            self._create_label("تأكيد كلمة المرور الجديدة:")
        )
        self.confirm_password_input = QLineEditPlus()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_card.add_widget(self.confirm_password_input)
        
        # زر تغيير كلمة المرور
        self.change_password_btn = GradientButton(
            "تغيير كلمة المرور", "fa5s.key"
        )
        self.change_password_btn.setObjectName("warningButton")  
        self.change_password_btn.clicked.connect(self.change_password)
        password_card.add_widget(self.change_password_btn)
        
        layout_H.addWidget(password_card)
        main_layout.addLayout(layout_H)
        main_layout.addStretch()
    
    def _create_widget(self, layout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    def _create_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            "color: #475569; font-weight: 650; font-size: 12px;"
        )
        return label
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_user_data(self):
        self.loading_overlay.show_loading("جاري تحميل البيانات...")

        def _fetch():
            if HrUsersFactory.is_remote():
                return HrUsersFactory.get_service().get_profile()
            else:
                from app.database.session import session_scope
                from app.database.models import User, Role
                from sqlalchemy import select
                with session_scope() as session:
                    u = session.get(User, self.user_id)
                    if not u:
                        return None
                    role = session.get(Role, u.role_id) if u.role_id else None
                    return {
                        'id': u.id,
                        'username': u.username or '',
                        'display_name': u.display_name,
                        'role_name': role.role_name if role else '',
                        'phone': u.phone or '',
                        'email': u.email or '',
                        'last_login_str': (
                            u.last_login.strftime("%Y/%m/%d %H:%M")
                            if u.last_login else 'أول تسجيل'
                        ),
                    }

        def _ok(data):
            try:
                if not data:
                    ErrorDialog("خطأ", "المستخدم غير موجود", self).exec()
                    return
                self.user_data = data
                self.avatar.setText(data['display_name'])
                self.name_label.setText(data['display_name'])
                self.role_label.setText(data['role_name'])
                self.last_login_label.setText(
                    f"آخر تسجيل دخول: {data['last_login_str']}"
                )
                self.phone_input.setText(data['phone'])
                self.email_input.setText(data['email'])
                self._is_loaded = True
                self.save_btn.setEnabled(True)
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            ErrorDialog("خطأ", f"فشل: {m}", self).exec()

        run_async(_fetch, on_result=_ok, on_error=_err)
        
    # ============================================================
    # ✅ حفظ البيانات الشخصية (Async)
    # ============================================================
    
    def save_profile(self):
        if not self._is_loaded:
            ErrorDialog("تنبيه", "انتظر التحميل", self).exec()
            return

        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()

        if email and '@' not in email:
            ErrorDialog("تنبيه", "بريد غير صحيح", self).exec()
            return

        self.loading_overlay.show_loading("جاري الحفظ...")

        def _save():
            if HrUsersFactory.is_remote():
                HrUsersFactory.get_service().update_profile({
                    'phone': phone or None,
                    'email': email or None,
                })
            else:
                from app.database.session import session_scope
                from app.database.models import User
                with session_scope() as session:
                    u = session.get(User, self.user_id)
                    if u:
                        u.phone = phone or None
                        u.email = email or None
                        session.commit()
            return True

        def _ok(_):
            self.loading_overlay.hide_loading()
            SuccessDialog("نجاح", "تم الحفظ", self).exec()
            self.user_data['phone'] = phone
            self.user_data['email'] = email

        def _err(m):
            self.loading_overlay.hide_loading()
            ErrorDialog("خطأ", f"فشل: {m}", self).exec()

        run_async(_save, on_result=_ok, on_error=_err)

    # ============================================================
    # ✅ تغيير كلمة المرور (Async)
    # ============================================================
    
    def change_password(self):
        current = self.current_password_input.text()
        new = self.new_password_input.text()
        confirm = self.confirm_password_input.text()

        if not current or not new or not confirm:
            ErrorDialog("تنبيه", "املأ كل الحقول", self).exec()
            return
        if new != confirm:
            ErrorDialog("تنبيه", "كلمتا المرور غير متطابقتين", self).exec()
            return
        if len(new) < 8:
            ErrorDialog("تنبيه", "8 أحرف على الأقل", self).exec()
            return
        if current == new:
            ErrorDialog("تنبيه", "الجديدة = الحالية", self).exec()
            return

        self.change_password_btn.setEnabled(False)
        self.loading_overlay.show_loading("جاري التغيير...")

        def _do():
            if HrUsersFactory.is_remote():
                HrUsersFactory.get_service().change_password(current, new)
            else:
                from app.database.session import session_scope
                from app.database.models import User
                from app.services.auth_service import AuthService
                with session_scope() as session:
                    AuthService.change_password(
                        session, self.user_id, current, new
                    )
                    session.commit()
            return True

        def _ok(_):
            self.loading_overlay.hide_loading()
            self.change_password_btn.setEnabled(True)
            SuccessDialog("نجاح", "تم التغيير", self).exec()
            self.current_password_input.clear()
            self.new_password_input.clear()
            self.confirm_password_input.clear()

        def _err(m):
            self.loading_overlay.hide_loading()
            self.change_password_btn.setEnabled(True)
            ErrorDialog("خطأ", f"فشل: {m}", self).exec()

        run_async(_do, on_result=_ok, on_error=_err)
        
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
        self._is_loaded = False
        self.save_btn.setEnabled(False)
        self.load_user_data()