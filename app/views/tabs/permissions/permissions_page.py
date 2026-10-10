"""
واجهة إدارة الصلاحيات والأدوار - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Dict, Optional
import qtawesome as qta

from app.database.session import session_scope
from app.database.models import Role, Permission, RolePermission
from app.services.permission_service import PermissionService
from app.services.permissions_factory import PermissionsFactory
from app.views.widgets.custom_widgets import (
    PageHeader, Card, GradientButton, QLineEditPlus
)
from app.views.widgets.dialogs import (
    SuccessDialog, ErrorDialog, ModernDialog
)
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select


class PermissionsPage(QWidget):
    """صفحة إدارة الصلاحيات - مع تحميل غير متزامن."""
    
    MODULES = [
        "لوحة التحكم", "لوحة المحاسب", "التهيئة الأكاديمية", "إدارة الطلاب", 
        "أولياء الأمور", "وثائق الطلاب", "توزيع الطلاب", "رسوم الطلاب", "سندات القبض",
        "كشف حساب طالب", "الموظفين والمعلمين", "سندات الصرف", "البدلات والخصومات",
        "السلف المالية", "كشف الرواتب", "كشف حساب موظف", "رصد الدرجات",
        "الشهادات والأوائل", "الحضور والغياب", "الواجبات المنزلية",
        "المتابعة السلوكية", "الجداول الدراسية", "المستخدمين", "الصلاحيات",
        "الإشعارات", "التقارير", "الإعدادات",
    ]
    
    PERMISSION_KEYS = [
        ("can_view", "عرض"),
        ("can_add", "إضافة"),
        ("can_edit", "تعديل"),
        ("can_delete", "حذف"),
        ("can_print", "طباعة"),
        ("can_cancel", "إلغاء"),
    ]
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.current_user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ تخزين ID الدور (بدلاً من ORM)
        self.selected_role_id: Optional[int] = None
        self.selected_role_name: str = ""
        
        # ✅ dicts
        self.roles_data: List[Dict] = []
        self.permissions_data: Dict[str, Dict[str, bool]] = {}
        # ✅ الوحدات الفعلية (من السيرفر في remote أو self.MODULES في local)
        self._active_modules: List[str] = list(self.MODULES)

        # ✅ منع الحفظ قبل التحميل
        self._is_loaded = False
        
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
        header_label = QLabel("إدارة الصلاحيات والأدوار")
        header_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(header_label)
        
        sub_label = QLabel("مصفوفة الصلاحيات التفاعلية")
        sub_label.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(sub_label)

        # بطاقة الأدوار
        roles_card = QFrame()
        roles_card.setObjectName("rolesCard")
        roles_card.setStyleSheet("""
            QFrame#rolesCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 10px 15px;
            }
        """)
        roles_card.setFixedHeight(200)

        roles_H = QHBoxLayout(roles_card)

        roles_title_buttons = QVBoxLayout()
 
        roles_title = QLabel("أدوار النظام")
        roles_title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        roles_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        roles_title_buttons.addWidget(roles_title)

        roles_title_buttons.addStretch()
        
        roles_buttons = QHBoxLayout()

        add_role_btn = GradientButton("إضافة دور", "fa5s.plus")
        add_role_btn.clicked.connect(self.add_role)
        roles_title_buttons.addWidget(add_role_btn)
        
        edit_role_btn = GradientButton("تعديل", "fa5s.edit")
        edit_role_btn.setObjectName("warningButton")
        edit_role_btn.clicked.connect(self.edit_role)
        roles_buttons.addWidget(edit_role_btn)
        
        delete_role_btn = GradientButton("حذف", "fa5s.trash")
        delete_role_btn.setObjectName("dangerButton")
        delete_role_btn.clicked.connect(self.delete_role)
        roles_buttons.addWidget(delete_role_btn)

        roles_title_buttons.addLayout(roles_buttons)        

        roles_H.addLayout(roles_title_buttons, 1)

        # قائمة الأدوار
        self.roles_list = QListWidget()
        self.roles_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background: #F1F5F9;
            }
            QListWidget::item:selected {
                background: #1976D3;
                color: white;
            }
        """)
        self.roles_list.itemClicked.connect(self.select_role)
        roles_H.addWidget(self.roles_list, 1)
        
        main_layout.addWidget(roles_card)
        
        # بطاقة مصفوفة الصلاحيات
        self.matrix_card = Card()
        self.matrix_card.setObjectName("tableCard")
        
        matrix_title = QLabel("مصفوفة الصلاحيات")
        matrix_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0F172A;")
        self.matrix_card.add_widget(matrix_title)
        
        # جدول الصلاحيات
        self.permissions_table = QTableWidget()
        self.permissions_table.setColumnCount(len(self.PERMISSION_KEYS) + 1)
        self.permissions_table.setHorizontalHeaderLabels(
            ["الوحدة"] + [label for _, label in self.PERMISSION_KEYS]
        )
        self.permissions_table.setColumnWidth(0, 150)
        self.permissions_table.horizontalHeader().setStretchLastSection(True)
        self.matrix_card.add_widget(self.permissions_table)
        
        # زر حفظ الصلاحيات
        self.save_btn = GradientButton("حفظ الصلاحيات", "fa5s.save")
        self.save_btn.clicked.connect(self.save_permissions)
        self.save_btn.setEnabled(False)  # ✅ معطّل حتى اختيار دور
        self.matrix_card.add_widget(self.save_btn)
        
        main_layout.addWidget(self.matrix_card)
    
    # ============================================================
    # ✅ التحميل غير المتزامن - الأدوار
    # ============================================================
    
    def load_data(self):
        """تحميل الأدوار - Local أو Remote."""
        self.loading_overlay.show_loading("جاري تحميل الأدوار...")

        def _fetch_data():
            if PermissionsFactory.is_remote():
                service = PermissionsFactory.get_service()
                return service.list_roles()
            with session_scope() as session:
                roles = session.execute(
                    select(Role).order_by(Role.role_name)
                ).scalars().all()
                return [
                    {
                        'id': r.id,
                        'name': r.role_name or '',
                        'description': r.description or '',
                    }
                    for r in roles
                ]

        def _on_result(data):
            try:
                self.roles_data = data
                self.roles_list.clear()
                for role in data:
                    item = QListWidgetItem(role['name'])
                    item.setData(Qt.ItemDataRole.UserRole, role['id'])
                    self.roles_list.addItem(item)
            except Exception as e:
                print(f"خطأ: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            ErrorDialog(
                "خطأ",
                f"فشل تحميل الأدوار:\n{error_msg}",
                self
            ).exec()

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
        
    # ============================================================
    # ✅ اختيار دور - تحميل الصلاحيات (Async)
    # ============================================================
    
    def select_role(self, item: QListWidgetItem):
        """اختيار دور - تحميل صلاحياته."""
        role_id = item.data(Qt.ItemDataRole.UserRole)
        
        # ✅ البحث في القائمة المحفوظة
        role = next(
            (r for r in self.roles_data if r['id'] == role_id),
            None
        )
        if not role:
            return
        
        self.selected_role_id = role_id
        self.selected_role_name = role['name']
        
        # ✅ تفعيل زر الحفظ
        self.save_btn.setEnabled(True)
        
        # ✅ تحميل الصلاحيات في الخلفية
        self._load_role_permissions(role_id)
    
    def _load_role_permissions(self, role_id: int):
        """تحميل صلاحيات الدور - Local أو Remote."""
        self.loading_overlay.show_loading("جاري تحميل الصلاحيات...")

        def _fetch_data():
            if PermissionsFactory.is_remote():
                service = PermissionsFactory.get_service()
                data = service.get_role_matrix(role_id)
                return {
                    'modules': data.get('modules', []),
                    'matrix': data.get('matrix', {}),
                }
            with session_scope() as session:
                role_permissions = session.execute(
                    select(RolePermission, Permission)
                    .join(
                        Permission,
                        RolePermission.permission_id == Permission.id
                    )
                    .where(RolePermission.role_id == role_id)
                ).all()

                matrix = {}
                for rp, perm in role_permissions:
                    matrix[perm.module_name] = {
                        'can_view': bool(rp.can_view),
                        'can_add': bool(rp.can_add),
                        'can_edit': bool(rp.can_edit),
                        'can_delete': bool(rp.can_delete),
                        'can_print': bool(rp.can_print),
                        'can_cancel': bool(rp.can_cancel),
                    }

                return {
                    'modules': list(self.MODULES),
                    'matrix': matrix,
                }

        def _on_result(data):
            try:
                # ✅ استخدم قائمة الوحدات من السيرفر
                if data.get('modules'):
                    self._active_modules = list(data['modules'])
                else:
                    self._active_modules = list(self.MODULES)

                self.permissions_data = data.get('matrix', {})
                self._display_permissions(self.permissions_data)
                self._is_loaded = True
            except Exception as e:
                print(f"خطأ: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            ErrorDialog(
                "خطأ",
                f"فشل تحميل الصلاحيات:\n{error_msg}",
                self
            ).exec()

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)

    def _display_permissions(self, permissions_map: Dict[str, Dict[str, bool]]):
        """عرض مصفوفة الصلاحيات (يستخدم self._active_modules)."""
        modules = self._active_modules or list(self.MODULES)
        self.permissions_table.setRowCount(len(modules))

        for row, module in enumerate(modules):
            self.permissions_table.setItem(
                row, 0, QTableWidgetItem(module)
            )

            module_perms = permissions_map.get(module, {})

            for col, (key, _) in enumerate(self.PERMISSION_KEYS, start=1):
                checkbox_widget = QWidget()
                checkbox_widget.setStyleSheet("background: transparent;")
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

                checkbox = QCheckBox()
                checkbox.setChecked(bool(module_perms.get(key, False)))

                checkbox.setStyleSheet("""
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                        border: 2px solid #CBD5E1;
                        border-radius: 4px;
                        background: white;
                    }
                    QCheckBox::indicator:hover {
                        border-color: #1976D3;
                    }
                    QCheckBox::indicator:checked {
                        background: #1976D3;
                        border-color: #1976D3;
                    }
                """)
                checkbox_layout.addWidget(checkbox)
                self.permissions_table.setCellWidget(row, col, checkbox_widget)

            self.permissions_table.setRowHeight(row, 35)

    # ============================================================
    # ✅ العمليات - الأدوار
    # ============================================================
    
    def add_role(self):
        """إضافة دور جديد."""
        if self.permission_service and not self.permission_service.can_add("الصلاحيات"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للإضافة في الصلاحيات"
            )
            return

        dialog = RoleDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            SuccessDialog("نجاح", "تم إضافة الدور بنجاح", self).exec()
    
    def edit_role(self):
        if self.permission_service and not self.permission_service.can_edit("الصلاحيات"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية للتعديل في الصلاحيات")
            return

        current_item = self.roles_list.currentItem()
        if not current_item:
            ErrorDialog("تنبيه", "اختر دوراً", self).exec()
            return

        role_id = current_item.data(Qt.ItemDataRole.UserRole)

        def _fetch():
            if PermissionsFactory.is_remote():
                # اجلب من roles_data
                return next(
                    (r for r in self.roles_data if r['id'] == role_id),
                    None,
                )
            with session_scope() as session:
                role = session.get(Role, role_id)
                if not role:
                    return None
                return {
                    'id': role.id,
                    'role_name': role.role_name or '',
                    'description': role.description or '',
                }

        def _ok(role_data):
            if not role_data:
                ErrorDialog("خطأ", "الدور غير موجود", self).exec()
                return
            dialog = RoleDialog(role_data=role_data, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_data()
                SuccessDialog("نجاح", "تم التحديث", self).exec()

        def _err(m):
            ErrorDialog("خطأ", str(m), self).exec()

        run_async(_fetch, on_result=_ok, on_error=_err)

    def delete_role(self):
        """حذف دور"""
        if self.permission_service and not self.permission_service.can_delete("الصلاحيات"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للحذف في الصلاحيات"
            )
            return

        current_item = self.roles_list.currentItem()
        if not current_item:
            ErrorDialog("تنبيه", "اختر دوراً", self).exec()
            return

        role_id = current_item.data(Qt.ItemDataRole.UserRole)
        role_name = current_item.text()

        from app.views.widgets.dialogs import ConfirmationDialog
        dialog = ConfirmationDialog(
            "حذف دور",
            f"هل تريد حذف الدور: {role_name}؟\n\n"
            "⚠️ سيتم حذف جميع صلاحيات هذا الدور!",
            self
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        def _do():
            if PermissionsFactory.is_remote():
                PermissionsFactory.get_service().delete_role(role_id)
            else:
                with session_scope() as session:
                    role = session.get(Role, role_id)
                    if role:
                        rps = session.query(RolePermission).filter(
                            RolePermission.role_id == role_id
                        ).all()
                        for rp in rps:
                            session.delete(rp)
                        session.delete(role)
                        session.commit()

        def _ok(_):
            SuccessDialog("نجاح", "تم حذف الدور", self).exec()
            self.selected_role_id = None
            self.save_btn.setEnabled(False)
            self.permissions_table.setRowCount(0)
            self._is_loaded = False
            self.load_data()

        def _err(m):
            ErrorDialog("خطأ", f"فشل: {m}", self).exec()

        run_async(_do, on_result=_ok, on_error=_err)
    
    # ============================================================
    # ✅ حفظ الصلاحيات (Async)
    # ============================================================
    
    def save_permissions(self):
        """حفظ الصلاحيات - Local أو Remote."""
        if self.permission_service and not self.permission_service.can_add("الصلاحيات"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية للإضافة في الصلاحيات")
            return

        if not self.selected_role_id:
            ErrorDialog("تنبيه", "اختر دوراً", self).exec()
            return
        if not self._is_loaded:
            ErrorDialog("تنبيه", "انتظر التحميل", self).exec()
            return

        # ✅ جمع البيانات (باستخدام self._active_modules)
        modules = self._active_modules or list(self.MODULES)
        matrix_records = []

        for row, module in enumerate(modules):
            perms = {}
            for col, (key, _) in enumerate(self.PERMISSION_KEYS, start=1):
                w = self.permissions_table.cellWidget(row, col)
                if w:
                    cb = w.findChild(QCheckBox)
                    if cb:
                        perms[key] = cb.isChecked()

            matrix_records.append({
                'module': module,
                'can_view': perms.get('can_view', False),
                'can_add': perms.get('can_add', False),
                'can_edit': perms.get('can_edit', False),
                'can_delete': perms.get('can_delete', False),
                'can_print': perms.get('can_print', False),
                'can_cancel': perms.get('can_cancel', False),
            })

        reply = QMessageBox.question(
            self, "تأكيد الحفظ",
            f"حفظ صلاحيات الدور: {self.selected_role_name}؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.loading_overlay.show_loading("جاري حفظ الصلاحيات...")
        role_id = self.selected_role_id

        def _save_data():
            if PermissionsFactory.is_remote():
                service = PermissionsFactory.get_service()
                service.save_role_matrix(
                    role_id, {'matrix': matrix_records}
                )
                return True

            # Local
            with session_scope() as session:
                # 1. جلب الموجود
                existing_rows = session.execute(
                    select(RolePermission, Permission)
                    .join(
                        Permission,
                        RolePermission.permission_id == Permission.id
                    )
                    .where(RolePermission.role_id == role_id)
                ).all()

                existing_map = {}
                for rp, perm in existing_rows:
                    existing_map[perm.module_name] = (rp, perm)

                incoming = set()

                for item in matrix_records:
                    module = item['module']
                    incoming.add(module)

                    if module in existing_map:
                        rp, perm = existing_map[module]
                        rp.can_view = item['can_view']
                        rp.can_add = item['can_add']
                        rp.can_edit = item['can_edit']
                        rp.can_delete = item['can_delete']
                        rp.can_print = item['can_print']
                        rp.can_cancel = item['can_cancel']
                    else:
                        perm = session.execute(
                            select(Permission).where(
                                Permission.module_name == module
                            )
                        ).scalar_one_or_none()
                        if not perm:
                            perm = Permission(
                                module_name=module,
                                permission_key=f"module_{module}",
                            )
                            session.add(perm)
                            session.flush()

                        session.add(RolePermission(
                            role_id=role_id,
                            permission_id=perm.id,
                            can_view=item['can_view'],
                            can_add=item['can_add'],
                            can_edit=item['can_edit'],
                            can_delete=item['can_delete'],
                            can_print=item['can_print'],
                            can_cancel=item['can_cancel'],
                        ))

                # احذف الوحدات المحذوفة
                for module, (rp, perm) in existing_map.items():
                    if module not in incoming:
                        session.delete(rp)

                session.commit()
            return True

        def _on_result(_):
            self.loading_overlay.hide_loading()
            SuccessDialog("نجاح", "تم حفظ الصلاحيات", self).exec()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            ErrorDialog("خطأ", f"فشل:\n{error_msg}", self).exec()

        run_async(_save_data, on_result=_on_result, on_error=_on_error)

    # ============================================================
    # ✅ الأحداث
    # ============================================================
    
    def resizeEvent(self, event):
        """تحديث حجم طبقة التحميل."""
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())
    
    def refresh(self):
        self.selected_role_id = None
        self.selected_role_name = ""
        self.save_btn.setEnabled(False)
        self.permissions_table.setRowCount(0)
        self._is_loaded = False
        self._active_modules = list(self.MODULES)
        self.load_data()


# ============================================================
# ✅ نافذة إضافة/تعديل دور (مع dicts)
# ============================================================

class RoleDialog(ModernDialog):
    """نافذة إضافة/تعديل دور."""
    
    def __init__(self, role_data: Optional[dict] = None, parent=None):
        super().__init__(
            "تعديل دور" if role_data else "إضافة دور جديد",
            "fa5s.shield-alt",
            parent,
            width=400,
            height=350
        )
        
        # ✅ تخزين dict بدلاً من ORM
        self.role_data = role_data
        self.role_id = role_data['id'] if role_data else None
        
        self.setup_form()
        
        # ✅ تعبئة البيانات إذا كان تعديل
        if role_data:
            self._fill_role_data()
    
    def setup_form(self):
        """إعداد النموذج."""
        # اسم الدور
        self.add_widget(self._create_label("اسم الدور:"))
        self.role_name_input = QLineEditPlus("مثال: محاسب، معلم...")
        self.add_widget(self.role_name_input)
        
        # الوصف
        self.add_widget(self._create_label("الوصف:"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(60)
        self.add_widget(self.description_input)
        
        # الأزرار
        self.add_button("حفظ", self.save_role, "primary")
        self.add_button("إلغاء", self.reject, "default")
    
    def _create_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            "color: #475569; font-weight: 600; font-size: 12px;"
        )
        return label
    
    def _fill_role_data(self):
        """تعبئة بيانات الدور للتعديل."""
        if not self.role_data:
            return
        
        self.role_name_input.setText(self.role_data['name'])
        self.description_input.setPlainText(self.role_data['description'])
    
    def save_role(self):
        """حفظ الدور - Local أو Remote."""
        if not self.role_name_input.text().strip():
            ErrorDialog("تنبيه", "أدخل اسم الدور", self).exec()
            return

        payload = {
            'role_name': self.role_name_input.text().strip(),
            'description': (
                self.description_input.toPlainText().strip() or None
            ),
        }

        def _do():
            if PermissionsFactory.is_remote():
                service = PermissionsFactory.get_service()
                if self.role_id:
                    service.update_role(self.role_id, payload)
                else:
                    service.create_role(payload)
                return True

            # Local
            with session_scope() as session:
                if self.role_id:
                    role = session.get(Role, self.role_id)
                    if not role:
                        raise Exception("الدور غير موجود")
                else:
                    existing = session.execute(
                        select(Role).where(
                            Role.role_name == payload['role_name']
                        )
                    ).scalar_one_or_none()
                    if existing:
                        raise Exception("اسم الدور موجود مسبقاً")
                    role = Role()
                    session.add(role)

                role.role_name = payload['role_name']
                if hasattr(role, 'description'):
                    role.description = payload['description']
                session.commit()
            return True

        def _ok(_):
            self.accept()

        def _err(m):
            ErrorDialog("خطأ", f"فشل: {m}", self).exec()

        run_async(_do, on_result=_ok, on_error=_err)
