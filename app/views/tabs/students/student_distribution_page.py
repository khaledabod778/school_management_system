"""
واجهة توزيع الطلاب على الشعب - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta

from app.database.session import session_scope
from app.database.models import Student, Grade, Section
from sqlalchemy import select

from app.services.permission_service import PermissionService
from app.services.student_distribution_factory import StudentDistributionFactory
from app.views.widgets.custom_widgets import GradientButton
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class StudentDistributionPage(QWidget):
    """صفحة توزيع الطلاب على الشعب - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ تخزين ID السنة قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        
        # ✅ dicts بدلاً من ORM objects
        self.all_students: List[Dict] = []
        
        # ✅ تخزين مراجع checkbox لكل صف (لتسهيل القراءة)
        self.row_checkboxes: List[QCheckBox] = []
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل البيانات الأولية في الخلفية
        QTimer.singleShot(100, self.load_initial_data)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)
        
        title = QLabel("توزيع الطلاب على الشعب")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        # فلاتر
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
        
        filter_layout.addWidget(QLabel("الصف:"))
        self.grade_combo = QComboBox()
        self.grade_combo.setMinimumWidth(150)
        self.grade_combo.currentIndexChanged.connect(self._on_grade_changed)
        filter_layout.addWidget(self.grade_combo)

        filter_layout.addSpacing(20)
        
        filter_layout.addWidget(QLabel("الشعبة المستهدفة:"))
        self.section_combo = QComboBox()
        self.section_combo.setMinimumWidth(150)
        filter_layout.addWidget(self.section_combo)
        
        filter_layout.addStretch()
        
        # ✅ عدّاد الطلاب المحددين
        self.selected_count_label = QLabel("المحددون: 0")
        self.selected_count_label.setStyleSheet(
            "color: #475569; font-weight: 600; font-size: 12px;"
        )
        filter_layout.addWidget(self.selected_count_label)
        
        # زر توزيع
        self.distribute_btn = GradientButton("توزيع المحددين", "fa5s.sitemap")
        self.distribute_btn.clicked.connect(self.distribute_students)
        filter_layout.addWidget(self.distribute_btn)
        
        main_layout.addWidget(filter_card)
        
        # جدول الطلاب
        table_Card = QFrame()
        table_Card.setObjectName("tableCard")
        table_Card.setStyleSheet("""
            QFrame#tableCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        card_layout = QVBoxLayout(table_Card)
        
        # ✅ شريط أدوات: تحديد الكل / إلغاء الكل
        toolbar = QHBoxLayout()
        
        self.count_label = QLabel("عدد الطلاب: 0")
        self.count_label.setStyleSheet("font-weight: 600; color: #475569;")
        toolbar.addWidget(self.count_label)
        
        toolbar.addStretch()
        
        select_all_btn = QPushButton("تحديد الكل")
        select_all_btn.setObjectName("primaryButton")
        select_all_btn.setStyleSheet("""
            QPushButton#primaryButton {
                background: #1976D3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton#primaryButton:hover {
                background: #1565C0;
            }
        """)
        select_all_btn.clicked.connect(lambda: self._toggle_all_checkboxes(True))
        toolbar.addWidget(select_all_btn)
        
        clear_all_btn = QPushButton("إلغاء الكل")
        clear_all_btn.setObjectName("secondaryButton")
        clear_all_btn.setStyleSheet("""
            QPushButton#secondaryButton {
                background: #E2E8F0;
                color: #475569;
                border: none;
                border-radius: 5px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton#secondaryButton:hover {
                background: #CBD5E1;
            }
        """)
        clear_all_btn.clicked.connect(lambda: self._toggle_all_checkboxes(False))
        toolbar.addWidget(clear_all_btn)
        
        card_layout.addLayout(toolbar)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "", "رقم الطالب", "الاسم", "الشعبة الحالية"
        ])
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 250)
        self.table.setColumnWidth(3, 120)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        card_layout.addWidget(self.table)
        
        main_layout.addWidget(table_Card)
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_initial_data(self):
        """تحميل الصفوف."""
        self.loading_overlay.show_loading("جاري تحميل الصفوف...")

        def _fetch():
            if StudentDistributionFactory.is_remote():
                service = StudentDistributionFactory.get_service()
                # استخدم endpoint الجديد للصفوف
                # أو استخدم lookup من خلال student_api
                from app.services.student_factory import StudentFactory
                student_service = StudentFactory.get_service()
                return student_service.list_grades()
            else:
                from app.database.session import session_scope
                from app.database.models import Grade
                from sqlalchemy import select
                with session_scope() as session:
                    grades = session.execute(
                        select(Grade).order_by(Grade.id)
                    ).scalars().all()
                    return [
                        {'id': g.id, 'name': g.grade_name or ''}
                        for g in grades
                    ]

        def _ok(data):
            try:
                self.grade_combo.blockSignals(True)
                self.grade_combo.clear()
                for grade in data:
                    self.grade_combo.addItem(
                        grade.get('name', grade.get('grade_name', '')),
                        grade['id']
                    )
                self.grade_combo.blockSignals(False)
                if data:
                    self._on_grade_changed()
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(self, "خطأ", f"فشل: {m}")

        run_async(_fetch, on_result=_ok, on_error=_err)
        
    def _on_grade_changed(self):
        """عند تغيير الصف - تحميل الشعب والطلاب."""
        grade_id = self.grade_combo.currentData()
        if not grade_id:
            return
        
        # ✅ تحميل الشعب + الطلاب معاً في طلب واحد
        self._load_sections_and_students(grade_id)
    
    def _load_sections_and_students(self, grade_id: int):
        """تحميل الشعب والطلاب."""
        self.loading_overlay.show_loading("جاري تحميل الطلاب...")
        academic_year_id = self.academic_year_id

        def _fetch():
            if StudentDistributionFactory.is_remote():
                from app.services.student_factory import StudentFactory
                student_service = StudentFactory.get_service()

                # الشعب
                sections = student_service.list_sections(grade_id=grade_id)

                # الطلاب
                students = student_service.list_students(
                    academic_year_id=academic_year_id,
                    grade_id=grade_id,
                    status='مستمر',
                )

                # احسب section_name لكل طالب
                sections_map = {s['id']: s['name'] for s in sections}
                for s in students:
                    s['section_name'] = sections_map.get(
                        s.get('section_id'), ''
                    )

                return {
                    'sections': sections,
                    'students': students,
                }
            else:
                # نفس الكود القديم
                from app.database.session import session_scope
                from app.database.models import Student, Section
                from sqlalchemy import select
                with session_scope() as session:
                    sections = session.execute(
                        select(Section)
                        .where(Section.grade_id == grade_id)
                        .order_by(Section.section_name)
                    ).scalars().all()
                    sections_data = [
                        {'id': s.id, 'name': s.section_name or ''}
                        for s in sections
                    ]

                    students = session.execute(
                        select(Student)
                        .where(
                            Student.grade_id == grade_id,
                            Student.academic_year_id == academic_year_id,
                            Student.status == 'مستمر',
                        )
                        .order_by(Student.full_name)
                    ).scalars().all()

                    sections_map = {s['id']: s['name'] for s in sections_data}
                    students_data = [
                        {
                            'id': s.id,
                            'student_number': s.student_number or '',
                            'full_name': s.full_name or '',
                            'section_id': s.section_id,
                            'section_name': sections_map.get(
                                s.section_id, ''
                            ),
                        }
                        for s in students
                    ]

                    return {
                        'sections': sections_data,
                        'students': students_data,
                    }

        def _ok(data):
            try:
                self.section_combo.blockSignals(True)
                self.section_combo.clear()
                for s in data['sections']:
                    self.section_combo.addItem(
                        s.get('name', ''), s['id']
                    )
                self.section_combo.blockSignals(False)

                self.all_students = data['students']
                self.display_students(self.all_students)
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(self, "خطأ", f"فشل: {m}")

        run_async(_fetch, on_result=_ok, on_error=_err)

    # ============================================================
    # ✅ عرض البيانات
    # ============================================================
    
    def display_students(self, students: List[Dict]):
        """عرض الطلاب."""
        # ✅ إعادة تعيين القائمة
        self.row_checkboxes = []
        
        self.table.setRowCount(len(students))
        
        for row, student in enumerate(students):
            # مربع اختيار
            checkbox_widget = QWidget()
            checkbox_widget.setStyleSheet("background: transparent;")
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(self._update_selected_count)
            checkbox_layout.addWidget(checkbox)
            
            # ✅ حفظ المرجع
            self.row_checkboxes.append(checkbox)
            
            self.table.setCellWidget(row, 0, checkbox_widget)
            self.table.setItem(
                row, 1, QTableWidgetItem(student['student_number'])
            )
            self.table.setItem(
                row, 2, QTableWidgetItem(student['full_name'])
            )
            self.table.setItem(
                row, 3, QTableWidgetItem(student['section_name'])
            )

            self.table.setRowHeight(row, 35)
        
        # تحديث العدّاد
        self.count_label.setText(f"عدد الطلاب: {len(students)}")
        self._update_selected_count()
    
    def _toggle_all_checkboxes(self, checked: bool):
        """تحديد/إلغاء الكل."""
        for checkbox in self.row_checkboxes:
            checkbox.blockSignals(True)
            checkbox.setChecked(checked)
            checkbox.blockSignals(False)
        self._update_selected_count()
    
    def _update_selected_count(self):
        """تحديث عدّاد الطلاب المحددين."""
        count = sum(
            1 for cb in self.row_checkboxes if cb.isChecked()
        )
        self.selected_count_label.setText(f"المحددون: {count}")
    
    # ============================================================
    # ✅ العمليات
    # ============================================================
    
    def distribute_students(self):
        """توزيع الطلاب المحددين."""
        if (self.permission_service
                and not self.permission_service.can_edit("توزيع الطلاب")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        section_id = self.section_combo.currentData()
        if not section_id:
            QMessageBox.warning(self, "تنبيه", "اختر الشعبة المستهدفة")
            return

        selected_ids = []
        for row, cb in enumerate(self.row_checkboxes):
            if cb.isChecked() and row < len(self.all_students):
                selected_ids.append(self.all_students[row]['id'])

        if not selected_ids:
            QMessageBox.warning(self, "تنبيه", "اختر طلاباً للتوزيع")
            return

        section_name = self.section_combo.currentText()
        reply = QMessageBox.question(
            self, "تأكيد التوزيع",
            f"توزيع {len(selected_ids)} طالب على: {section_name}؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        def _do():
            if StudentDistributionFactory.is_remote():
                service = StudentDistributionFactory.get_service()
                service.distribute(selected_ids, section_id)
            else:
                from app.database.session import session_scope
                from app.database.models import Student
                with session_scope() as session:
                    for sid in selected_ids:
                        st = session.get(Student, sid)
                        if st:
                            st.section_id = section_id
                    session.commit()

        try:
            _do()
            QMessageBox.information(
                self, "نجاح",
                f"تم توزيع {len(selected_ids)} طالب بنجاح"
            )
            grade_id = self.grade_combo.currentData()
            if grade_id:
                self._load_sections_and_students(grade_id)
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
        self.load_initial_data()