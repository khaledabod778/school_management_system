"""
واجهة إدارة الواجبات المنزلية - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta
from datetime import date

from app.database.session import session_scope
from app.database.models import (
    Student, Grade, Section, Subject, Homework, AcademicYear
)
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.services.operations_factory import OperationsFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    GradientButton, IconButton, QDateEditEN, QLineEditPlus
)
from app.views.widgets.dialogs import ModernDialog
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class HomeworkPage(QWidget):
    """صفحة إدارة الواجبات المنزلية - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ تخزين ID السنة قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        
        # ✅ dicts بدلاً من ORM
        self.all_homeworks: List[Dict] = []
        self.current_filtered_homeworks: List[Dict] = []
        
        # ✅ debounce
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        
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
        header_label = QLabel("إدارة الواجبات المنزلية")
        header_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(header_label)
        
        sub_label = QLabel("إضافة ومتابعة الواجبات المنزلية للطلاب")
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
        
        filter_layout.addWidget(QLabel("الصف:"))
        self.grade_filter = QComboBox()
        self.grade_filter.addItem("جميع الصفوف", None)
        self.grade_filter.setMinimumWidth(120)
        self.grade_filter.currentIndexChanged.connect(self.filter_homeworks)
        filter_layout.addWidget(self.grade_filter)
        
        filter_layout.addWidget(QLabel("الشعبة:"))
        self.section_filter = QComboBox()
        self.section_filter.addItem("جميع الشعب", None)
        self.section_filter.setMinimumWidth(120)
        self.section_filter.currentIndexChanged.connect(self.filter_homeworks)
        filter_layout.addWidget(self.section_filter)
        
        filter_layout.addWidget(QLabel("المادة:"))
        self.subject_filter = QComboBox()
        self.subject_filter.addItem("جميع المواد", None)
        self.subject_filter.setMinimumWidth(120)
        self.subject_filter.currentIndexChanged.connect(self.filter_homeworks)
        filter_layout.addWidget(self.subject_filter)
        
        filter_layout.addStretch()

        add_btn = GradientButton("إضافة واجب", "fa5s.plus")
        add_btn.clicked.connect(self.add_homework)
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
        
        self.count_label = QLabel("إجمالي الواجبات: 0")
        self.count_label.setObjectName("count_label")
        toolbar.addWidget(self.count_label)
        
        toolbar.addStretch()

        edit_btn = IconButton('fa5s.edit', "تعديل", color='#1976D3')
        edit_btn.clicked.connect(self.edit_homework)
        toolbar.addWidget(edit_btn)
        
        delete_btn = IconButton('fa5s.trash', "حذف", color='#EF4444')
        delete_btn.clicked.connect(self.delete_homework)
        toolbar.addWidget(delete_btn)
        
        print_btn = IconButton('fa5s.print', "طباعة", color='#10B981')
        print_btn.clicked.connect(self.print_homework)
        toolbar.addWidget(print_btn)
        
        card_layout.addLayout(toolbar)
        
        # الجدول
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "المادة", "تاريخ الواجب", "العنوان", "الوصف", 
            "تاريخ الاستحقاق", "الحالة"
        ])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 170)
        self.table.setColumnWidth(3, 300)
        self.table.setColumnWidth(4, 140)
        self.table.setColumnWidth(5, 80)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.edit_homework)
        card_layout.addWidget(self.table)
        
        main_layout.addWidget(table_card)
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_data(self):
        """تحميل الواجبات - Local أو Remote."""
        self.loading_overlay.show_loading("جاري تحميل الواجبات...")
        academic_year_id = self.academic_year_id

        def _fetch_data():
            # ✅ Remote
            if OperationsFactory.is_remote():
                return OperationsFactory.get_service() \
                    .list_homeworks(academic_year_id)

            # Local
            with session_scope() as session:
                grades = session.execute(
                    select(Grade).order_by(Grade.grade_name)
                ).scalars().all()
                grades_data = [
                    {'id': g.id, 'name': g.grade_name or ''}
                    for g in grades
                ]

                sections = session.execute(
                    select(Section).order_by(Section.section_name)
                ).scalars().all()
                sections_data = [
                    {
                        'id': s.id,
                        'name': s.section_name or '',
                        'grade_id': s.grade_id,
                        'grade_name': '',
                    }
                    for s in sections
                ]

                subjects = session.execute(
                    select(Subject).order_by(Subject.subject_name)
                ).scalars().all()
                subjects_data = [
                    {'id': s.id, 'name': s.subject_name or ''}
                    for s in subjects
                ]

                homeworks = session.execute(
                    select(Homework).where(
                        Homework.academic_year_id == academic_year_id
                    ).order_by(Homework.homework_date.desc())
                ).scalars().all()

                # خرائط
                grade_map = {g['id']: g['name'] for g in grades_data}
                section_map = {s['id']: s['name'] for s in sections_data}
                subject_map = {s['id']: s['name'] for s in subjects_data}

                today = date.today()
                items = []
                for hw in homeworks:
                    is_late = bool(hw.due_date and hw.due_date < today)
                    items.append({
                        'id': hw.id,
                        'subject_id': hw.subject_id,
                        'subject_name': subject_map.get(hw.subject_id, ''),
                        'grade_id': hw.grade_id,
                        'grade_name': grade_map.get(hw.grade_id, ''),
                        'section_id': hw.section_id,
                        'section_name': section_map.get(hw.section_id, ''),
                        'homework_date_str': (
                            hw.homework_date.strftime("%Y/%m/%d")
                            if hw.homework_date else ''
                        ),
                        'due_date_str': (
                            hw.due_date.strftime("%Y/%m/%d")
                            if hw.due_date else ''
                        ),
                        'title': hw.title or '',
                        'description': hw.description or '',
                        'status': 'متأخر' if is_late else 'نشط',
                        'is_late': is_late,
                    })

                # أضف grade_name للشعب
                for s in sections_data:
                    s['grade_name'] = grade_map.get(s['grade_id'], '')

                return {
                    'grades': grades_data,
                    'sections': sections_data,
                    'subjects': subjects_data,
                    'homeworks': items,
                }

        def _on_result(data):
            try:
                self.grade_filter.blockSignals(True)
                self.grade_filter.clear()
                self.grade_filter.addItem("جميع الصفوف", None)
                for grade in data['grades']:
                    self.grade_filter.addItem(grade['name'], grade['id'])
                self.grade_filter.blockSignals(False)

                self.section_filter.blockSignals(True)
                self.section_filter.clear()
                self.section_filter.addItem("جميع الشعب", None)
                for section in data['sections']:
                    display = (
                        f"{section['grade_name']} - {section['name']}"
                        if section.get('grade_name') else section['name']
                    )
                    self.section_filter.addItem(display, section['id'])
                self.section_filter.blockSignals(False)

                self.subject_filter.blockSignals(True)
                self.subject_filter.clear()
                self.subject_filter.addItem("جميع المواد", None)
                for subject in data['subjects']:
                    self.subject_filter.addItem(subject['name'], subject['id'])
                self.subject_filter.blockSignals(False)

                self.all_homeworks = data['homeworks']
                self.current_filtered_homeworks = list(self.all_homeworks)
                self.display_homeworks(self.all_homeworks)

            except Exception as e:
                print(f"خطأ في تحديث الواجهة: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            print(f"فشل تحميل البيانات: {error_msg}")
            self.all_homeworks = []
            self.current_filtered_homeworks = []
            self.display_homeworks([])

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
        
    # ============================================================
    # ✅ عرض البيانات
    # ============================================================
    
    def display_homeworks(self, homeworks: List[Dict]):
        """عرض الواجبات في الجدول."""
        self.table.setRowCount(len(homeworks))
        
        for row, hw in enumerate(homeworks):
            # المادة
            self.table.setItem(
                row, 0, QTableWidgetItem(hw['subject_name'])
            )
            
            self.table.setItem(
                row, 1, QTableWidgetItem(hw['homework_date_str'])
            )
            self.table.setItem(row, 2, QTableWidgetItem(hw['title']))
            self.table.setItem(row, 3, QTableWidgetItem(hw['description']))
            self.table.setItem(
                row, 4, QTableWidgetItem(hw['due_date_str'])
            )
            
            # الحالة
            status_item = QTableWidgetItem(hw['status'])
            if hw['is_late']:
                status_item.setForeground(QColor('#EF4444'))
            else:
                status_item.setForeground(QColor('#10B981'))
            self.table.setItem(row, 5, status_item)
            
            self.table.setRowHeight(row, 35)

        self.count_label.setText(f"إجمالي الواجبات: {len(homeworks)}")
    
    def filter_homeworks(self):
        """تصفية الواجبات."""
        grade_id = self.grade_filter.currentData()
        section_id = self.section_filter.currentData()
        subject_id = self.subject_filter.currentData()
        
        filtered = []
        for hw in self.all_homeworks:
            if grade_id and hw['grade_id'] != grade_id:
                continue
            if section_id and hw['section_id'] != section_id:
                continue
            if subject_id and hw['subject_id'] != subject_id:
                continue
            filtered.append(hw)
        
        self.current_filtered_homeworks = filtered
        self.display_homeworks(filtered)
    
    # ============================================================
    # ✅ الحصول على الواجب المحدد
    # ============================================================
    
    def _get_selected_homework_id(self) -> Optional[int]:
        """الحصول على ID الواجب المحدد."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
        
        if current_row >= len(self.current_filtered_homeworks):
            return None
        
        return self.current_filtered_homeworks[current_row]['id']
    
    # ============================================================
    # ✅ العمليات
    # ============================================================
    
    def add_homework(self):
        """إضافة واجب جديد."""
        if self.permission_service and not self.permission_service.can_add("الواجبات المنزلية"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للإضافة في الواجبات المنزلية"
            )
            return

        dialog = HomeworkDialog(self.academic_year_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            QMessageBox.information(self, "نجاح", "تم إضافة الواجب بنجاح")
    
    def edit_homework(self):
        if self.permission_service and not self.permission_service.can_edit("الواجبات المنزلية"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        homework_id = self._get_selected_homework_id()
        if not homework_id:
            QMessageBox.warning(self, "تنبيه", "اختر واجباً")
            return

        def _fetch():
            if OperationsFactory.is_remote():
                data = OperationsFactory.get_service() \
                    .get_homework(homework_id)
                for k in ('homework_date', 'due_date'):
                    if data.get(k) and isinstance(data[k], str):
                        try:
                            data[k] = date.fromisoformat(data[k])
                        except Exception:
                            pass
                return data
            with session_scope() as session:
                hw = session.get(Homework, homework_id)
                if not hw:
                    return None
                return {
                    'id': hw.id,
                    'grade_id': hw.grade_id,
                    'section_id': hw.section_id,
                    'subject_id': hw.subject_id,
                    'homework_date': hw.homework_date,
                    'due_date': hw.due_date,
                    'title': hw.title or '',
                    'description': hw.description or '',
                }

        def _ok(data):
            if not data:
                QMessageBox.warning(self, "تنبيه", "الواجب غير موجود")
                return
            dialog = HomeworkDialog(
                self.academic_year_id,
                homework_data=data,
                parent=self,
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_data()
                QMessageBox.information(self, "نجاح", "تم التحديث")

        def _err(m):
            QMessageBox.critical(self, "خطأ", str(m))

        run_async(_fetch, on_result=_ok, on_error=_err)

    def delete_homework(self):
        if self.permission_service and not self.permission_service.can_delete("الواجبات المنزلية"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        homework_id = self._get_selected_homework_id()
        if not homework_id:
            QMessageBox.warning(self, "تنبيه", "اختر واجباً")
            return

        hw = next(
            (h for h in self.current_filtered_homeworks
             if h['id'] == homework_id), None
        )
        if not hw:
            return

        reply = QMessageBox.question(
            self, "حذف واجب", f"حذف: {hw['title']}؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        def _do():
            if OperationsFactory.is_remote():
                OperationsFactory.get_service().delete_homework(homework_id)
            else:
                with session_scope() as session:
                    obj = session.get(Homework, homework_id)
                    if obj:
                        session.delete(obj)
                        session.commit()

        def _ok(_):
            QMessageBox.information(self, "نجاح", "تم الحذف")
            self.load_data()

        def _err(m):
            QMessageBox.critical(self, "خطأ", str(m))

        run_async(_do, on_result=_ok, on_error=_err)

    def print_homework(self):
        """طباعة واجبات."""
        if self.permission_service and not self.permission_service.can_print("الواجبات المنزلية"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للطباعة في الواجبات المنزلية"
            )
            return

        QMessageBox.information(
            self, "طباعة",
            "سيتم تنفيذ الطباعة في مرحلة التقارير"
        )
    
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
# ✅ نافذة إضافة/تعديل واجب (مع dicts)
# ============================================================

class HomeworkDialog(ModernDialog):
    """نافذة إضافة/تعديل واجب - مع تحميل غير متزامن."""
    
    def __init__(self, academic_year_id: int, 
                 homework_data: Optional[dict] = None, parent=None):
        super().__init__(
            "تعديل واجب" if homework_data else "إضافة واجب جديد",
            "fa5s.tasks",
            parent,
            width=500,
            height=700
        )
        
        # ✅ تخزين ID فقط
        self.academic_year_id = academic_year_id
        self.homework_data = homework_data
        self.homework_id = homework_data['id'] if homework_data else None
        
        self._is_loaded = False
        
        self.setup_form()
        
        # ✅ تحميل أولي
        QTimer.singleShot(50, self._load_initial_data)
    
    def setup_form(self):
        """إعداد النموذج."""
        
        # الصف
        self.add_widget(self._create_label("الصف:"))
        self.grade_combo = QComboBox()
        self.grade_combo.currentIndexChanged.connect(self.load_sections)
        self.add_widget(self.grade_combo)
        
        # الشعبة
        self.add_widget(self._create_label("الشعبة:"))
        self.section_combo = QComboBox()
        self.add_widget(self.section_combo)
        
        # المادة
        self.add_widget(self._create_label("المادة:"))
        self.subject_combo = QComboBox()
        self.add_widget(self.subject_combo)
        
        # تاريخ الواجب
        self.add_widget(self._create_label("تاريخ الواجب:"))
        self.date_input = QDateEditEN()
        self.add_widget(self.date_input)
        
        # عنوان الواجب
        self.add_widget(self._create_label("عنوان الواجب:"))
        self.title_input = QLineEditPlus(placeholder="أدخل عنوان الواجب")
        self.add_widget(self.title_input)
        
        # ✅ Bug fixed: استخدام QTextEdit بدلاً من QLineEditPlus
        # لأن الكود الأصلي كان يستدعي toPlainText()
        self.add_widget(self._create_label("الوصف التفصيلي:"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("أدخل وصف الواجب...")
        self.description_input.setMaximumHeight(80)
        self.description_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                background: #F8FAFC;
            }
            QTextEdit:focus {
                border-color: #1976D3;
                background: white;
            }
        """)
        self.add_widget(self.description_input)
        
        # تاريخ الاستحقاق
        self.add_widget(self._create_label("تاريخ الاستحقاق:"))
        self.due_date_input = QDateEditEN(QDate.currentDate().addDays(7))
        self.add_widget(self.due_date_input)

        # الأزرار
        self.add_button("إلغاء", self.reject, "default")
        self.add_button("حفظ", self.save_homework, "primary")


    def _create_label(self, text: str) -> QLabel:
        """إنشاء تسمية."""
        label = QLabel(text)
        label.setStyleSheet("color: #475569; font-weight: 600; font-size: 12px;")
        return label                
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def _load_initial_data(self):
        """تحميل البيانات الأولية."""
        def _fetch_data():
            with session_scope() as session:
                grades = session.execute(
                    select(Grade).order_by(Grade.grade_name)
                ).scalars().all()
                
                subjects = session.execute(
                    select(Subject).order_by(Subject.subject_name)
                ).scalars().all()
                
                return {
                    'grades': [
                        {'id': g.id, 'name': g.grade_name or ''}
                        for g in grades
                    ],
                    'subjects': [
                        {'id': s.id, 'name': s.subject_name or ''}
                        for s in subjects
                    ],
                }
        
        def _on_result(data):
            try:
                # ✅ تعبئة الصفوف
                self.grade_combo.blockSignals(True)
                self.grade_combo.clear()
                for grade in data['grades']:
                    self.grade_combo.addItem(grade['name'], grade['id'])
                self.grade_combo.blockSignals(False)
                
                # ✅ تعبئة المواد
                self.subject_combo.blockSignals(True)
                self.subject_combo.clear()
                for subject in data['subjects']:
                    self.subject_combo.addItem(subject['name'], subject['id'])
                self.subject_combo.blockSignals(False)
                
                self._is_loaded = True
                
                # ✅ تحميل الشعب
                self.load_sections()
                
                # ✅ إذا كنا في وضع التعديل، عبّئ البيانات
                if self.homework_data:
                    self._fill_homework_data()
            except Exception as e:
                print(f"خطأ: {str(e)}")
        
        run_async(_fetch_data, on_result=_on_result)
    
    def load_sections(self):
        """تحميل الشعب حسب الصف - Local أو Remote."""
        grade_id = self.grade_combo.currentData()

        def _fetch_data():
            if OperationsFactory.is_remote():
                from app.services.student_factory import StudentFactory
                service = StudentFactory.get_service()
                sections = service.list_sections(grade_id=grade_id)
                return [
                    {'id': s['id'], 'name': s.get('name', '')}
                    for s in sections
                ]
            with session_scope() as session:
                if not grade_id:
                    return []
                sections = session.execute(
                    select(Section)
                    .where(Section.grade_id == grade_id)
                    .order_by(Section.section_name)
                ).scalars().all()
                return [
                    {'id': s.id, 'name': s.section_name or ''}
                    for s in sections
                ]

        def _on_result(data):
            try:
                current_section = self.section_combo.currentData()
                self.section_combo.blockSignals(True)
                self.section_combo.clear()
                for section in data:
                    self.section_combo.addItem(section['name'], section['id'])
                self.section_combo.blockSignals(False)
                if current_section:
                    idx = self.section_combo.findData(current_section)
                    if idx >= 0:
                        self.section_combo.setCurrentIndex(idx)
            except Exception as e:
                print(f"خطأ: {str(e)}")

        run_async(_fetch_data, on_result=_on_result)

    def _fill_homework_data(self):
        """تعبئة بيانات الواجب للتعديل."""
        if not self.homework_data:
            return
        
        d = self.homework_data
        
        # تحديد الصف
        if d['grade_id']:
            index = self.grade_combo.findData(d['grade_id'])
            if index >= 0:
                self.grade_combo.setCurrentIndex(index)
                # ✅ load_sections سيُستدعى تلقائياً عبر currentIndexChanged
                # لكن قد نحتاج تأخيراً بسيطاً لضمان التحميل
                QTimer.singleShot(100, lambda: self._set_section(d['section_id']))
        
        # تحديد المادة
        if d['subject_id']:
            index = self.subject_combo.findData(d['subject_id'])
            if index >= 0:
                self.subject_combo.setCurrentIndex(index)
        
        # التاريخ
        if d['homework_date']:
            self.date_input.setDate(QDate(
                d['homework_date'].year,
                d['homework_date'].month,
                d['homework_date'].day
            ))
        
        # العنوان والوصف
        self.title_input.setText(d['title'])
        self.description_input.setPlainText(d['description'])
        
        # تاريخ الاستحقاق
        if d['due_date']:
            self.due_date_input.setDate(QDate(
                d['due_date'].year,
                d['due_date'].month,
                d['due_date'].day
            ))
    
    def _set_section(self, section_id: int):
        """تعيين الشعبة بعد تحميل الشعب."""
        if not section_id:
            return
        index = self.section_combo.findData(section_id)
        if index >= 0:
            self.section_combo.setCurrentIndex(index)
    
    def save_homework(self):
        """حفظ الواجب - Local أو Remote."""
        if not self._is_loaded:
            QMessageBox.warning(self, "تنبيه", "انتظر التحميل")
            return
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "تنبيه", "أدخل العنوان")
            return
        if not self.grade_combo.currentData() \
           or not self.section_combo.currentData() \
           or not self.subject_combo.currentData():
            QMessageBox.warning(self, "تنبيه", "أكمل الحقول")
            return

        hd = self.date_input.date()
        dd = self.due_date_input.date()
        payload = {
            'academic_year_id': self.academic_year_id,
            'grade_id': self.grade_combo.currentData(),
            'section_id': self.section_combo.currentData(),
            'subject_id': self.subject_combo.currentData(),
            'homework_date': date(
                hd.year(), hd.month(), hd.day()
            ).isoformat(),
            'due_date': date(dd.year(), dd.month(), dd.day()).isoformat(),
            'title': self.title_input.text().strip(),
            'description': self.description_input.toPlainText().strip()
                or None,
        }

        try:
            if OperationsFactory.is_remote():
                service = OperationsFactory.get_service()
                if self.homework_id:
                    service.update_homework(self.homework_id, payload)
                else:
                    service.create_homework(payload)
            else:
                self._save_local(payload)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", str(e))

    def _save_local(self, payload):
        with session_scope() as session:
            if self.homework_id:
                hw = session.get(Homework, self.homework_id)
            else:
                hw = Homework()
                session.add(hw)
            hw.academic_year_id = payload['academic_year_id']
            hw.grade_id = payload['grade_id']
            hw.section_id = payload['section_id']
            hw.subject_id = payload['subject_id']
            hw.homework_date = date.fromisoformat(payload['homework_date'])
            hw.due_date = date.fromisoformat(payload['due_date'])
            hw.title = payload['title']
            hw.description = payload['description']
            session.commit()