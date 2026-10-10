"""
واجهة إدارة الصفوف والشعب - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Dict, List, Optional
import qtawesome as qta

from app.database.session import session_scope
from app.database.models import Grade, Section, Student
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.services.academic_factory import AcademicFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import GradientButton, QLineEditPlus, QSpinBoxEN
from datetime import date

from app.views.widgets.dialogs import ModernDialog
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class GradesSectionsPage(QWidget):
    """صفحة إدارة الصفوف والشعب - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.permission_service = permission_service
        self.academic_year = academic_year
        self.all_grades: List[Dict] = []  # ✅ dicts بدلاً من كائنات
        
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
        
        title = QLabel("إدارة الصفوف والشعب")
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
        
        self.count_label = QLabel("عدد الصفوف: 0")
        self.count_label.setObjectName("count_label")
        toolbar.addWidget(self.count_label)
        
        toolbar.addStretch()
        
        add_btn = GradientButton("إضافة صف", "fa5s.plus")
        add_btn.clicked.connect(self.add_grade)
        toolbar.addWidget(add_btn)
        
        card_layout.addLayout(toolbar)
        
        # جدول الصفوف
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "اسم الصف", "المرحلة", "الشعب", "السعة", "إجراء"
        ])
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 150)
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
        self.loading_overlay.show_loading("جاري تحميل الصفوف...")

        def _fetch():
            if AcademicFactory.is_remote():
                service = AcademicFactory.get_service()
                data = service.list_grades()
                return [
                    {
                        'id': g['id'],
                        'grade_name': g['grade_name'],
                        'stage_name': g['stage_name'],
                        'max_capacity': g['max_capacity'],
                        'sections': g['sections'],
                        'sections_count': len(g['sections']),
                    }
                    for g in data
                ]
            else:
                from app.database.session import session_scope
                from app.database.models import Grade
                from sqlalchemy import select
                from sqlalchemy.orm import joinedload
                with session_scope() as session:
                    grades = session.execute(
                        select(Grade).options(joinedload(Grade.sections))
                        .order_by(Grade.id)
                    ).unique().scalars().all()
                    return [
                        {
                            'id': g.id,
                            'grade_name': g.grade_name or '',
                            'stage_name': g.stage_name or '',
                            'max_capacity': g.max_capacity or 0,
                            'sections': [
                                {
                                    'id': s.id,
                                    'name': s.section_name,
                                    'capacity': s.capacity or 0,
                                }
                                for s in (g.sections or [])
                            ],
                            'sections_count': len(g.sections or []),
                        }
                        for g in grades
                    ]

        def _ok(data):
            try:
                self.all_grades = data
                self.display_grades()
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(self, "خطأ", f"فشل: {m}")

        run_async(_fetch, on_result=_ok, on_error=_err)
        
    # ============================================================
    # ✅ عرض البيانات
    # ============================================================
    
    def display_grades(self):
        """عرض الصفوف."""
        self.table.setRowCount(len(self.all_grades))
        
        for row, grade in enumerate(self.all_grades):
            self.table.setItem(row, 0, QTableWidgetItem(grade['grade_name']))
            self.table.setItem(row, 1, QTableWidgetItem(grade['stage_name']))
            
            # الشعب
            sections_names = "، ".join([s['name'] for s in grade['sections']])
            self.table.setItem(row, 2, QTableWidgetItem(sections_names))
            self.table.setItem(row, 3, QTableWidgetItem(str(grade['max_capacity'])))

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
            # ✅ استخدام ID بدلاً من الكائن
            edit_btn.clicked.connect(
                lambda checked, gid=grade['id']: self.edit_grade(gid)
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
                lambda checked, gid=grade['id']: self.delete_single_grade(gid)
            )
            action_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 4, action_widget)
            self.table.setRowHeight(row, 45)
        
        self.count_label.setText(f"عدد الصفوف: {len(self.all_grades)}")
    
    # ============================================================
    # ✅ العمليات (إضافة / تعديل / حذف)
    # ============================================================
    
    def add_grade(self):
        """إضافة صف جديد."""
        if self.permission_service and not self.permission_service.can_add("التهيئة الأكاديمية"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للإضافة في التهيئة الأكاديمية"
            )
            return
          
        dialog = GradeDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            QMessageBox.information(self, "نجاح", "تم إضافة الصف بنجاح")
    
    def edit_grade(self, grade_id: int):
        """تعديل صف (باستخدام ID)."""
        if self.permission_service and not self.permission_service.can_edit("التهيئة الأكاديمية"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للتعديل في التهيئة الأكاديمية"
            )
            return
        
        # ✅ إعادة تحميل الصف من قاعدة البيانات في جلسة جديدة
        try:
            with session_scope() as session:
                grade = session.execute(
                    select(Grade)
                    .options(joinedload(Grade.sections))
                    .where(Grade.id == grade_id)
                ).unique().scalar_one_or_none()
                
                if not grade:
                    QMessageBox.warning(self, "تنبيه", "الصف غير موجود")
                    return
                
                # ✅ تحويل إلى dict قبل تمريره للحوار
                grade_data = {
                    'id': grade.id,
                    'grade_name': grade.grade_name or '',
                    'stage_name': grade.stage_name or '',
                    'max_capacity': grade.max_capacity or 30,
                    'sections': [
                        {
                            'id': s.id,
                            'name': s.section_name,
                            'capacity': s.capacity or 30,
                        }
                        for s in (grade.sections or [])
                    ],
                }
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل تحميل بيانات الصف: {str(e)}")
            return
        
        dialog = GradeDialog(grade_data=grade_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            QMessageBox.information(self, "نجاح", "تم تحديث الصف بنجاح")
    
    def delete_single_grade(self, grade_id: int):
        if (self.permission_service
                and not self.permission_service.can_delete("التهيئة الأكاديمية")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return
        grade = next((g for g in self.all_grades if g['id'] == grade_id), None)
        if not grade:
            return
        reply = QMessageBox.warning(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف الصف: {grade['grade_name']}؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            if AcademicFactory.is_remote():
                AcademicFactory.get_service().delete_grade(grade_id)
            else:
                from app.database.session import session_scope
                from app.database.models import Grade, Section
                from sqlalchemy import select
                with session_scope() as session:
                    session.query(Section).filter(
                        Section.grade_id == grade_id
                    ).delete()
                    g = session.get(Grade, grade_id)
                    if g:
                        session.delete(g)
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
# ✅ نافذة إضافة/تعديل صف (مع dicts)
# ============================================================

class GradeDialog(ModernDialog):
    """نافذة إضافة/تعديل صف دراسي مع الشعب."""
    
    def __init__(self, grade_data: Optional[dict] = None, parent=None):
        super().__init__(
            "تعديل صف" if grade_data else "إضافة صف جديد",
            "fa5s.school",
            parent,
            width=500,
            height=700
        )
        # ✅ تخزين dict بدلاً من كائن ORM
        self.grade_data = grade_data
        self.grade_id = grade_data['id'] if grade_data else None
        
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد النموذج."""
        
        # اسم الصف
        self.add_widget(QLabel("اسم الصف:"))
        self.grade_name_input = QLineEditPlus("مثال: الأول الأساسي، السابع...")
        self.add_widget(self.grade_name_input)
        
        # المرحلة
        self.add_widget(QLabel("المرحلة:"))
        self.stage_combo = QComboBox()
        self.stage_combo.addItems([
            "رياض الأطفال", "الابتدائي", "الإعدادي", "الثانوي"
        ])
        self.add_widget(self.stage_combo)
        
        # السعة الاستيعابية
        self.add_widget(QLabel("السعة الاستيعابية للصف:"))
        self.capacity_spin = QSpinBoxEN(1, 500)
        self.capacity_spin.setValue(30)
        self.add_widget(self.capacity_spin)
        
        # عدد الشعب
        self.add_widget(QLabel("عدد الشعب:"))
        self.sections_count_spin = QSpinBoxEN(1, 10)
        self.sections_count_spin.setValue(3)
        self.sections_count_spin.valueChanged.connect(self.update_sections_table)
        self.add_widget(self.sections_count_spin)
        
        # جدول الشعب
        self.add_widget(QLabel("أسماء الشعب:"))
        
        sections_frame = QFrame()
        sections_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                background: #F8FAFC;
            }
        """)
        
        sections_layout = QVBoxLayout(sections_frame)
        sections_layout.setContentsMargins(10, 10, 10, 10)
        
        self.sections_table = QTableWidget()
        self.sections_table.setColumnCount(2)
        self.sections_table.setHorizontalHeaderLabels(["اسم الشعبة", "السعة"])
        self.sections_table.setColumnWidth(0, 200)
        self.sections_table.setColumnWidth(1, 150)
        self.sections_table.horizontalHeader().setStretchLastSection(True)
        self.sections_table.verticalHeader().setVisible(False)
        self.sections_table.setMaximumHeight(190)
        sections_layout.addWidget(self.sections_table)
        
        self.add_widget(sections_frame)
                
        # الأزرار
        self.add_button("إلغاء", self.reject, "default")
        self.add_button("حفظ", self.save_grade, "primary")

        if self.grade_data:
            self.load_grade_data()
        else:
            self.update_sections_table()
    
    def update_sections_table(self):
        """تحديث جدول الشعب حسب العدد."""
        count = self.sections_count_spin.value()
        default_names = ["أ", "ب", "ج", "د", "هـ", "و", "ز", "ح", "ط", "ي"]
        
        # حفظ القيم الحالية قبل إعادة البناء
        current_values = []
        for row in range(self.sections_table.rowCount()):
            name_widget = self.sections_table.cellWidget(row, 0)
            cap_widget = self.sections_table.cellWidget(row, 1)
            if name_widget and cap_widget:
                current_values.append((
                    name_widget.text(),
                    cap_widget.value()
                ))
        
        self.sections_table.setRowCount(count)
        
        for row in range(count):
            # اسم الشعبة
            name_input = QLineEditPlus("اسم الشعبة")
            if row < len(current_values):
                name_input.setText(current_values[row][0])
            else:
                name_input.setText(
                    default_names[row] if row < len(default_names) else ""
                )
            name_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sections_table.setCellWidget(row, 0, name_input)
            
            # سعة الشعبة
            capacity_spin = QSpinBoxEN(1, 500)
            if row < len(current_values):
                capacity_spin.setValue(current_values[row][1])
            else:
                capacity_spin.setValue(self.capacity_spin.value())
            self.sections_table.setCellWidget(row, 1, capacity_spin)
            
            self.sections_table.setRowHeight(row, 45)
    
    def load_grade_data(self):
        """تحميل بيانات الصف للتعديل (من dict)."""
        if not self.grade_data:
            return
        
        self.grade_name_input.setText(self.grade_data['grade_name'])
        self.stage_combo.setCurrentText(self.grade_data['stage_name'])
        self.capacity_spin.setValue(self.grade_data['max_capacity'])
        
        # ✅ تعيين العدد قبل التحديث لمنع إعادة البناء
        sections = self.grade_data.get('sections', [])
        if sections:
            self.sections_count_spin.blockSignals(True)
            self.sections_count_spin.setValue(len(sections))
            self.sections_count_spin.blockSignals(False)
            
            # بناء الجدول يدوياً
            self.sections_table.setRowCount(len(sections))
            
            for row, section in enumerate(sections):
                name_input = QLineEditPlus("اسم الشعبة")
                name_input.setText(section['name'])
                name_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.sections_table.setCellWidget(row, 0, name_input)
                
                capacity_spin = QSpinBoxEN(1, 500)
                capacity_spin.setValue(section['capacity'])
                self.sections_table.setCellWidget(row, 1, capacity_spin)
                
                self.sections_table.setRowHeight(row, 45)
        else:
            self.update_sections_table()
    
    def save_grade(self):
        if not self.grade_name_input.text().strip():
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال اسم الصف")
            return
        sections = []
        names_seen = set()
        for row in range(self.sections_table.rowCount()):
            nm = self.sections_table.cellWidget(row, 0)
            cp = self.sections_table.cellWidget(row, 1)
            if isinstance(nm, QLineEdit) and isinstance(cp, QSpinBox):
                name = nm.text().strip()
                if name and name not in names_seen:
                    sections.append({'name': name, 'capacity': cp.value()})
                    names_seen.add(name)
        if not sections:
            QMessageBox.warning(self, "تنبيه", "أدخل اسم شعبة واحدة على الأقل")
            return
        payload = {
            'grade_name': self.grade_name_input.text().strip(),
            'stage_name': self.stage_combo.currentText(),
            'max_capacity': self.capacity_spin.value(),
            'sections': sections,
        }
        try:
            if AcademicFactory.is_remote():
                service = AcademicFactory.get_service()
                if self.grade_id:
                    service.update_grade(self.grade_id, payload)
                else:
                    service.create_grade(payload)
            else:
                self._save_local(payload)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل: {e}")

    def _save_local(self, payload):
        from app.database.session import session_scope
        from app.database.models import Grade, Section
        from sqlalchemy import select
        with session_scope() as session:
            if self.grade_id:
                grade = session.get(Grade, self.grade_id)
                session.query(Section).filter(
                    Section.grade_id == self.grade_id
                ).delete()
            else:
                grade = Grade()
                session.add(grade)
            grade.grade_name = payload['grade_name']
            grade.stage_name = payload['stage_name']
            grade.max_capacity = payload['max_capacity']
            session.flush()
            for sec in payload['sections']:
                session.add(Section(
                    grade_id=grade.id,
                    section_name=sec['name'],
                    capacity=sec['capacity'],
                ))