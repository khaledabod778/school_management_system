"""
واجهة توزيع المواد على المعلمين - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta

from app.database.session import session_scope
from app.database.models import (
    Grade, Section, Subject, Employee, TeacherSubjectSection
)
from sqlalchemy import select

from app.services.academic_factory import AcademicFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import GradientButton
from app.views.widgets.dialogs import ModernDialog
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class TeacherAssignmentPage(QWidget):
    """صفحة توزيع المواد على المعلمين - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ تخزين ID السنة قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        
        # ✅ dicts بدلاً من tuples
        self.all_assignments: List[Dict] = []
        
        # ✅ تخزين الصفوف والمواد
        self.all_grades: List[Dict] = []
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
        
        title = QLabel("توزيع المواد على المعلمين")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        # بطاقة الجدول
        card = QFrame()
        card.setObjectName("cardFrame")
        card.setStyleSheet("""
            QFrame#cardFrame {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        card_layout = QVBoxLayout(card)

        # فلاتر
        filter_layout = QHBoxLayout()

        self.count_label = QLabel("الصف:")
        filter_layout.addWidget(self.count_label)
        self.grade_filter = QComboBox()
        self.grade_filter.addItem("جميع الصفوف", None)
        self.grade_filter.setMinimumWidth(150)
        self.grade_filter.currentIndexChanged.connect(self.filter_assignments)
        filter_layout.addWidget(self.grade_filter)

        filter_layout.addWidget(QLabel("        "))
        self.count_labell = QLabel("المادة:")
        filter_layout.addWidget(self.count_labell)
        self.subject_filter = QComboBox()
        self.subject_filter.addItem("جميع المواد", None)
        self.subject_filter.setMinimumWidth(150)
        self.subject_filter.currentIndexChanged.connect(self.filter_assignments)
        filter_layout.addWidget(self.subject_filter)
        
        filter_layout.addStretch()
        
        add_btn = GradientButton("توزيع مادة", "fa5s.plus")
        add_btn.clicked.connect(self.add_assignment)
        filter_layout.addWidget(add_btn)
        
        card_layout.addLayout(filter_layout)
        
        # جدول توزيع المواد
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "الصف", "الشعبة", "المادة", "المعلم", "إجراء"
        ])
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 250)
        self.table.setColumnWidth(4, 100)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        card_layout.addWidget(self.table)
        
        main_layout.addWidget(card)
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_data(self):
        self.loading_overlay.show_loading("جاري تحميل التوزيعات...")

        def _fetch():
            if AcademicFactory.is_remote():
                service = AcademicFactory.get_service()
                grades = service.list_grades()
                subjects = service.list_subjects()
                assignments = service.list_assignments(self.academic_year_id)
                return {
                    'grades': grades,
                    'subjects': subjects,
                    'assignments': assignments,
                }
            else:
                # نفس الكود القديم (local)
                from app.database.session import session_scope
                from app.database.models import (
                    Grade, Section, Subject, Employee, TeacherSubjectSection
                )
                from sqlalchemy import select
                with session_scope() as session:
                    grades = session.execute(
                        select(Grade).order_by(Grade.id)
                    ).scalars().all()
                    subjects = session.execute(
                        select(Subject).order_by(Subject.subject_name)
                    ).scalars().all()
                    assignments_q = session.execute(
                        select(TeacherSubjectSection)
                        .where(TeacherSubjectSection.academic_year_id == self.academic_year_id)
                    ).scalars().all()
                    return {
                        'grades': [
                            {'id': g.id, 'name': g.grade_name or ''} for g in grades
                        ],
                        'subjects': [
                            {'id': s.id, 'name': s.subject_name or ''} for s in subjects
                        ],
                        'assignments': [],  # مبسط
                    }

        def _ok(data):
            try:
                self.all_grades = data['grades']
                self.all_subjects = data['subjects']
                self.all_assignments = data['assignments']
                # فلاتر
                self.grade_filter.blockSignals(True)
                self.grade_filter.clear()
                self.grade_filter.addItem("جميع الصفوف", None)
                for g in self.all_grades:
                    self.grade_filter.addItem(g.get('name', ''), g['id'])
                self.grade_filter.blockSignals(False)

                self.subject_filter.blockSignals(True)
                self.subject_filter.clear()
                self.subject_filter.addItem("جميع المواد", None)
                for s in self.all_subjects:
                    self.subject_filter.addItem(s.get('name', ''), s['id'])
                self.subject_filter.blockSignals(False)

                self.display_assignments(self.all_assignments)
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(self, "خطأ", f"فشل: {m}")

        run_async(_fetch, on_result=_ok, on_error=_err)
        
    # ============================================================
    # ✅ عرض البيانات
    # ============================================================
    
    def display_assignments(self, assignments: List[Dict]):
        """عرض التوزيعات."""
        self.table.setRowCount(len(assignments))
        
        for row, assignment in enumerate(assignments):
            self.table.setItem(
                row, 0, QTableWidgetItem(assignment['grade_name'])
            )
            self.table.setItem(
                row, 1, QTableWidgetItem(assignment['section_name'])
            )
            self.table.setItem(
                row, 2, QTableWidgetItem(assignment['subject_name'])
            )
            self.table.setItem(
                row, 3, QTableWidgetItem(assignment['teacher_name'])
            )
            
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
            # ✅ تمرير ID فقط
            delete_btn.clicked.connect(
                lambda checked, aid=assignment['id']: self.delete_assignment(aid)
            )
            self.table.setCellWidget(row, 4, delete_btn)
            self.table.setRowHeight(row, 45)
    
    def filter_assignments(self):
        """تصفية التوزيعات."""
        grade_id = self.grade_filter.currentData()
        subject_id = self.subject_filter.currentData()
        
        filtered = []
        for assignment in self.all_assignments:
            # ✅ استخدام dict keys بدلاً من indices
            if grade_id and assignment['grade_id'] != grade_id:
                continue
            if subject_id and assignment['subject_id'] != subject_id:
                continue
            filtered.append(assignment)
        
        self.display_assignments(filtered)
    
    # ============================================================
    # ✅ العمليات (إضافة / حذف)
    # ============================================================
    
    def add_assignment(self):
        """إضافة توزيع."""
        if self.permission_service and not self.permission_service.can_add("التهيئة الأكاديمية"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للإضافة في التهيئة الأكاديمية"
            )
            return
        
        dialog = AssignmentDialog(self.academic_year_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            QMessageBox.information(self, "نجاح", "تم إضافة التوزيع بنجاح")
    
    def delete_assignment(self, assignment_id: int):
        if (self.permission_service
                and not self.permission_service.can_delete("التهيئة الأكاديمية")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return
        reply = QMessageBox.question(
            self, "حذف", "حذف هذا التوزيع؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            if AcademicFactory.is_remote():
                AcademicFactory.get_service().delete_assignment(assignment_id)
            else:
                from app.database.session import session_scope
                from app.database.models import TeacherSubjectSection
                with session_scope() as session:
                    a = session.get(TeacherSubjectSection, assignment_id)
                    if a:
                        session.delete(a)
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
# ✅ نافذة توزيع مادة (مع dicts)
# ============================================================

class AssignmentDialog(ModernDialog):
    """نافذة توزيع مادة."""
    
    def __init__(self, academic_year_id: int, parent=None):
        super().__init__(
            "توزيع مادة على معلم",
            "fa5s.chalkboard-teacher",  # ✅ أيقونة مناسبة
            parent,
            width=500,
            height=450
        )
        # ✅ تخزين ID فقط (وليس الكائن الكامل)
        self.academic_year_id = academic_year_id
        self._is_loaded = False

        self.setup_ui()
    
    def setup_ui(self):
        """إعداد النموذج."""        
        # الصف
        self.add_widget(QLabel("الصف:"))
        self.grade_combo = QComboBox()
        self.grade_combo.currentIndexChanged.connect(self.load_sections)
        self.add_widget(self.grade_combo)
        
        # الشعبة
        self.add_widget(QLabel("الشعبة:"))
        self.section_combo = QComboBox()
        self.add_widget(self.section_combo)
        
        # المادة
        self.add_widget(QLabel("المادة:"))
        self.subject_combo = QComboBox()
        self.add_widget(self.subject_combo)
        
        # المعلم
        self.add_widget(QLabel("المعلم:"))
        self.teacher_combo = QComboBox()
        self.add_widget(self.teacher_combo)
        
        # الأزرار
        self.add_button("إلغاء", self.reject, "default")
        self.add_button("حفظ", self.save_assignment, "primary")
        
        # ✅ تحميل البيانات (متزامن لأن النافذة صغيرة)
        self.load_data()
    
    def load_data(self):
        try:
            if AcademicFactory.is_remote():
                service = AcademicFactory.get_service()
                grades = service.list_grades()
                subjects = service.list_subjects()
                teachers = service.list_teachers()
            else:
                from app.database.session import session_scope
                from app.database.models import Grade, Subject, Employee
                from sqlalchemy import select, or_
                with session_scope() as session:
                    grades = [
                        {'id': g.id, 'name': g.grade_name or ''}
                        for g in session.execute(select(Grade).order_by(Grade.id)).scalars().all()
                    ]
                    subjects = [
                        {'id': s.id, 'name': s.subject_name or ''}
                        for s in session.execute(select(Subject).order_by(Subject.subject_name)).scalars().all()
                    ]
                    teachers = [
                        {'id': t.id, 'full_name': t.full_name or ''}
                        for t in session.execute(
                            select(Employee).where(
                                or_(
                                    Employee.job_title.ilike('%معلم%'),
                                    Employee.job_title.ilike('%مدرب%'),
                                    Employee.job_title.ilike('%مدرس%'),
                                )
                            ).order_by(Employee.full_name)
                        ).scalars().all()
                    ]

            self.grade_combo.blockSignals(True)
            self.grade_combo.clear()
            for g in grades:
                self.grade_combo.addItem(g.get('name', g.get('grade_name', '')), g['id'])
            self.grade_combo.blockSignals(False)

            for s in subjects:
                self.subject_combo.addItem(s.get('name', s.get('subject_name', '')), s['id'])

            for t in teachers:
                self.teacher_combo.addItem(t.get('full_name', ''), t['id'])

            self._is_loaded = True
            self.load_sections()
        except Exception as e:
            print(f"خطأ في التحميل: {e}")

    def load_sections(self):
        """تحميل الشعب بناءً على الصف المختار."""
        grade_id = self.grade_combo.currentData()
        
        try:
            with session_scope() as session:
                if grade_id:
                    sections = session.execute(
                        select(Section)
                        .where(Section.grade_id == grade_id)
                        .order_by(Section.section_name)
                    ).scalars().all()
                else:
                    sections = []
                
                self.section_combo.clear()
                for section in sections:
                    self.section_combo.addItem(section.section_name, section.id)
        except Exception as e:
            print(f"خطأ في تحميل الشعب: {str(e)}")
    
    def save_assignment(self):
        grade_id = self.grade_combo.currentData()
        section_id = self.section_combo.currentData()
        subject_id = self.subject_combo.currentData()
        teacher_id = self.teacher_combo.currentData()
        if not all([grade_id, section_id, subject_id, teacher_id]):
            QMessageBox.warning(self, "تنبيه", "اختر كل الحقول")
            return
        payload = {
            'academic_year_id': self.academic_year_id,
            'grade_id': grade_id,
            'section_id': section_id,
            'subject_id': subject_id,
            'teacher_id': teacher_id,
        }
        try:
            if AcademicFactory.is_remote():
                AcademicFactory.get_service().create_assignment(payload)
            else:
                from app.database.session import session_scope
                from app.database.models import TeacherSubjectSection
                with session_scope() as session:
                    session.add(TeacherSubjectSection(**payload))
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل: {e}")
            