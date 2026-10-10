"""
واجهة إدارة الطلاب - تعمل مع Local أو Remote.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Dict, Optional
from fastapi import logger
import qtawesome as qta
from datetime import date

from app.services.permission_service import PermissionService
from app.services.student_factory import StudentFactory
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from app.views.widgets.custom_widgets import (
    PageHeader, Card, SearchBox, ModernTable,
    AvatarLabel, Badge, GradientButton, IconButton
)
from app.views.tabs.students.student_dialog import StudentDialog
from app.views.widgets.dialogs import (
    ConfirmationDialog, SuccessDialog, ErrorDialog
)


class StudentListPage(QWidget):
    """صفحة إدارة الطلاب - Local أو Remote."""

    def __init__(self, user, academic_year,
                 permission_service: Optional[PermissionService] = None,
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service

        # ✅ حفظ ID السنة قبل فقدان الجلسة
        self.academic_year_id = (
            academic_year.id if academic_year else None
        )

        self.all_students: List[Dict] = []
        self.current_filtered_students: List[Dict] = []
        self.grades_data: List[Dict] = []
        self.sections_data: List[Dict] = []

        self.setup_ui()
        self.loading_overlay = LoadingOverlay(self)

        QTimer.singleShot(100, self.load_data)

    def setup_ui(self):
        """إعداد الواجهة (نفس السابق)."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)

        header_label = QLabel("إدارة الطلاب")
        header_label.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #0F172A;"
        )
        main_layout.addWidget(header_label)

        sub_label = QLabel("عرض وإدارة بيانات الطلاب المسجلين")
        sub_label.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(sub_label)

        # بطاقة الفلاتر
        filter_card = QFrame()
        filter_card.setObjectName("filterCard")
        filter_layout = QHBoxLayout(filter_card)

        self.search_box = SearchBox("بحث عن طالب...")
        self.search_box.setMinimumWidth(200)
        self.search_box.textChanged.connect(self.filter_students)
        filter_layout.addWidget(self.search_box)

        self.grade_filter = QComboBox()
        self.grade_filter.addItem("جميع الصفوف", None)
        self.grade_filter.setMinimumWidth(130)
        self.grade_filter.currentIndexChanged.connect(self.filter_students)
        filter_layout.addWidget(self.grade_filter)

        self.section_filter = QComboBox()
        self.section_filter.addItem("جميع الشعب", None)
        self.section_filter.setMinimumWidth(130)
        self.section_filter.currentIndexChanged.connect(self.filter_students)
        filter_layout.addWidget(self.section_filter)

        self.status_filter = QComboBox()
        self.status_filter.addItems(
            ["جميع الحالات", "مستمر", "انسحاب", "موقف", "خريج"]
        )
        self.status_filter.currentIndexChanged.connect(self.filter_students)
        filter_layout.addWidget(self.status_filter)

        filter_layout.addStretch()

        add_btn = GradientButton("إضافة طالب", "fa5s.plus")
        add_btn.clicked.connect(self.add_student)
        filter_layout.addWidget(add_btn)

        main_layout.addWidget(filter_card)

        # بطاقة الجدول
        table_card = QFrame()
        table_card.setObjectName("tableCard")
        table_layout = QVBoxLayout(table_card)

        toolbar = QHBoxLayout()
        self.count_label = QLabel("إجمالي الطلاب: 0")
        self.count_label.setObjectName("count_label")
        toolbar.addWidget(self.count_label)
        toolbar.addStretch()

        edit_btn = IconButton('fa5s.edit', "تعديل", color='#1976D3')
        edit_btn.clicked.connect(self.edit_student)
        toolbar.addWidget(edit_btn)

        delete_btn = IconButton('fa5s.trash', "حذف", color='#EF4444')
        delete_btn.clicked.connect(self.delete_student)
        toolbar.addWidget(delete_btn)

        table_layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "رقم الطالب", "الاسم الكامل", "الصف", "الشعبة",
            "الجنس", "الحالة", "ولي الأمر"
        ])
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 200)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.verticalHeader().setVisible(False)
        table_layout.addWidget(self.table)

        main_layout.addWidget(table_card)

    # ============================================================
    # ✅ التحميل - Local أو Remote
    # ============================================================

    def load_data(self):
        """تحميل البيانات."""
        self.loading_overlay.show_loading("جاري تحميل بيانات الطلاب...")

        academic_year_id = self.academic_year_id

        def _fetch_data():
            """جلب البيانات (في الخلفية)."""
            if StudentFactory.is_remote():
                # ✅ Remote mode
                service = StudentFactory.get_service()

                # 1. الصفوف
                grades_data = service.list_grades()

                # 2. الشعب
                sections_data = service.list_sections()

                # 3. الطلاب
                students_data = service.list_students(
                    academic_year_id=academic_year_id,
                )

                return {
                    'grades': grades_data,
                    'sections': sections_data,
                    'students': students_data,
                }
            else:
                # ✅ Local mode (الكود القديم)
                from app.database.session import session_scope
                from app.database.models import Student, Grade, Section
                from sqlalchemy import select
                from sqlalchemy.orm import joinedload

                with session_scope() as session:
                    grades = session.execute(
                        select(Grade).order_by(Grade.grade_name)
                    ).scalars().all()
                    grades_data = [
                        {'id': g.id, 'name': g.grade_name or ''}
                        for g in grades
                    ]

                    sections = session.execute(
                        select(Section)
                        .options(joinedload(Section.grade))
                        .order_by(Section.section_name)
                    ).unique().scalars().all()
                    sections_data = [
                        {
                            'id': s.id,
                            'name': s.section_name or '',
                            'grade_id': s.grade_id,
                            'grade_name': (
                                s.grade.grade_name if s.grade else ''
                            ),
                        }
                        for s in sections
                    ]

                    students = session.execute(
                        select(Student)
                        .options(
                            joinedload(Student.grade),
                            joinedload(Student.section),
                            joinedload(Student.parent),
                        )
                        .where(
                            Student.academic_year_id == academic_year_id
                        )
                        .order_by(Student.full_name)
                    ).unique().scalars().all()

                    students_data = [
                        {
                            'id': s.id,
                            'student_number': s.student_number or '',
                            'full_name': s.full_name or '',
                            'gender': s.gender or '',
                            'status': s.status or '',
                            'grade_id': s.grade_id,
                            'section_id': s.section_id,
                            'grade_name': (
                                s.grade.grade_name if s.grade else ''
                            ),
                            'section_name': (
                                s.section.section_name if s.section else ''
                            ),
                            'parent_name': (
                                s.parent.full_name if s.parent else ''
                            ),
                        }
                        for s in students
                    ]

                    return {
                        'grades': grades_data,
                        'sections': sections_data,
                        'students': students_data,
                    }

        def _on_result(data):
            """عند اكتمال التحميل."""
            try:
                self.grades_data = data['grades']
                self.sections_data = data['sections']
                self.all_students = data['students']

                # فلاتر الصفوف
                self.grade_filter.blockSignals(True)
                self.grade_filter.clear()
                self.grade_filter.addItem("جميع الصفوف", None)
                for g in self.grades_data:
                    self.grade_filter.addItem(g['name'], g['id'])
                self.grade_filter.blockSignals(False)

                # فلاتر الشعب
                self.section_filter.blockSignals(True)
                self.section_filter.clear()
                self.section_filter.addItem("جميع الشعب", None)
                for s in self.sections_data:
                    label = (
                        f"{s.get('grade_name', '')} - {s['name']}"
                        if s.get('grade_name') else s['name']
                    )
                    self.section_filter.addItem(label, s['id'])
                self.section_filter.blockSignals(False)

                self.current_filtered_students = self.all_students
                self.display_students(self.all_students)

            except Exception as e:
                logger.exception(f"خطأ في تحديث الواجهة: {e}")
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(
                self, "خطأ", f"فشل تحميل البيانات:\n{error}"
            )
            self.all_students = []
            self.current_filtered_students = []
            self.display_students([])

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)

    # ============================================================
    # ✅ العرض والتصفية
    # ============================================================

    def display_students(self, students: List[Dict]):
        """عرض الطلاب."""
        self.table.setRowCount(len(students))

        status_colors = {
            'مستمر': '#10B981',
            'انسحاب': '#EF4444',
            'موقف': '#F59E0B',
            'خريج': '#1976D3',
        }

        for row, student in enumerate(students):
            self.table.setItem(
                row, 0, QTableWidgetItem(student.get('student_number', ''))
            )
            self.table.setItem(
                row, 1, QTableWidgetItem(student.get('full_name', ''))
            )
            self.table.setItem(
                row, 2, QTableWidgetItem(student.get('grade_name', ''))
            )
            self.table.setItem(
                row, 3, QTableWidgetItem(student.get('section_name', ''))
            )
            self.table.setItem(
                row, 4, QTableWidgetItem(student.get('gender', ''))
            )

            status_item = QTableWidgetItem(student.get('status', ''))
            status_item.setForeground(
                QColor(status_colors.get(student.get('status'), '#64748B'))
            )
            self.table.setItem(row, 5, status_item)

            self.table.setItem(
                row, 6, QTableWidgetItem(student.get('parent_name', ''))
            )
            self.table.setRowHeight(row, 35)

        self.count_label.setText(f"إجمالي الطلاب: {len(students)}")

    def filter_students(self):
        """تصفية محلية (client-side)."""
        if not hasattr(self, 'all_students'):
            return

        search_text = (
            self.search_box.text().lower()
            if self.search_box.text() else ""
        )
        grade_id = self.grade_filter.currentData()
        section_id = self.section_filter.currentData()
        status = self.status_filter.currentText()

        filtered = []
        for student in self.all_students:
            if search_text:
                full_name = (student.get('full_name') or '').lower()
                student_number = (
                    student.get('student_number') or ''
                ).lower()
                if (search_text not in full_name
                        and search_text not in student_number):
                    continue

            if grade_id and student.get('grade_id') != grade_id:
                continue
            if section_id and student.get('section_id') != section_id:
                continue
            if (status != "جميع الحالات"
                    and student.get('status') != status):
                continue

            filtered.append(student)

        self.current_filtered_students = filtered
        self.display_students(filtered)

    # ============================================================
    # ✅ العمليات (إضافة / تعديل / حذف)
    # ============================================================

    def add_student(self):
        """إضافة طالب جديد."""
        if (self.permission_service
                and not self.permission_service.can_add("الطلاب")):
            QMessageBox.warning(
                self, "تنبيه", "ليس لديك الصلاحية لإضافة طالب"
            )
            return

        dialog = StudentDialog(
            self.academic_year, user=self.user, parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            QMessageBox.information(self, "نجاح", "تم إضافة الطالب بنجاح")

    def edit_student(self):
        """تعديل بيانات طالب."""
        if (self.permission_service
                and not self.permission_service.can_edit("الطلاب")):
            QMessageBox.warning(
                self, "تنبيه", "ليس لديك الصلاحية لتعديل بيانات طالب"
            )
            return

        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار طالب للتعديل")
            return
        if current_row >= len(self.current_filtered_students):
            return

        student_data = self.current_filtered_students[current_row]
        student_id = student_data['id']

        # ✅ تحميل الطالب (Local أو Remote)
        try:
            student_obj = self._load_student_for_dialog(student_id)
            if not student_obj:
                QMessageBox.warning(self, "تنبيه", "الطالب غير موجود")
                return

            dialog = StudentDialog(
                self.academic_year,
                self.user,
                student=student_obj,
                parent=self,
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_data()
                QMessageBox.information(
                    self, "نجاح", "تم تحديث بيانات الطالب بنجاح"
                )
        except Exception as e:
            QMessageBox.critical(
                self, "خطأ", f"فشل تعديل الطالب: {str(e)}"
            )

    def _load_student_for_dialog(self, student_id: int):
        """تحميل الطالب لتمريره للـ Dialog."""
        if StudentFactory.is_remote():
            from types import SimpleNamespace
            service = StudentFactory.get_service()
            data = service.get(student_id)
            return SimpleNamespace(**data)
        else:
            from app.database.session import session_scope
            from app.database.models import Student
            with session_scope() as session:
                student = session.get(Student, student_id)
                if student:
                    _ = student.grade
                    _ = student.section
                    _ = student.parent
                return student

    def delete_student(self):
        """حذف طالب."""
        if (self.permission_service
                and not self.permission_service.can_delete("الطلاب")):
            QMessageBox.warning(
                self, "تنبيه", "ليس لديك الصلاحية لحذف طالب"
            )
            return

        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار طالب للحذف")
            return
        if current_row >= len(self.current_filtered_students):
            return

        student_data = self.current_filtered_students[current_row]
        student_id = student_data['id']

        reply = QMessageBox.question(
            self,
            "تأكيد الحذف",
            f"هل أنت متأكد من حذف الطالب:\n"
            f"{student_data.get('full_name')} "
            f"({student_data.get('student_number')})؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        def _do_delete():
            if StudentFactory.is_remote():
                service = StudentFactory.get_service()
                service.delete(student_id)
            else:
                from app.database.session import session_scope
                from app.database.models import Student
                with session_scope() as session:
                    fresh = session.get(Student, student_id)
                    if fresh:
                        session.delete(fresh)

        try:
            _do_delete()
            QMessageBox.information(self, "نجاح", "تم حذف الطالب بنجاح")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(
                self, "خطأ", f"فشل حذف الطالب: {str(e)}"
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())