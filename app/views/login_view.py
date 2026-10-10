"""
نافذة تسجيل الدخول - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Optional, Callable, Dict
from fastapi import logger
import qtawesome as qta
import sys

from app.core.config import config_manager
from app.services.auth_service import AuthService
from app.database.session import session_scope
from app.database.models import AcademicYear, User, Employee, Role
from app.views.widgets.custom_widgets import GradientButton, QLineEditPlus
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class LoginWindow(QWidget):
    """نافذة تسجيل الدخول الرئيسية - مع تحميل غير متزامن."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تسجيل الدخول - نظام إدارة المدرسة")
        self.setFixedSize(1000, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # ✅ dicts بدلاً من ORM objects
        self.logged_in_user_data: Optional[Dict] = None
        self.selected_year_data: Optional[Dict] = None
        
        self._drag_pos = None
        self.login_successful: Optional[Callable] = None
        self.loading_dialog = None
        
        # ✅ debounce للتحقق من الإدخال
        self._is_logging_in = False

        # ✅ حقول مؤقتة لتمرير بيانات الدخول إلى _authenticate_task
        self._pending_username: str = ""
        self._pending_password: str = ""
        self._pending_year_id: int = 0
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل السنوات الدراسية في الخلفية (بعد ظهور النافذة)
        QTimer.singleShot(100, self.load_academic_years)
        
        # ✅ ظل النافذة
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setXOffset(0)
        shadow.setYOffset(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)
    
    def setup_ui(self):
        """إعداد واجهة تسجيل الدخول."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
            }
        """)
        main_layout.addWidget(card)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        
        left_panel = self._create_left_panel()
        card_layout.addWidget(left_panel, 1)
        
        right_panel = self._create_right_panel()
        card_layout.addWidget(right_panel, 1)
    
    def _create_left_panel(self) -> QWidget:
        """إنشاء اللوحة اليسرى."""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1565C0, stop:0.5 #1976D3, stop:1 #64B5F6);
                border-top-left-radius: 20px;
                border-bottom-left-radius: 20px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        icon_label = QLabel()
        icon_label.setPixmap(
            qta.icon('fa5s.school', color='white').pixmap(80, 80)
        )
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(icon_label)
        
        title = QLabel("نظام إدارة المدرسة")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: 800;
            background: transparent;
        """)
        layout.addWidget(title)
        
        description = QLabel(
            "نظام متكامل لإدارة المدارس الأهلية\n"
            "يشمل الشؤون الأكاديمية والمالية والإدارية"
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 13px;
            line-height: 1.6;
            background: transparent;
        """)
        layout.addWidget(description)
        
        layout.addStretch()
        
        features = [
            ("fa5s.chart-line", "تقارير وإحصائيات شاملة"),
            ("fa5s.wallet", "إدارة مالية متكاملة"),
            ("fa5s.bell", "إشعارات فورية"),
            ("fa5s.cloud", "مزامنة سحابية"),
        ]
        
        for icon, text in features:
            feature_layout = QHBoxLayout()
            
            feature_icon = QLabel()
            feature_icon.setPixmap(
                qta.icon(icon, color='white').pixmap(20, 20)
            )
            feature_icon.setStyleSheet("background: transparent;")
            feature_layout.addWidget(feature_icon)
            
            feature_text = QLabel(text)
            feature_text.setStyleSheet("""
                color: white;
                font-size: 12px;
                font-weight: 500;
                background: transparent;
            """)
            feature_layout.addWidget(feature_text)
            feature_layout.addStretch()
            
            layout.addLayout(feature_layout)
        
        layout.addStretch()
        
        copyright_label = QLabel("© 2024 جميع الحقوق محفوظة")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-size: 11px;
            background: transparent;
        """)
        layout.addWidget(copyright_label)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """إنشاء اللوحة اليمنى."""
        panel = QWidget()
        panel.setStyleSheet("background: white;")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(15)
        
        # زر الإغلاق
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        close_btn = QPushButton()
        close_btn.setIcon(qta.icon('fa5s.times', color='#64748B'))
        close_btn.setIconSize(QSize(14, 14))
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #F1F5F9;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background: #EF4444;
            }
        """)
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)
        
        # العنوان
        title = QLabel("مرحباً بعودتك!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: #0F172A;
            font-size: 22px;
            font-weight: 700;
        """)
        layout.addWidget(title)
        
        subtitle = QLabel("قم بتسجيل الدخول للمتابعة")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            color: #64748B;
            font-size: 13px;
        """)
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # السنة الدراسية
        year_label = QLabel("السنة الدراسية")
        year_label.setStyleSheet(
            "color: #475569; font-weight: 600; font-size: 12px;"
        )
        layout.addWidget(year_label)
        
        self.year_combo = QComboBox()
        self.year_combo.setMinimumHeight(40)
        self.year_combo.addItem("جاري التحميل...", None)  # ✅ مؤقت
        self.year_combo.setEnabled(False)  # ✅ معطّل حتى التحميل
        self.year_combo.setStyleSheet("""
            QComboBox {
                background: #F8FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 13px;
                color: #0F172A;
            }
            QComboBox:hover {
                border-color: #CBD5E1;
            }
            QComboBox:focus {
                border-color: #1976D3;
            }
            QComboBox:disabled {
                background: #F1F5F9;
                color: #94A3B8;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 5px;
                selection-background-color: #1976D3;
                selection-color: white;
            }
        """)
        layout.addWidget(self.year_combo)
        
        # اسم المستخدم
        username_label = QLabel("اسم المستخدم")
        username_label.setStyleSheet(
            "color: #475569; font-weight: 600; font-size: 12px;"
        )
        layout.addWidget(username_label)
        
        self.username_input = QLineEditPlus(placeholder="أدخل اسم المستخدم")
        self.username_input.setMinimumHeight(40)
        layout.addWidget(self.username_input)
        
        # كلمة المرور
        password_label = QLabel("كلمة المرور")
        password_label.setStyleSheet(
            "color: #475569; font-weight: 600; font-size: 12px;"
        )
        layout.addWidget(password_label)
        
        self.password_input = QLineEditPlus(placeholder="أدخل كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        layout.addWidget(self.password_input)
        
        # خيارات
        options_layout = QHBoxLayout()
        
        self.remember_checkbox = QCheckBox("تذكرني")
        self.remember_checkbox.setStyleSheet(
            "color: #64748B; font-size: 12px;"
        )
        options_layout.addWidget(self.remember_checkbox)
        
        options_layout.addStretch()
        
        forgot_btn = QPushButton("نسيت كلمة المرور؟")
        forgot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #1976D3;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #0D47A1;
            }
        """)
        options_layout.addWidget(forgot_btn)
        
        layout.addLayout(options_layout)
        
        layout.addSpacing(10)
        
        # زر تسجيل الدخول
        self.login_btn = GradientButton("تسجيل الدخول")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)
        
        layout.addStretch()
        
        version_label = QLabel(
            f"الإصدار {config_manager.app_config.app_version}"
        )
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #CBD5E1; font-size: 11px;")
        layout.addWidget(version_label)
        
        return panel
    
    # ============================================================
    # ✅ تحميل السنوات الدراسية (Async)
    # ============================================================
    
    def load_academic_years(self):
        """تحميل السنوات الدراسية في الخلفية."""
        def _fetch_data():
            """جلب السنوات (في الخلفية)."""
            with session_scope() as session:
                from sqlalchemy import select
                years = session.execute(
                    select(AcademicYear)
                    .order_by(AcademicYear.start_date.desc())
                ).scalars().all()
                
                # ✅ تحويل إلى dicts
                return [
                    {
                        'id': y.id,
                        'name': y.year_name_gregorian or '',
                        'is_current': bool(y.is_current),
                    }
                    for y in years
                ]
        
        def _on_result(data):
            """عند اكتمال التحميل."""
            try:
                self.year_combo.blockSignals(True)
                self.year_combo.clear()
                
                if not data:
                    # لا توجد سنوات دراسية
                    self.year_combo.addItem("لا توجد سنوات دراسية", None)
                    self.year_combo.setEnabled(False)
                    self.login_btn.setEnabled(False)
                    return
                
                for year in data:
                    self.year_combo.addItem(year['name'], year['id'])
                
                # ✅ تعيين السنة الحالية افتراضياً
                current_year_index = next(
                    (i for i, y in enumerate(data) if y['is_current']),
                    0
                )
                self.year_combo.setCurrentIndex(current_year_index)
                
                self.year_combo.setEnabled(True)
                self.year_combo.blockSignals(False)
                
            except Exception as e:
                print(f"خطأ في تحديث السنوات: {str(e)}")
        
        def _on_error(error_msg):
            print(f"فشل تحميل السنوات: {error_msg}")
            self.year_combo.clear()
            self.year_combo.addItem("خطأ في التحميل", None)
            self.year_combo.setEnabled(False)
        
        # ✅ لا نُظهر LoadingOverlay لأن التحميل سريع
        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
    
    # ============================================================
    # ✅ تسجيل الدخول (Async)
    # ============================================================
    
    def login(self):
        """تسجيل الدخول - مع حوار تحقق."""
        # ✅ منع الضغط المزدوج
        if self._is_logging_in:
            return
        
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # ✅ التحقق من الإدخال
        if not username:
            self._show_error("يرجى إدخال اسم المستخدم")
            self.username_input.setFocus()
            return
        
        if not password:
            self._show_error("يرجى إدخال كلمة المرور")
            self.password_input.setFocus()
            return
        
        # ✅ التحقق من اختيار السنة
        year_id = self.year_combo.currentData()
        if not year_id:
            self._show_error("يرجى اختيار السنة الدراسية")
            return
        
        self._is_logging_in = True
        
        # ✅ 1. عرض حوار التحقق
        from app.views.widgets.loading_dialog import LoadingDialog
        self.loading_dialog = LoadingDialog(
            self,
            title="جاري التحقق",
            message="يتم التحقق من بياناتك، الرجاء الانتظار..."
        )
        self.loading_dialog.show()
        QApplication.processEvents()
        
        # ✅ 2. تعطيل الحقول
        self.login_btn.setEnabled(False)
        self.username_input.setEnabled(False)
        self.password_input.setEnabled(False)
        self.year_combo.setEnabled(False)

        # احفظ بيانات الدخول ليستخدمها _authenticate_task
        self._pending_username = username
        self._pending_password = password
        self._pending_year_id = year_id

        # ✅ 3. المصادقة في الخلفية
        self._authenticate(username, password, year_id)
    
    def _authenticate(self, username: str, password: str, year_id: int):
        """تنفيذ المصادقة في الخلفية."""
        # ✅ احفظ بيانات الدخول (تستخدمها _authenticate_task)
        self._pending_username = username
        self._pending_password = password
        self._pending_year_id = year_id

        def _on_result(data):
            """عند اكتمال المصادقة."""
            self._is_logging_in = False

            if data is None:
                if self.loading_dialog:
                    self.loading_dialog.close()
                    self.loading_dialog = None
                self._enable_form()
                self._show_error("اسم المستخدم أو كلمة المرور غير صحيحة")
                return

            # ✅ نجاح
            self.logged_in_user_data = data['user']
            self.selected_year_data = data['year']

            self._show_success()

            if self.loading_dialog:
                self.loading_dialog.set_message("✓ تم التحقق بنجاح!")
                self.loading_dialog.set_success()
                QApplication.processEvents()
                QTimer.singleShot(500, self._finish_login_success)

        def _on_error(error_msg):
            """عند حدوث خطأ."""
            self._is_logging_in = False

            if self.loading_dialog:
                self.loading_dialog.close()
                self.loading_dialog = None

            self._enable_form()
            self._show_error(f"فشل تسجيل الدخول:\n{error_msg}")

        # ✅ استدعاء دالة الفصل (بدون parameters)
        run_async(
            self._authenticate_task,
            on_result=_on_result,
            on_error=_on_error,
        )

    def _authenticate_task(self):
        """مهمة المصادقة (في الخلفية) - دالة في الفصل."""
        from app.core.config import config_manager

        api_mode = config_manager.app_config.api_mode

        # ==================== Remote Mode ====================
        if api_mode in ('remote', 'auto'):
            try:
                return self._authenticate_remote()
            except Exception as e:
                if api_mode == 'auto':
                    import logging
                    logging.getLogger(__name__).warning(
                        f"Remote فشل، fallback: {e}"
                    )
                else:
                    raise

        # ==================== Local Mode ====================
        return self._authenticate_local()

    def _authenticate_remote(self):
        """مصادقة عبر Local API."""
        from app.services.auth_factory import AuthFactory

        client = AuthFactory.get_api_client()
        service = AuthFactory.get_auth_service()

        # 1. تسجيل دخول
        login_result = service.authenticate(
            self._pending_username,
            self._pending_password,
        )

        # 2. اجلب الصلاحيات + معلومات المستخدم
        me = client.get("/api/auth/me")

        # 3. اجلب السنة
        years = client.get("/api/academic-years/")
        year_data = next(
            (y for y in years if y['id'] == self._pending_year_id),
            None,
        )
        if not year_data:
            raise Exception("السنة الدراسية غير موجودة")

        return {
            'user': {
                'id': me['id'],
                'username': me['username'],
                'display_name': me.get('full_name', me['username']),
                'role_id': me['role_id'],
                'role_name': me.get('role_name', ''),
                'employee_id': me.get('employee_id'),
                'employee_name': me.get('full_name', ''),
                'phone': me.get('phone', ''),
                'email': me.get('email', ''),
                'status': 'نشط',
                'permissions': me.get('permissions', {}),
                'last_login': None,
            },
            'year': {
                'id': year_data['id'],
                'name': year_data['name'],
                'is_current': year_data['is_current'],
                'start_date': None,
                'end_date': None,
            },
        }

    def _authenticate_local(self):
        """مصادقة تقليدية عبر DB محلي (legacy)."""
        with session_scope() as session:
            user = AuthService.authenticate(
                session,
                self._pending_username,
                self._pending_password,
            )
            if not user:
                return None

            year = session.get(AcademicYear, self._pending_year_id)
            if not year:
                return None

            # المنطق القديم
            role_name = ''
            employee_name = ''
            user_display_name = user.username or ''

            try:
                if user.role:
                    role_name = user.role.role_name or ''
            except Exception:
                pass

            try:
                if user.employee:
                    employee_name = user.employee.full_name or ''
                    if employee_name:
                        user_display_name = employee_name
            except Exception:
                pass

            try:
                if hasattr(user, 'display_name'):
                    user_display_name = (
                        user.display_name or user_display_name
                    )
            except Exception:
                pass

            return {
                'user': {
                    'id': user.id,
                    'username': user.username or '',
                    'display_name': user_display_name,
                    'role_id': user.role_id,
                    'role_name': role_name,
                    'employee_id': user.employee_id,
                    'employee_name': employee_name,
                    'phone': user.phone or '',
                    'email': user.email or '',
                    'status': user.status or '',
                    'last_login': user.last_login,
                    'permissions': None,
                },
                'year': {
                    'id': year.id,
                    'name': year.year_name_gregorian or '',
                    'is_current': bool(year.is_current),
                    'start_date': year.start_date,
                    'end_date': year.end_date,
                }
            }
        
    def _enable_form(self):
        """إعادة تفعيل الحقول."""
        self.login_btn.setEnabled(True)
        self.username_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.year_combo.setEnabled(True)
    
    def _finish_login_success(self):
        """إغلاق الحوار وإكمال تسجيل الدخول."""
        if self.loading_dialog:
            self.loading_dialog.close()
            self.loading_dialog = None
        
        # ✅ استدعاء الـ callback
        self._notify_login_success()
        self.close()
    
    def _notify_login_success(self):
        """إعلام نجاح تسجيل الدخول - يعمل في الوضعين."""
        if not (self.login_successful
                and self.logged_in_user_data
                and self.selected_year_data):
            return

        from app.core.config import config_manager
        from types import SimpleNamespace

        # ✅ استخدم SimpleNamespace دائماً (يعمل مع API و Local)
        user_data = self.logged_in_user_data
        year_data = self.selected_year_data

        user = SimpleNamespace(
            id=user_data['id'],
            username=user_data['username'],
            display_name=user_data['display_name'],
            role_id=user_data['role_id'],
            role_name=user_data.get('role_name', ''),
            employee_id=user_data['employee_id'],
            phone=user_data['phone'],
            email=user_data['email'],
            status=user_data['status'],
            permissions=user_data.get('permissions'),
            # العلاقات لا تُستخدم في وضع API
            role=None,
            employee=None,
        )

        year = SimpleNamespace(
            id=year_data['id'],
            year_name_gregorian=year_data['name'],
            is_current=year_data['is_current'],
            start_date=year_data.get('start_date'),
            end_date=year_data.get('end_date'),
        )

        try:
            self.login_successful(user, year)
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                None, "خطأ",
                f"فشل فتح النظام:\n{str(e)}"
            )

    def _show_error(self, message: str):
        """عرض رسالة خطأ."""
        QMessageBox.critical(self, "خطأ", message)
    
    def _show_success(self):
        """عرض رسالة نجاح."""
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: #10B981;
                border: none;
                color: white;
                font-size: 14px;
                font-weight: 700;
                border-radius: 10px;
            }
        """)
        self.login_btn.setText("✓ تم تسجيل الدخول بنجاح")
    
    # ============================================================
    # ✅ الأحداث
    # ============================================================
    
    def resizeEvent(self, event):
        """تحديث حجم طبقة التحميل."""
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())
    
    def mousePressEvent(self, event):
        """بدء سحب النافذة."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - 
                self.frameGeometry().topLeft()
            )
            event.accept()
    
    def mouseMoveEvent(self, event):
        """سحب النافذة."""
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """إنهاء السحب."""
        self._drag_pos = None
        event.accept()
    
    def keyPressEvent(self, event):
        """معالجة ضغطات المفاتيح."""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.login()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)