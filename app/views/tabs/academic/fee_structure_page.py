"""
واجهة لائحة الرسوم المدرسية - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Tuple, Dict
import qtawesome as qta
from decimal import Decimal

from app.database.session import session_scope
from app.database.models import Grade, FeeType, GradeFeeStructure
from sqlalchemy import select

from app.services.academic_factory import AcademicFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import GradientButton, QDoubleSpinBoxEN
from app.views.widgets.dialogs import ModernDialog
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class FeeStructurePage(QWidget):
    """صفحة لائحة الرسوم المدرسية - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ تخزين ID السنة قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        
        # ✅ dicts بدلاً من tuples من ORM
        self.all_fees: List[Dict] = []
        
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
        
        title = QLabel("لائحة الرسوم المدرسية")
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

        # فلاتر
        filter_layout = QHBoxLayout()

        self.count_label = QLabel("الصف:")
        filter_layout.addWidget(self.count_label)

        self.grade_filter = QComboBox()
        self.grade_filter.addItem("جميع الصفوف", None)
        self.grade_filter.setMinimumWidth(150)
        self.grade_filter.currentIndexChanged.connect(self.filter_fees)
        filter_layout.addWidget(self.grade_filter)
        
        filter_layout.addStretch()
        
        add_btn = GradientButton("إضافة رسوم", "fa5s.plus")
        add_btn.clicked.connect(self.add_fee)
        filter_layout.addWidget(add_btn)
        
        card_layout.addLayout(filter_layout)
        
        # جدول الرسوم
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "الصف", "نوع الرسوم", "المبلغ", "إجراء"
        ])
        self.table.setColumnWidth(0, 220)
        self.table.setColumnWidth(1, 220)
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
        self.loading_overlay.show_loading("جاري تحميل لائحة الرسوم...")

        def _fetch():
            if AcademicFactory.is_remote():
                service = AcademicFactory.get_service()
                return {
                    'grades': service.list_grades(),
                    'fees': service.list_fee_structures(self.academic_year_id),
                }
            else:
                from app.database.session import session_scope
                from app.database.models import Grade, GradeFeeStructure, FeeType
                from sqlalchemy import select
                from sqlalchemy.orm import joinedload
                with session_scope() as session:
                    grades = session.execute(
                        select(Grade).order_by(Grade.grade_name)
                    ).scalars().all()
                    grades_data = [
                        {'id': g.id, 'grade_name': g.grade_name or '', 'name': g.grade_name or ''}
                        for g in grades
                    ]
                    fees_q = session.execute(
                        select(GradeFeeStructure)
                        .options(
                            joinedload(GradeFeeStructure.grade),
                            joinedload(GradeFeeStructure.fee_type),
                        )
                        .where(GradeFeeStructure.academic_year_id == self.academic_year_id)
                    ).all()
                    fees = [
                        {
                            'id': f.id,
                            'grade_id': f.grade_id,
                            'grade_name': f.grade.grade_name if f.grade else '',
                            'fee_type_id': f.fee_type_id,
                            'fee_type_name': f.fee_type.fee_name if f.fee_type else '',
                            'amount': float(f.amount or 0),
                        }
                        for f in fees_q
                    ]
                    return {'grades': grades_data, 'fees': fees}

        def _ok(data):
            try:
                self.grade_filter.blockSignals(True)
                self.grade_filter.clear()
                self.grade_filter.addItem("جميع الصفوف", None)
                for g in data['grades']:
                    self.grade_filter.addItem(
                        g.get('grade_name', g.get('name', '')),
                        g['id']
                    )
                self.grade_filter.blockSignals(False)
                self.all_fees = data['fees']
                self.display_fees(self.all_fees)
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(self, "خطأ", f"فشل: {m}")

        run_async(_fetch, on_result=_ok, on_error=_err)
        
    # ============================================================
    # ✅ عرض البيانات
    # ============================================================
    
    def display_fees(self, fees: List[Dict]):
        """عرض الرسوم."""
        self.table.setRowCount(len(fees))
        
        for row, fee in enumerate(fees):
            self.table.setItem(row, 0, QTableWidgetItem(fee['grade_name']))
            self.table.setItem(row, 1, QTableWidgetItem(fee['fee_type_name']))
            self.table.setItem(
                row, 2,
                QTableWidgetItem(f"{fee['amount']:,.2f}")
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
                lambda checked, fid=fee['id']: self.edit_fee(fid)
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
                lambda checked, fid=fee['id']: self.delete_fee(fid)
            )
            action_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 3, action_widget)
            self.table.setRowHeight(row, 45)
    
    def filter_fees(self):
        """تصفية الرسوم."""
        grade_id = self.grade_filter.currentData()
        
        if not grade_id:
            self.display_fees(self.all_fees)
            return
        
        filtered = [
            fee for fee in self.all_fees
            if fee['grade_id'] == grade_id
        ]
        
        self.display_fees(filtered)
    
    # ============================================================
    # ✅ العمليات (إضافة / تعديل / حذف)
    # ============================================================
    
    def add_fee(self):
        """إضافة رسوم جديدة."""
        if self.permission_service and not self.permission_service.can_add("التهيئة الأكاديمية"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للإضافة في التهيئة الأكاديمية"
            )
            return
                
        dialog = FeeDialog(self.academic_year, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            QMessageBox.information(self, "نجاح", "تم إضافة الرسوم بنجاح")
    
    def edit_fee(self, fee_id: int):
        """تعديل رسوم (باستخدام ID)."""
        if self.permission_service and not self.permission_service.can_edit("التهيئة الأكاديمية"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للتعديل في التهيئة الأكاديمية"
            )
            return
        
        # ✅ إعادة تحميل من قاعدة البيانات
        try:
            with session_scope() as session:
                fee_structure = session.get(GradeFeeStructure, fee_id)
                if not fee_structure:
                    QMessageBox.warning(self, "تنبيه", "الرسوم غير موجودة")
                    return
                
                # ✅ تحويل إلى dict
                fee_data = {
                    'id': fee_structure.id,
                    'grade_id': fee_structure.grade_id,
                    'fee_type_id': fee_structure.fee_type_id,
                    'amount': float(fee_structure.amount or 0),
                }
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل تحميل البيانات: {str(e)}")
            return
        
        dialog = FeeDialog(
            self.academic_year,
            fee_data=fee_data,
            parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            QMessageBox.information(self, "نجاح", "تم تحديث الرسوم بنجاح")
    
    def delete_fee(self, fee_id: int):
        if (self.permission_service
                and not self.permission_service.can_delete("التهيئة الأكاديمية")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return
        fee = next((f for f in self.all_fees if f['id'] == fee_id), None)
        if not fee:
            return
        reply = QMessageBox.warning(
            self, "تأكيد الحذف",
            f"حذف: {fee['grade_name']} - {fee['fee_type_name']} ({fee['amount']})؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            if AcademicFactory.is_remote():
                AcademicFactory.get_service().delete_fee_structure(fee_id)
            else:
                from app.database.session import session_scope
                from app.database.models import GradeFeeStructure
                with session_scope() as session:
                    f = session.get(GradeFeeStructure, fee_id)
                    if f:
                        session.delete(f)
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
# ✅ نافذة إضافة/تعديل رسوم (مع dicts)
# ============================================================

class FeeDialog(ModernDialog):
    """نافذة إضافة/تعديل رسوم."""
    
    def __init__(self, academic_year, fee_data: Optional[dict] = None, parent=None):
        super().__init__(
            "تعديل رسوم" if fee_data else "إضافة رسوم جديدة",
            "fa5s.money-bill-wave",
            parent,
            width=500,
            height=400
        )
        self.academic_year = academic_year
        # ✅ تخزين dict بدلاً من ORM object
        self.fee_data = fee_data
        self.fee_id = fee_data['id'] if fee_data else None
        
        self.setup_ui()
        self.load_data()
        
        if fee_data:
            self.load_fee_data()
    
    def setup_ui(self):
        """إعداد النموذج."""
        
        # الصف
        self.add_widget(QLabel("الصف الدراسي:"))
        self.grade_combo = QComboBox()
        self.add_widget(self.grade_combo)
        
        # نوع الرسوم
        self.add_widget(QLabel("نوع الرسوم:"))
        self.fee_type_combo = QComboBox()
        self.add_widget(self.fee_type_combo)
        
        # المبلغ
        self.add_widget(QLabel("المبلغ:"))
        self.amount_spin = QDoubleSpinBoxEN()
        self.amount_spin.setStyleSheet("""
            QDoubleSpinBox {
                border: 2px solid #10B981;
                border-radius: 8px;
                padding: 10px;
                font-weight: 700;
                font-size: 16px;
                color: #059669;
                background: #ECFDF5;
            }
        """)
        self.add_widget(self.amount_spin)
        
        # الأزرار
        self.add_button("إلغاء", self.reject, "default")
        self.add_button("حفظ", self.save_fee, "primary")
    
    def load_data(self):
        try:
            if AcademicFactory.is_remote():
                service = AcademicFactory.get_service()
                grades = service.list_grades()
                fee_types = service.list_fee_types()
            else:
                from app.database.session import session_scope
                from app.database.models import Grade, FeeType
                from sqlalchemy import select
                with session_scope() as session:
                    grades = [
                        {'id': g.id, 'grade_name': g.grade_name or '', 'name': g.grade_name or ''}
                        for g in session.execute(
                            select(Grade).order_by(Grade.grade_name)
                        ).scalars().all()
                    ]
                    fee_types = [
                        {'id': t.id, 'fee_name': t.fee_name or ''}
                        for t in session.execute(
                            select(FeeType).order_by(FeeType.fee_name)
                        ).scalars().all()
                    ]
            for g in grades:
                self.grade_combo.addItem(g.get('grade_name', g.get('name', '')), g['id'])
            for t in fee_types:
                self.fee_type_combo.addItem(t['fee_name'], t['id'])
        except Exception as e:
            print(f"خطأ: {e}")

    def load_fee_data(self):
        """تحميل بيانات الرسوم للتعديل (من dict)."""
        if not self.fee_data:
            return
        
        # تحديد الصف
        grade_index = self.grade_combo.findData(self.fee_data['grade_id'])
        if grade_index >= 0:
            self.grade_combo.setCurrentIndex(grade_index)
        
        # تحديد نوع الرسوم
        fee_type_index = self.fee_type_combo.findData(self.fee_data['fee_type_id'])
        if fee_type_index >= 0:
            self.fee_type_combo.setCurrentIndex(fee_type_index)
        
        # المبلغ
        self.amount_spin.setValue(self.fee_data['amount'])
    
    def save_fee(self):
        grade_id = self.grade_combo.currentData()
        fee_type_id = self.fee_type_combo.currentData()
        amount = self.amount_spin.value()
        if not grade_id or not fee_type_id or amount <= 0:
            QMessageBox.warning(self, "تنبيه", "تحقق من البيانات")
            return
        payload = {
            'grade_id': grade_id,
            'fee_type_id': fee_type_id,
            'amount': float(amount),
        }
        try:
            if AcademicFactory.is_remote():
                service = AcademicFactory.get_service()
                if self.fee_id:
                    service.update_fee_structure(
                        self.fee_id, payload, self.academic_year.id
                    )
                else:
                    service.create_fee_structure(
                        payload, self.academic_year.id
                    )
            else:
                self._save_local(payload)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل: {e}")

    def _save_local(self, payload):
        from app.database.session import session_scope
        from app.database.models import GradeFeeStructure
        from sqlalchemy import select
        from decimal import Decimal
        with session_scope() as session:
            if self.fee_id:
                fee = session.get(GradeFeeStructure, self.fee_id)
            else:
                fee = GradeFeeStructure(
                    academic_year_id=self.academic_year.id,
                )
                session.add(fee)
            fee.grade_id = payload['grade_id']
            fee.fee_type_id = payload['fee_type_id']
            fee.amount = Decimal(str(payload['amount']))
            