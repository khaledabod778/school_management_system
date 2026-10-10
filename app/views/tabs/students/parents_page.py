"""
واجهة إدارة أولياء الأمور - Local أو Remote.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta
from sqlalchemy import select, func

from app.services.permission_service import PermissionService
from app.services.parent_factory import ParentFactory
from app.views.widgets.custom_widgets import (
    GradientButton, IconButton, QLineEditPlus, SearchBox
)
from app.views.widgets.dialogs import (
    ModernDialog, SuccessDialog, ConfirmationDialog
)
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class ParentsPage(QWidget):
    """صفحة إدارة أولياء الأمور - Local أو Remote."""

    def __init__(self, user, academic_year,
                 permission_service: Optional[PermissionService] = None,
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service

        self.all_parents: List[Dict] = []
        self.current_filtered_parents: List[Dict] = []

        self.setup_ui()
        self.loading_overlay = LoadingOverlay(self)

        QTimer.singleShot(100, self.load_data)

    def setup_ui(self):
        """إعداد الواجهة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        title = QLabel("إدارة أولياء الأمور")
        title.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #0F172A;"
        )
        main_layout.addWidget(title)

        # بحث
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

        self.search_input = SearchBox("بحث عن ولي أمر...")
        self.search_input.textChanged.connect(self.filter_parents)
        filter_layout.addWidget(self.search_input)
        filter_layout.addStretch()

        add_btn = GradientButton("إضافة ولي أمر", "fa5s.plus")
        add_btn.clicked.connect(self.add_parent)
        filter_layout.addWidget(add_btn)

        main_layout.addWidget(filter_card)

        # الجدول
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
        table_layout = QVBoxLayout(table_card)

        toolbar = QHBoxLayout()
        self.count_label = QLabel("عدد أولياء الأمور: 0")
        self.count_label.setObjectName("count_label")
        toolbar.addWidget(self.count_label)
        toolbar.addStretch()

        edit_btn = IconButton('fa5s.edit', "تعديل", color='#1976D3')
        edit_btn.clicked.connect(self.edit_parents)
        toolbar.addWidget(edit_btn)

        delete_btn = IconButton('fa5s.trash', "حذف", color='#EF4444')
        delete_btn.clicked.connect(self.delete_parents)
        toolbar.addWidget(delete_btn)

        table_layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "الاسم", "الهاتف الرئيسي", "الهاتف الثانوي",
            "الوظيفة", "الفئة", "العنوان"
        ])
        self.table.setColumnWidth(0, 220)
        self.table.setColumnWidth(1, 130)
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 150)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.edit_parents)
        table_layout.addWidget(self.table)

        main_layout.addWidget(table_card)

    # ============================================================
    # ✅ التحميل
    # ============================================================

    def load_data(self):
        """تحميل البيانات (Local أو Remote)."""
        self.loading_overlay.show_loading("جاري تحميل أولياء الأمور...")

        def _fetch_data():
            if ParentFactory.is_remote():
                service = ParentFactory.get_service()
                return service.list_parents()
            else:
                # Local
                from app.database.session import session_scope
                from app.database.models import Parent
                with session_scope() as session:
                    parents = session.execute(
                        select(Parent)
                        .where(Parent.deleted_at.is_(None))
                        .order_by(Parent.full_name)
                    ).scalars().all()
                    return [
                        {
                            'id': p.id,
                            'full_name': p.full_name or '',
                            'primary_phone': p.primary_phone or '',
                            'secondary_phone': p.secondary_phone or '',
                            'job': p.job or '',
                            'category': p.category or 'عادي',
                            'address': p.address or '',
                        }
                        for p in parents
                    ]

        def _on_result(data):
            try:
                self.all_parents = data
                self.current_filtered_parents = list(self.all_parents)
                self.display_parents(self.all_parents)
            except Exception as e:
                print(f"خطأ في تحديث الواجهة: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(
                self, "خطأ",
                f"فشل تحميل البيانات:\n{error_msg}"
            )
            self.all_parents = []
            self.current_filtered_parents = []
            self.display_parents([])

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)

    def display_parents(self, parents: List[Dict]):
        """عرض أولياء الأمور."""
        self.table.setRowCount(len(parents))

        category_colors = {
            'عادي': '#64748B',
            'VIP': '#F59E0B',
            'كفالة': '#10B981',
        }

        for row, parent in enumerate(parents):
            self.table.setItem(
                row, 0, QTableWidgetItem(parent.get('full_name', ''))
            )
            self.table.setItem(
                row, 1, QTableWidgetItem(parent.get('primary_phone', ''))
            )
            self.table.setItem(
                row, 2, QTableWidgetItem(parent.get('secondary_phone', '') or '')
            )
            self.table.setItem(
                row, 3, QTableWidgetItem(parent.get('job', '') or '')
            )

            category_item = QTableWidgetItem(parent.get('category', 'عادي'))
            category_item.setForeground(
                QColor(category_colors.get(
                    parent.get('category', 'عادي'), '#64748B'
                ))
            )
            self.table.setItem(row, 4, category_item)

            self.table.setItem(
                row, 5, QTableWidgetItem(parent.get('address', '') or '')
            )
            self.table.setRowHeight(row, 35)

        self.count_label.setText(f"عدد أولياء الأمور: {len(parents)}")

    def filter_parents(self):
        """تصفية محلية."""
        search_text = self.search_input.text().lower().strip()

        filtered = []
        for parent in self.all_parents:
            if search_text:
                name = (parent.get('full_name') or '').lower()
                phone = parent.get('primary_phone') or ''
                if search_text not in name and search_text not in phone:
                    continue
            filtered.append(parent)

        self.current_filtered_parents = filtered
        self.display_parents(filtered)

    def get_selected_parent_id(self) -> Optional[int]:
        """ID ولي الأمر المحدد."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار ولي أمر أولاً")
            return None
        if current_row >= len(self.current_filtered_parents):
            return None
        return self.current_filtered_parents[current_row]['id']

    # ============================================================
    # ✅ العمليات
    # ============================================================

    def add_parent(self):
        """إضافة ولي أمر."""
        if (self.permission_service
                and not self.permission_service.can_add("أولياء الأمور")):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للإضافة في أولياء الأمور"
            )
            return

        dialog = ParentDialog(self.user, parent_data=None, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.filter_parents()
            SuccessDialog("نجاح", "تم إضافة ولي أمر بنجاح", self).exec()

    def edit_parents(self):
        """تعديل ولي أمر."""
        if (self.permission_service
                and not self.permission_service.can_edit("أولياء الأمور")):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للتعديل في أولياء الأمور"
            )
            return

        parent_id = self.get_selected_parent_id()
        if not parent_id:
            return

        try:
            parent_data = self._load_parent_for_dialog(parent_id)
            if not parent_data:
                QMessageBox.warning(
                    self, "تنبيه", "ولي الأمر غير موجود"
                )
                return
        except Exception as e:
            QMessageBox.critical(
                self, "خطأ", f"فشل تحميل البيانات: {str(e)}"
            )
            return

        dialog = ParentDialog(
            self.user, parent_data=parent_data, parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.filter_parents()
            SuccessDialog(
                "نجاح", "تم تحديث بيانات ولي الأمر بنجاح", self
            ).exec()

    def _load_parent_for_dialog(self, parent_id: int) -> Optional[Dict]:
        """تحميل بيانات ولي الأمر."""
        if ParentFactory.is_remote():
            service = ParentFactory.get_service()
            return service.get(parent_id)
        else:
            from app.database.session import session_scope
            from app.database.models import Parent
            with session_scope() as session:
                parent = session.get(Parent, parent_id)
                if not parent:
                    return None
                return {
                    'id': parent.id,
                    'full_name': parent.full_name or '',
                    'primary_phone': parent.primary_phone or '',
                    'secondary_phone': parent.secondary_phone or '',
                    'job': parent.job or '',
                    'category': parent.category or 'عادي',
                    'address': parent.address or '',
                }

    def delete_parents(self):
        """حذف ولي أمر."""
        if (self.permission_service
                and not self.permission_service.can_delete("أولياء الأمور")):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للحذف في أولياء الأمور"
            )
            return

        parent_id = self.get_selected_parent_id()
        if not parent_id:
            return

        parent_data = self._load_parent_for_dialog(parent_id)
        if not parent_data:
            return

        dialog = ConfirmationDialog(
            "حذف ولي أمر",
            f"هل أنت متأكد من حذف ولي الأمر:\n"
            f"{parent_data['full_name']}؟",
            self,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        def _do_delete():
            if ParentFactory.is_remote():
                service = ParentFactory.get_service()
                service.delete(parent_id)
            else:
                from app.database.session import session_scope
                from app.database.models import Parent
                with session_scope() as session:
                    parent = session.get(Parent, parent_id)
                    if parent:
                        session.delete(parent)

        try:
            _do_delete()
            SuccessDialog("نجاح", "تم حذف ولي الأمر بنجاح", self).exec()
            self.load_data()
            self.filter_parents()
        except Exception as e:
            QMessageBox.critical(
                self, "خطأ", f"فشل حذف ولي الأمر: {str(e)}"
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())

    def refresh(self):
        self.load_data()
        self.filter_parents()


# ============================================================
# ✅ ParentDialog - Local أو Remote
# ============================================================

class ParentDialog(ModernDialog):
    """نافذة إضافة/تعديل ولي أمر."""

    def __init__(self, user, parent_data: Optional[dict] = None,
                 parent=None):
        super().__init__(
            "تعديل ولي أمر" if parent_data else "إضافة ولي أمر",
            "fa5s.user-friends",
            parent,
            width=500,
            height=650,
        )
        self.user = user
        self.parent_data = parent_data
        self.parent_id = parent_data['id'] if parent_data else None

        self.setup_form()

    def setup_form(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("الاسم الكامل:"))
        self.name_input = QLineEditPlus(placeholder="أدخل الاسم الكامل")
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("رقم الهاتف الرئيسي:"))
        self.phone_input = QLineEditPlus(placeholder="مثال: 777777777")
        layout.addWidget(self.phone_input)

        layout.addWidget(QLabel("رقم الهاتف الثانوي:"))
        self.phone2_input = QLineEditPlus(placeholder="اختياري")
        layout.addWidget(self.phone2_input)

        layout.addWidget(QLabel("العنوان:"))
        self.address_input = QLineEditPlus(placeholder="اختياري")
        layout.addWidget(self.address_input)

        layout.addWidget(QLabel("الوظيفة:"))
        self.job_input = QLineEditPlus(placeholder="اختياري")
        layout.addWidget(self.job_input)

        layout.addWidget(QLabel("الفئة:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["عادي", "VIP", "كفالة"])
        layout.addWidget(self.category_combo)

        layout.addWidget(QLabel("كلمة المرور:"))
        self.password_input = QLineEditPlus()
        if self.parent_id:
            self.password_input.setPlaceholderText(
                "اتركها فارغة لعدم التغيير"
            )
        else:
            self.password_input.setPlaceholderText(
                "اتركها فارغة لكلمة المرور الافتراضية (123456)"
            )
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.add_layout(layout)
        self.add_button("إلغاء", self.reject, "default")
        self.add_button("حفظ", self.save_parent, "primary")

        if self.parent_data:
            self._load_parent_data()

    def _load_parent_data(self):
        if not self.parent_data:
            return
        self.name_input.setText(self.parent_data.get('full_name', ''))
        self.phone_input.setText(self.parent_data.get('primary_phone', ''))
        self.phone2_input.setText(
            self.parent_data.get('secondary_phone', '') or ''
        )
        self.address_input.setText(
            self.parent_data.get('address', '') or ''
        )
        self.job_input.setText(self.parent_data.get('job', '') or '')
        self.category_combo.setCurrentText(
            self.parent_data.get('category', 'عادي')
        )

    def save_parent(self):
        """حفظ - Local أو Remote."""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال الاسم")
            return
        if not self.phone_input.text().strip():
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال رقم الهاتف")
            return

        payload = {
            'full_name': self.name_input.text().strip(),
            'primary_phone': self.phone_input.text().strip(),
            'secondary_phone': (
                self.phone2_input.text().strip() or None
            ),
            'address': self.address_input.text().strip() or None,
            'job': self.job_input.text().strip() or None,
            'category': self.category_combo.currentText(),
            'password': self.password_input.text() or None,
        }

        try:
            if ParentFactory.is_remote():
                service = ParentFactory.get_service()
                if self.parent_id:
                    service.update(self.parent_id, payload)
                else:
                    service.create(payload)
            else:
                self._save_local(payload)

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل الحفظ: {str(e)}")

    def _save_local(self, payload: dict):
        """حفظ في Local DB (legacy)."""
        from app.database.session import session_scope
        from app.database.models import Parent
        from app.services.auth_service import AuthService
        from sqlalchemy import select

        with session_scope() as session:
            if self.parent_id:
                parent = session.get(Parent, self.parent_id)
                if not parent:
                    raise Exception("ولي الأمر غير موجود")

                # فحص التكرار
                existing = session.execute(
                    select(Parent).where(
                        Parent.primary_phone == payload['primary_phone'],
                        Parent.id != self.parent_id,
                    )
                ).scalar_one_or_none()
                if existing:
                    raise Exception("رقم الهاتف مسجل مسبقاً")
            else:
                existing = session.execute(
                    select(Parent).where(
                        Parent.primary_phone == payload['primary_phone']
                    )
                ).scalar_one_or_none()
                if existing:
                    raise Exception("رقم الهاتف مسجل مسبقاً")
                parent = Parent()
                session.add(parent)

            parent.full_name = payload['full_name']
            parent.primary_phone = payload['primary_phone']
            parent.secondary_phone = payload['secondary_phone']
            parent.address = payload['address']
            parent.job = payload['job']
            parent.category = payload['category']

            if payload['password']:
                result = AuthService.hash_password(payload['password'])
                parent.password_hash = (
                    result[0] if isinstance(result, tuple) else result
                )
            elif not self.parent_id:
                result = AuthService.hash_password("123456")
                parent.password_hash = (
                    result[0] if isinstance(result, tuple) else result
                )

            session.flush()