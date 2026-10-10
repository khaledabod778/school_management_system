"""
واجهة دليل المواد الدراسية - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta
from decimal import Decimal

from app.database.session import session_scope
from app.database.models import Subject
from sqlalchemy import select

from app.services.academic_factory import AcademicFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    GradientButton, QDoubleSpinBoxEN, QLineEditPlus
)
from app.views.widgets.dialogs import ModernDialog
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class SubjectsPage(QWidget):
    """صفحة دليل المواد الدراسية - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ dicts بدلاً من ORM objects
        self.all_subjects: List[Dict] = []
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل البيانات في الخلفية
        QTimer.singleShot(100, self.load_data)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)
        
        title = QLabel("دليل المواد الدراسية")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        # بطاقة الجدول
        tableCard = QFrame()
        tableCard.setObjectName("tableCard")
        tableCard.setStyleSheet("""
            QFrame#tableCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        card_layout = QVBoxLayout(tableCard)
        
        toolbar = QHBoxLayout()
        
        self.count_label = QLabel("عدد المواد: 0")
        self.count_label.setObjectName("count_label")
        toolbar.addWidget(self.count_label)
        
        toolbar.addStretch()
        
        add_btn = GradientButton("إضافة مادة", "fa5s.plus")
        add_btn.clicked.connect(self.add_subject)
        toolbar.addWidget(add_btn)
        
        card_layout.addLayout(toolbar)
        
        # الجدول
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "اسم المادة", "درجة النجاح", "الدرجة الكبرى", "إجراء"
        ])
        self.table.setColumnWidth(0, 250)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 150)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        card_layout.addWidget(self.table)
        
        main_layout.addWidget(tableCard)
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_data(self):
        """تحميل - Local أو Remote."""
        self.loading_overlay.show_loading("جاري تحميل المواد...")

        def _fetch():
            if AcademicFactory.is_remote():
                service = AcademicFactory.get_service()
                return service.list_subjects()
            else:
                from app.database.session import session_scope
                from app.database.models import Subject
                from sqlalchemy import select
                with session_scope() as session:
                    subjects = session.execute(
                        select(Subject).order_by(Subject.subject_name)
                    ).scalars().all()
                    return [
                        {
                            'id': s.id,
                            'subject_name': s.subject_name or '',
                            'min_pass_score': float(s.min_pass_score or 0),
                            'max_score': float(s.max_score or 0),
                        }
                        for s in subjects
                    ]

        def _on_ok(data):
            try:
                self.all_subjects = data
                self.display_subjects()
            finally:
                self.loading_overlay.hide_loading()

        def _on_err(msg):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(self, "خطأ", f"فشل: {msg}")
            self.all_subjects = []

        run_async(_fetch, on_result=_on_ok, on_error=_on_err)
        
    # ============================================================
    # ✅ عرض البيانات
    # ============================================================
    
    def display_subjects(self):
        """عرض المواد."""
        self.table.setRowCount(len(self.all_subjects))
        
        for row, subject in enumerate(self.all_subjects):
            self.table.setItem(
                row, 0, QTableWidgetItem(subject['subject_name'])
            )
            self.table.setItem(
                row, 1, QTableWidgetItem(f"{subject['min_pass_score']:g}")
            )
            self.table.setItem(
                row, 2, QTableWidgetItem(f"{subject['max_score']:g}")
            )

            # أزرار الإجراء
            action_widget = QWidget()
            action_widget.setStyleSheet("background: transparent;")
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 0, 5, 0)
            action_layout.setSpacing(5)

            # زر التعديل
            edit_btn = QPushButton("تعديل")
            edit_btn.setObjectName("warningButton")
            edit_btn.setStyleSheet("""
                QPushButton#warningButton {
                    background: #F59E0B;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton#warningButton:hover {
                    background: #D97706;
                }
            """)
            # ✅ تمرير ID فقط
            edit_btn.clicked.connect(
                lambda checked, sid=subject['id']: self.edit_subject(sid)
            )
            action_layout.addWidget(edit_btn)

            # زر الحذف
            delete_btn = QPushButton("حذف")
            delete_btn.setObjectName("dangerButton")
            delete_btn.setStyleSheet("""
                QPushButton#dangerButton {
                    background: #EF4444;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton#dangerButton:hover {
                    background: #DC2626;
                }
            """)
            delete_btn.clicked.connect(
                lambda checked, sid=subject['id']: self.delete_subject(sid)
            )
            action_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 3, action_widget)
            self.table.setRowHeight(row, 45)
        
        self.count_label.setText(f"عدد المواد: {len(self.all_subjects)}")
    
    # ============================================================
    # ✅ العمليات (إضافة / تعديل / حذف)
    # ============================================================
    
    def add_subject(self):
        """إضافة مادة."""
        if self.permission_service and not self.permission_service.can_add("التهيئة الأكاديمية"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للإضافة في التهيئة الأكاديمية"
            )
            return
                
        dialog = SubjectDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            QMessageBox.information(self, "نجاح", "تم إضافة المادة بنجاح")
    
    def edit_subject(self, subject_id: int):
        """تعديل مادة (باستخدام ID)."""
        if self.permission_service and not self.permission_service.can_edit("التهيئة الأكاديمية"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للتعديل في التهيئة الأكاديمية"
            )
            return
        
        # ✅ إعادة تحميل من قاعدة البيانات
        try:
            with session_scope() as session:
                subject = session.get(Subject, subject_id)
                if not subject:
                    QMessageBox.warning(self, "تنبيه", "المادة غير موجودة")
                    return
                
                # ✅ تحويل إلى dict
                subject_data = {
                    'id': subject.id,
                    'subject_name': subject.subject_name or '',
                    'min_pass_score': float(subject.min_pass_score or 0),
                    'max_score': float(subject.max_score or 0),
                }
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل تحميل البيانات: {str(e)}")
            return
        
        dialog = SubjectDialog(subject_data=subject_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            QMessageBox.information(self, "نجاح", "تم تحديث المادة بنجاح")

    def delete_subject(self, subject_id: int):
        if (self.permission_service
                and not self.permission_service.can_delete("التهيئة الأكاديمية")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return
        try:
            # اجلب الاسم للعرض
            name = next(
                (s['subject_name'] for s in self.all_subjects
                 if s['id'] == subject_id), ''
            )
            reply = QMessageBox.warning(
                self, "تأكيد الحذف",
                f"هل أنت متأكد من حذف المادة:\n{name}؟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

            if AcademicFactory.is_remote():
                service = AcademicFactory.get_service()
                service.delete_subject(subject_id)
            else:
                from app.database.session import session_scope
                from app.database.models import Subject
                with session_scope() as session:
                    s = session.get(Subject, subject_id)
                    if s:
                        session.delete(s)
            QMessageBox.information(self, "نجاح", "تم الحذف")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل: {e}")

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
# ✅ نافذة إضافة/تعديل مادة (مع dicts)
# ============================================================

class SubjectDialog(ModernDialog):
    """نافذة إضافة/تعديل مادة."""
    
    def __init__(self, subject_data: Optional[dict] = None, parent=None):
        super().__init__(
            "تعديل مادة" if subject_data else "إضافة مادة",
            "fa5s.book",  # ✅ أيقونة مناسبة للمواد
            parent,
            width=500,
            height=400
        )
        # ✅ تخزين dict بدلاً من ORM object
        self.subject_data = subject_data
        self.subject_id = subject_data['id'] if subject_data else None

        self.setup_ui()
        
        if subject_data:
            self.load_subject_data()

    def setup_ui(self):
        """إعداد النموذج."""    
        
        self.add_widget(QLabel("اسم المادة:"))
        self.name_input = QLineEditPlus()
        self.add_widget(self.name_input)
        
        self.add_widget(QLabel("درجة النجاح:"))
        self.min_score = QDoubleSpinBoxEN()
        self.min_score.setRange(0, 100)
        self.min_score.setValue(50)
        self.add_widget(self.min_score)
        
        self.add_widget(QLabel("الدرجة الكبرى:"))
        self.max_score = QDoubleSpinBoxEN()
        self.max_score.setRange(0, 200)
        self.max_score.setValue(100)
        self.add_widget(self.max_score)

        # الأزرار
        self.add_button("إلغاء", self.reject, "default")
        self.add_button("حفظ", self.save_subject, "primary")
    
    def load_subject_data(self):
        """تحميل بيانات المادة للتعديل (من dict)."""
        if not self.subject_data:
            return
        
        self.name_input.setText(self.subject_data['subject_name'])
        self.min_score.setValue(self.subject_data['min_pass_score'])
        self.max_score.setValue(self.subject_data['max_score'])
    
    def save_subject(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال اسم المادة")
            return
        min_s = self.min_score.value()
        max_s = self.max_score.value()
        if min_s > max_s:
            QMessageBox.warning(self, "تنبيه", "درجة النجاح > الدرجة الكبرى")
            return
        try:
            payload = {
                'subject_name': self.name_input.text().strip(),
                'min_pass_score': float(min_s),
                'max_score': float(max_s),
            }
            if AcademicFactory.is_remote():
                service = AcademicFactory.get_service()
                if self.subject_id:
                    service.update_subject(self.subject_id, payload)
                else:
                    service.create_subject(payload)
            else:
                self._save_local(payload)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل: {e}")

    def _save_local(self, payload):
        from app.database.session import session_scope
        from app.database.models import Subject
        from sqlalchemy import select
        from decimal import Decimal
        with session_scope() as session:
            if self.subject_id:
                s = session.get(Subject, self.subject_id)
            else:
                existing = session.execute(
                    select(Subject).where(
                        Subject.subject_name == payload['subject_name']
                    )
                ).scalar_one_or_none()
                if existing:
                    raise Exception("اسم المادة مكرر")
                s = Subject()
                session.add(s)
            s.subject_name = payload['subject_name']
            s.min_pass_score = Decimal(str(payload['min_pass_score']))
            s.max_score = Decimal(str(payload['max_score']))
             