"""
واجهة إدارة المستخدمين - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta
from datetime import datetime

from app.database.session import session_scope
from app.database.models import User, Employee, Role
from app.services.auth_service import AuthService
from app.services.hr_users_factory import HrUsersFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    PageHeader, Card, QLineEditPlus, SearchBox, ModernTable, Badge,
    GradientButton, IconButton, AvatarLabel
)
from app.views.widgets.dialogs import (
    ConfirmationDialog, SuccessDialog, ErrorDialog, ModernDialog
)
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class UsersPage(QWidget):
    """صفحة إدارة المستخدمين - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.current_user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ تخزين ID المستخدم الحالي
        self.current_user_id = user.id if user else None
        
        # ✅ dicts بدلاً من ORM
        self.all_users: List[Dict] = []
        self.current_filtered_users: List[Dict] = []
        
        # ✅ debounce للبحث
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self.filter_users)
        
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
        header_label = QLabel("إدارة المستخدمين")
        header_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(header_label)
        
        sub_label = QLabel("إدارة حسابات المستخدمين وصلاحياتهم")
        sub_label.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(sub_label)
        
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
        
        self.search_box = SearchBox("بحث عن مستخدم...")
        self.search_box.textChanged.connect(self._on_search_text_changed)
        filter_layout.addWidget(self.search_box)
        
        filter_layout.addWidget(QLabel("الدور:"))
        self.role_filter = QComboBox()
        self.role_filter.addItem("جميع الأدوار", None)
        self.role_filter.currentIndexChanged.connect(self.filter_users)
        filter_layout.addWidget(self.role_filter)
        
        filter_layout.addWidget(QLabel("الحالة:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["جميع الحالات", "نشط", "موقف"])
        self.status_filter.currentIndexChanged.connect(self.filter_users)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch()
        
        add_btn = GradientButton("إضافة مستخدم", "fa5s.user-plus")
        add_btn.clicked.connect(self.add_user)
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
        
        self.count_label = QLabel("إجمالي المستخدمين: 0")
        self.count_label.setObjectName("count_label")
        toolbar.addWidget(self.count_label)
        
        toolbar.addStretch()
        
        edit_btn = IconButton('fa5s.edit', "تعديل", color='#1976D3')
        edit_btn.clicked.connect(self.edit_user)
        toolbar.addWidget(edit_btn)
        
        reset_btn = IconButton('fa5s.key', "إعادة ضبط كلمة المرور", color='#F59E0B')
        reset_btn.clicked.connect(self.reset_password)
        toolbar.addWidget(reset_btn)
        
        toggle_btn = IconButton('fa5s.power-off', "تعطيل/تفعيل", color='#EF4444')
        toggle_btn.clicked.connect(self.toggle_user)
        toolbar.addWidget(toggle_btn)
        
        card_layout.addLayout(toolbar)
        
        # الجدول
        self.table = ModernTable()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "صورة", "اسم المستخدم", "الموظف", "الدور",
            "الحالة", "آخر تسجيل", "إجراء"
        ])
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 180)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 130)
        self.table.setColumnWidth(6, 80)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.edit_user)

        card_layout.addWidget(self.table)
        
        main_layout.addWidget(table_card)
    
    def _create_widget(self, layout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_data(self):
        self.loading_overlay.show_loading("جاري تحميل المستخدمين...")

        def _fetch():
            if HrUsersFactory.is_remote():
                service = HrUsersFactory.get_service()
                return {
                    'users': service.list_users(),
                    'roles': service.list_roles(),
                }
            else:
                from app.database.session import session_scope
                from app.database.models import User, Role
                from sqlalchemy import select
                from sqlalchemy.orm import joinedload
                with session_scope() as session:
                    users = session.execute(
                        select(User)
                        .options(joinedload(User.employee), joinedload(User.role))
                        .order_by(User.username)
                    ).unique().scalars().all()
                    users_data = [
                        {
                            'id': u.id,
                            'username': u.username or '',
                            'display_name': u.display_name,
                            'employee_id': u.employee_id,
                            'employee_name': u.employee.full_name if u.employee else '',
                            'role_id': u.role_id,
                            'role_name': u.role.role_name if u.role else '',
                            'status': u.status or '',
                            'phone': u.phone or '',
                            'email': u.email or '',
                            'last_login_str': (
                                u.last_login.strftime("%Y/%m/%d %H:%M")
                                if u.last_login else ''
                            ),
                        }
                        for u in users
                    ]
                    roles = session.execute(
                        select(Role).order_by(Role.role_name)
                    ).scalars().all()
                    roles_data = [
                        {'id': r.id, 'name': r.role_name or ''} for r in roles
                    ]
                    return {'users': users_data, 'roles': roles_data}

        def _ok(data):
            try:
                self.all_users = data['users']
                self.current_filtered_users = list(self.all_users)
                self.role_filter.blockSignals(True)
                self.role_filter.clear()
                self.role_filter.addItem("جميع الأدوار", None)
                for r in data['roles']:
                    self.role_filter.addItem(r['name'], r['id'])
                self.role_filter.blockSignals(False)
                self.display_users(self.all_users)
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            ErrorDialog("خطأ", f"فشل: {m}", self).exec()

        run_async(_fetch, on_result=_ok, on_error=_err)
        
    # ============================================================
    # ✅ عرض البيانات
    # ============================================================
    
    def display_users(self, users: List[Dict]):
        """عرض المستخدمين."""
        self.table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            # صورة المستخدم
            avatar_widget = QWidget()
            avatar_widget.setStyleSheet("background: transparent;")
            avatar_layout = QHBoxLayout(avatar_widget)
            avatar_layout.setContentsMargins(5, 2, 5, 2)
            avatar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            avatar = AvatarLabel(user['display_name'], 32, '#1976D3')
            avatar_layout.addWidget(avatar)
            
            self.table.setCellWidget(row, 0, avatar_widget)
            self.table.setItem(row, 1, QTableWidgetItem(user['username']))
            self.table.setItem(row, 2, QTableWidgetItem(user['employee_name']))
            self.table.setItem(row, 3, QTableWidgetItem(user['role_name']))
            
            # الحالة
            status_item = QTableWidgetItem(user['status'])
            if user['status'] == 'نشط':
                status_item.setForeground(QColor('#10B981'))
            else:
                status_item.setForeground(QColor('#EF4444'))
            self.table.setItem(row, 4, status_item)
            
            self.table.setItem(
                row, 5, QTableWidgetItem(user['last_login_str'])
            )
            
            # زر التبديل
            toggle_btn = QPushButton()
            if user['status'] == 'نشط':
                toggle_btn.setIcon(qta.icon('fa5s.pause', color='#F59E0B'))
                toggle_btn.setToolTip("تعطيل")
            else:
                toggle_btn.setIcon(qta.icon('fa5s.play', color='#10B981'))
                toggle_btn.setToolTip("تفعيل")
            
            toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            toggle_btn.setStyleSheet("""
                QPushButton {
                    background: #F1F5F9;
                    border: none;
                    border-radius: 6px;
                    padding: 0px 5px;
                }
                QPushButton:hover {
                    background: #E2E8F0;
                }
            """)
            # ✅ تمرير ID فقط
            toggle_btn.clicked.connect(
                lambda checked, uid=user['id']: self.toggle_user_status(uid)
            )
            self.table.setCellWidget(row, 6, toggle_btn)
            self.table.setRowHeight(row, 45)
        
        self.count_label.setText(f"إجمالي المستخدمين: {len(users)}")
    
    # ============================================================
    # ✅ الفلترة
    # ============================================================
    
    def _on_search_text_changed(self):
        """عند تغيير نص البحث - debounce."""
        self._search_timer.stop()
        self._search_timer.start()
    
    def filter_users(self):
        """تصفية المستخدمين."""
        search_text = self.search_box.text().lower().strip()
        role_id = self.role_filter.currentData()
        status = self.status_filter.currentText()
        
        filtered = []
        for user in self.all_users:
            # فلتر البحث
            if search_text:
                username = user['username'].lower()
                employee_name = user['employee_name'].lower()
                if search_text not in username and search_text not in employee_name:
                    continue
            
            # فلتر الدور
            if role_id and user['role_id'] != role_id:
                continue
            
            # فلتر الحالة
            if status != "جميع الحالات" and user['status'] != status:
                continue
            
            filtered.append(user)
        
        self.current_filtered_users = filtered
        self.display_users(filtered)
    
    # ============================================================
    # ✅ الحصول على المستخدم المحدد
    # ============================================================
    
    def _get_selected_user_id(self) -> Optional[int]:
        """الحصول على ID المستخدم المحدد."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
        
        if current_row >= len(self.current_filtered_users):
            return None
        
        return self.current_filtered_users[current_row]['id']
    
    # ============================================================
    # ✅ العمليات
    # ============================================================
    
    def add_user(self):
        """إضافة مستخدم جديد."""
        if self.permission_service and not self.permission_service.can_add("المستخدمين"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للإضافة في المستخدمين"
            )
            return

        dialog = UserDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            SuccessDialog("نجاح", "تم إضافة المستخدم بنجاح", self).exec()
    
    def edit_user(self):
        if (self.permission_service
                and not self.permission_service.can_edit("المستخدمين")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        uid = self._get_selected_user_id()
        if not uid:
            ErrorDialog("تنبيه", "اختر مستخدماً", self).exec()
            return

        try:
            if HrUsersFactory.is_remote():
                user_data = HrUsersFactory.get_service().get_user(uid)
            else:
                from app.database.session import session_scope
                from app.database.models import User
                with session_scope() as session:
                    u = session.get(User, uid)
                    if not u:
                        return
                    user_data = {
                        'id': u.id,
                        'username': u.username or '',
                        'employee_id': u.employee_id,
                        'role_id': u.role_id,
                        'phone': u.phone or '',
                        'email': u.email or '',
                    }
            dialog = UserDialog(user_data=user_data, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_data()
                SuccessDialog("نجاح", "تم التحديث", self).exec()
        except Exception as ex:
            ErrorDialog("خطأ", f"فشل: {ex}", self).exec()

    def reset_password(self):
        if (self.permission_service
                and not self.permission_service.can_cancel("المستخدمين")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        uid = self._get_selected_user_id()
        if not uid:
            ErrorDialog("تنبيه", "اختر مستخدماً", self).exec()
            return

        if ConfirmationDialog(
            "إعادة ضبط", "هل تريد إعادة ضبط كلمة المرور؟", self
        ).exec() != QDialog.DialogCode.Accepted:
            return

        try:
            if HrUsersFactory.is_remote():
                result = HrUsersFactory.get_service().reset_password(uid)
                new_password = result['new_password']
            else:
                from app.database.session import session_scope
                from app.database.models import User
                from app.services.auth_service import AuthService
                with session_scope() as session:
                    new_password = AuthService.reset_password(session, uid)

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("كلمة المرور الجديدة")
            msg.setText("تم إعادة الضبط بنجاح")
            msg.setInformativeText(f"كلمة المرور: {new_password}")
            msg.exec()
        except Exception as ex:
            ErrorDialog("خطأ", f"فشل: {ex}", self).exec()

    def toggle_user(self):
        """تبديل حالة مستخدم (من الشريط)."""
        user_id = self._get_selected_user_id()
        if not user_id:
            ErrorDialog("تنبيه", "يرجى اختيار مستخدم", self).exec()
            return
        
        self.toggle_user_status(user_id)
    
    def toggle_user_status(self, user_id: int):
        if (self.permission_service
                and not self.permission_service.can_delete("المستخدمين")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        try:
            if HrUsersFactory.is_remote():
                result = HrUsersFactory.get_service().toggle_user(user_id)
                message = result.get('message', 'تم التغيير')
            else:
                from app.database.session import session_scope
                from app.database.models import User
                with session_scope() as session:
                    u = session.get(User, user_id)
                    if not u:
                        return
                    if u.status == 'نشط':
                        u.status = 'موقف'
                        message = "تم تعطيل المستخدم"
                    else:
                        u.status = 'نشط'
                        message = "تم تفعيل المستخدم"

            SuccessDialog("نجاح", message, self).exec()
            self.load_data()
        except Exception as ex:
            ErrorDialog("خطأ", f"فشل: {ex}", self).exec()

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
# ✅ نافذة إضافة/تعديل مستخدم (مع dicts)
# ============================================================

class UserDialog(ModernDialog):
    """نافذة إضافة/تعديل مستخدم - مع تحميل غير متزامن."""
    
    def __init__(self, user_data: Optional[dict] = None, parent=None):
        super().__init__(
            "تعديل مستخدم" if user_data else "إضافة مستخدم جديد",
            "fa5s.user-cog",
            parent,
            width=500,
            height=620
        )
        
        # ✅ تخزين dict بدلاً من ORM
        self.user_data = user_data
        self.user_id = user_data['id'] if user_data else None
        
        # ✅ dicts
        self.employees_data: List[Dict] = []
        self.roles_data: List[Dict] = []
        
        self._is_loaded = False
        
        self.setup_form()
        
        # ✅ تحميل أولي
        QTimer.singleShot(50, self._load_initial_data)
    
    def setup_form(self):
        """إعداد النموذج."""
        # اسم المستخدم
        self.add_widget(self._create_label("اسم المستخدم:"))
        self.username_input = QLineEditPlus("أدخل اسم المستخدم")
        self.add_widget(self.username_input)
        
        # كلمة المرور (للمستخدم الجديد فقط)
        if not self.user_data:
            self.add_widget(self._create_label("كلمة المرور:"))
            self.password_input = QLineEditPlus("أدخل كلمة المرور")
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.add_widget(self.password_input)
        
        # الموظف المرتبط
        self.add_widget(self._create_label("الموظف المرتبط:"))
        self.employee_combo = QComboBox()
        self.employee_combo.addItem("بدون موظف", None)
        self.add_widget(self.employee_combo)
        
        # الدور
        self.add_widget(self._create_label("الدور:"))
        self.role_combo = QComboBox()
        self.add_widget(self.role_combo)
        
        # الهاتف
        self.add_widget(self._create_label("رقم الهاتف:"))
        self.phone_input = QLineEditPlus()
        self.add_widget(self.phone_input)
        
        # البريد الإلكتروني
        self.add_widget(self._create_label("البريد الإلكتروني:"))
        self.email_input = QLineEditPlus()
        self.add_widget(self.email_input)
        
        # الأزرار
        self.add_button("حفظ", self.save_user, "primary")
        self.add_button("إلغاء", self.reject, "default")
    
    def _create_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            "color: #475569; font-weight: 600; font-size: 12px;"
        )
        return label
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def _load_initial_data(self):
        def _fetch():
            if HrUsersFactory.is_remote():
                service = HrUsersFactory.get_service()
                employees = service.client.get("/api/hr/employees/")
                roles = service.list_roles()
                return {
                    'employees': [
                        {'id': e['id'], 'name': e['full_name']}
                        for e in employees
                    ],
                    'roles': roles,
                }
            else:
                from app.database.session import session_scope
                from app.database.models import Employee, Role
                from sqlalchemy import select
                with session_scope() as session:
                    employees = session.execute(
                        select(Employee).filter(
                            Employee.deleted_at.is_(None)
                        ).order_by(Employee.full_name)
                    ).scalars().all()
                    roles = session.execute(
                        select(Role).order_by(Role.role_name)
                    ).scalars().all()
                    return {
                        'employees': [
                            {'id': e.id, 'name': e.full_name or ''}
                            for e in employees
                        ],
                        'roles': [
                            {'id': r.id, 'name': r.role_name or ''}
                            for r in roles
                        ],
                    }

        def _ok(data):
            self.employees_data = data['employees']
            self.roles_data = data['roles']
            for emp in self.employees_data:
                self.employee_combo.addItem(emp['name'], emp['id'])
            for role in self.roles_data:
                self.role_combo.addItem(role['name'], role['id'])
            self._is_loaded = True
            if self.user_data:
                self._fill_user_data()

        run_async(_fetch, on_result=_ok)

    def _fill_user_data(self):
        """تعبئة بيانات المستخدم للتعديل."""
        if not self.user_data:
            return
        
        d = self.user_data
        
        self.username_input.setText(d['username'])
        
        if d['employee_id']:
            index = self.employee_combo.findData(d['employee_id'])
            if index >= 0:
                self.employee_combo.setCurrentIndex(index)
        
        if d['role_id']:
            index = self.role_combo.findData(d['role_id'])
            if index >= 0:
                self.role_combo.setCurrentIndex(index)
        
        self.phone_input.setText(d['phone'])
        self.email_input.setText(d['email'])
    
    # ============================================================
    # ✅ الحفظ
    # ============================================================
    
    def save_user(self):
        if not self._is_loaded:
            ErrorDialog("تنبيه", "انتظر التحميل", self).exec()
            return
        if not self.username_input.text().strip():
            ErrorDialog("تنبيه", "أدخل اسم المستخدم", self).exec()
            return
        if not self.user_id and (
            not hasattr(self, 'password_input')
            or not self.password_input.text()
        ):
            ErrorDialog("تنبيه", "أدخل كلمة المرور", self).exec()
            return

        try:
            if HrUsersFactory.is_remote():
                service = HrUsersFactory.get_service()
                payload = {
                    'username': self.username_input.text().strip(),
                    'employee_id': self.employee_combo.currentData(),
                    'role_id': self.role_combo.currentData(),
                    'phone': self.phone_input.text().strip() or None,
                    'email': self.email_input.text().strip() or None,
                }
                if self.user_id:
                    service.update_user(self.user_id, payload)
                else:
                    payload['password'] = self.password_input.text()
                    service.create_user(payload)
            else:
                self._save_local()
            self.accept()
        except Exception as ex:
            ErrorDialog("خطأ", f"فشل: {ex}", self).exec()

    def _save_local(self):
        from app.database.session import session_scope
        from app.database.models import User
        from app.services.auth_service import AuthService
        from sqlalchemy import select
        with session_scope() as session:
            if self.user_id:
                user = session.get(User, self.user_id)
            else:
                existing = session.execute(
                    select(User).where(
                        User.username == self.username_input.text().strip()
                    )
                ).scalar_one_or_none()
                if existing:
                    raise Exception("اسم المستخدم موجود")
                user = User()
                session.add(user)
                result = AuthService.hash_password(self.password_input.text())
                user.password_hash = result[0] if isinstance(result, tuple) else result
                user.status = 'نشط'

            user.username = self.username_input.text().strip()
            user.employee_id = self.employee_combo.currentData()
            user.role_id = self.role_combo.currentData()
            user.phone = self.phone_input.text().strip() or None
            user.email = self.email_input.text().strip() or None
            session.commit()