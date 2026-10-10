"""
واجهة المتابعة السلوكية والتوجيه التربوي - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta
from datetime import date

from app.database.session import session_scope
from app.database.models import Student, BehavioralRecord, AcademicYear
from app.services.operations_factory import OperationsFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    PageHeader, Card, QDateEditEN, QLineEditPlus, SearchBox, 
    ModernTable, Badge, GradientButton, IconButton
)
from app.views.widgets.dialogs import (
    ConfirmationDialog, SuccessDialog, ErrorDialog, ModernDialog
)
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class BehaviorPage(QWidget):
    """صفحة المتابعة السلوكية - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ تخزين ID السنة قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        
        # ✅ dicts بدلاً من ORM
        self.all_records: List[Dict] = []
        self.current_filtered_records: List[Dict] = []
        
        # ✅ debounce للبحث
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self.filter_records)
        
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
        header_label = QLabel("المتابعة السلوكية والتوجيه التربوي")
        header_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(header_label)
        
        sub_label = QLabel("تسجيل ومتابعة الملاحظات السلوكية للطلاب")
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
        
        self.search_box = SearchBox("بحث عن طالب...")
        self.search_box.textChanged.connect(self._on_search_text_changed)
        filter_layout.addWidget(self.search_box)
        
        filter_layout.addWidget(QLabel("نوع السلوك:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["جميع الأنواع", "تميز", "مخالفة", "تنبيه أخصائي"])
        self.type_filter.currentIndexChanged.connect(self.filter_records)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addStretch()
        
        add_btn = GradientButton("إضافة متابعة سلوكية", "fa5s.plus")
        add_btn.clicked.connect(self.add_behavior)
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
        
        self.count_label = QLabel("إجمالي الملاحظات: 0")
        self.count_label.setObjectName("count_label")
        toolbar.addWidget(self.count_label)
        
        toolbar.addStretch()
        
        edit_btn = IconButton('fa5s.edit', "تعديل", color='#1976D3')
        edit_btn.clicked.connect(self.edit_record)
        toolbar.addWidget(edit_btn)
        
        delete_btn = IconButton('fa5s.trash', "حذف", color='#EF4444')
        delete_btn.clicked.connect(self.delete_record)
        toolbar.addWidget(delete_btn)
        
        print_btn = IconButton('fa5s.print', "طباعة", color='#10B981')
        print_btn.clicked.connect(self.print_record)
        toolbar.addWidget(print_btn)
        
        card_layout.addLayout(toolbar)
        
        # الجدول
        self.table = ModernTable()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "اسم الطالب", "نوع السلوك", "العنوان", "التفاصيل", 
            "الإجراء المتخذ", "التاريخ", "الحالة"
        ])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 100)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.edit_record)
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
        """تحميل الملاحظات السلوكية - Local أو Remote."""
        self.loading_overlay.show_loading("جاري تحميل الملاحظات...")
        academic_year_id = self.academic_year_id

        def _fetch_data():
            # ✅ Remote
            if OperationsFactory.is_remote():
                return OperationsFactory.get_service() \
                    .list_behavior(academic_year_id)

            # Local
            with session_scope() as session:
                records = session.execute(
                    select(BehavioralRecord).where(
                        BehavioralRecord.academic_year_id == academic_year_id
                    ).order_by(BehavioralRecord.record_date.desc())
                ).scalars().all()

                # خرائط الطلاب
                student_ids = {r.student_id for r in records if r.student_id}
                student_map = {}
                if student_ids:
                    students = session.execute(
                        select(Student).where(Student.id.in_(student_ids))
                    ).scalars().all()
                    student_map = {
                        s.id: (s.full_name or '') for s in students
                    }

                return [
                    {
                        'id': r.id,
                        'student_id': r.student_id,
                        'student_name': student_map.get(
                            r.student_id, 'غير معروف'
                        ),
                        'behavior_type': r.behavior_type or '',
                        'title': r.title or '',
                        'details': r.details or '',
                        'action_taken': r.action_taken or '',
                        'record_date_str': (
                            r.record_date.strftime("%Y/%m/%d")
                            if r.record_date else ''
                        ),
                    }
                    for r in records
                ]

        def _on_result(data):
            try:
                self.all_records = data
                self.current_filtered_records = list(self.all_records)
                self.display_records(self.all_records)
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            ErrorDialog("خطأ", f"فشل التحميل:\n{error_msg}", self).exec()

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
        
    # ============================================================
    # ✅ عرض البيانات
    # ============================================================
    
    def display_records(self, records: List[Dict]):
        """عرض السجلات في الجدول."""
        self.table.setRowCount(len(records))
        
        type_colors = {
            'تميز': '#10B981',
            'مخالفة': '#EF4444',
            'تنبيه أخصائي': '#F59E0B'
        }
        
        for row, record in enumerate(records):
            self.table.setItem(
                row, 0, QTableWidgetItem(record['student_name'])
            )
            
            # نوع السلوك
            type_item = QTableWidgetItem(record['behavior_type'])
            type_item.setForeground(
                QColor(type_colors.get(record['behavior_type'], '#64748B'))
            )
            self.table.setItem(row, 1, type_item)
            
            self.table.setItem(
                row, 2, QTableWidgetItem(record['title'])
            )
            self.table.setItem(
                row, 3, QTableWidgetItem(record['details'])
            )
            self.table.setItem(
                row, 4, QTableWidgetItem(record['action_taken'])
            )
            self.table.setItem(
                row, 5, QTableWidgetItem(record['record_date_str'])
            )
            
            # الحالة
            status_item = QTableWidgetItem(
                "مسجل" if record['action_taken'] else "جديد"
            )
            status_item.setForeground(
                QColor('#10B981') if record['action_taken'] 
                else QColor('#F59E0B')
            )
            self.table.setItem(row, 6, status_item)
            self.table.setRowHeight(row, 35)
        
        self.count_label.setText(f"إجمالي الملاحظات: {len(records)}")
    
    # ============================================================
    # ✅ الفلترة
    # ============================================================
    
    def _on_search_text_changed(self):
        """عند تغيير نص البحث - debounce."""
        self._search_timer.stop()
        self._search_timer.start()
    
    def filter_records(self):
        """تصفية السجلات."""
        search_text = self.search_box.text().lower().strip()
        type_filter = self.type_filter.currentText()
        
        filtered = []
        for record in self.all_records:
            # فلتر البحث
            if search_text:
                student_name = record['student_name'].lower()
                title = record['title'].lower()
                if search_text not in student_name and search_text not in title:
                    continue
            
            # فلتر النوع
            if type_filter != "جميع الأنواع" and \
               record['behavior_type'] != type_filter:
                continue
            
            filtered.append(record)
        
        self.current_filtered_records = filtered
        self.display_records(filtered)
    
    # ============================================================
    # ✅ الحصول على السجل المحدد
    # ============================================================
    
    def _get_selected_record_id(self) -> Optional[int]:
        """الحصول على ID السجل المحدد."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
        
        if current_row >= len(self.current_filtered_records):
            return None
        
        return self.current_filtered_records[current_row]['id']
    
    # ============================================================
    # ✅ العمليات
    # ============================================================
    
    def add_behavior(self):
        """إضافة ملاحظة جديدة."""
        if self.permission_service and not self.permission_service.can_add("المتابعة السلوكية"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للإضافة في المتابعة السلوكية"
            )
            return

        dialog = BehaviorDialog(self.academic_year_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            SuccessDialog("نجاح", "تم إضافة الملاحظة بنجاح", self).exec()
    
    def edit_record(self):
        if self.permission_service and not self.permission_service.can_edit("المتابعة السلوكية"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        record_id = self._get_selected_record_id()
        if not record_id:
            ErrorDialog("تنبيه", "اختر ملاحظة", self).exec()
            return

        def _fetch():
            if OperationsFactory.is_remote():
                data = OperationsFactory.get_service() \
                    .get_behavior(record_id)
                if data and isinstance(data.get('record_date'), str):
                    try:
                        data['record_date'] = date.fromisoformat(
                            data['record_date']
                        )
                    except Exception:
                        pass
                return data
            with session_scope() as session:
                r = session.get(BehavioralRecord, record_id)
                if not r:
                    return None
                return {
                    'id': r.id,
                    'student_id': r.student_id,
                    'behavior_type': r.behavior_type or '',
                    'title': r.title or '',
                    'details': r.details or '',
                    'action_taken': r.action_taken or '',
                    'record_date': r.record_date,
                }

        def _ok(data):
            if not data:
                ErrorDialog("خطأ", "غير موجود", self).exec()
                return
            dialog = BehaviorDialog(
                self.academic_year_id, record_data=data, parent=self
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_data()
                SuccessDialog("نجاح", "تم التحديث", self).exec()

        def _err(m):
            ErrorDialog("خطأ", str(m), self).exec()

        run_async(_fetch, on_result=_ok, on_error=_err)

    def delete_record(self):
        if self.permission_service and not self.permission_service.can_delete("المتابعة السلوكية"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        record_id = self._get_selected_record_id()
        if not record_id:
            ErrorDialog("تنبيه", "اختر ملاحظة", self).exec()
            return

        rec = next(
            (r for r in self.current_filtered_records
             if r['id'] == record_id), None
        )
        if not rec:
            return

        if ConfirmationDialog(
            "حذف ملاحظة",
            f"حذف: {rec['title']}؟",
            self,
        ).exec() != QDialog.DialogCode.Accepted:
            return

        def _do():
            if OperationsFactory.is_remote():
                OperationsFactory.get_service().delete_behavior(record_id)
            else:
                with session_scope() as session:
                    obj = session.get(BehavioralRecord, record_id)
                    if obj:
                        session.delete(obj)
                        session.commit()

        def _ok(_):
            SuccessDialog("نجاح", "تم الحذف", self).exec()
            self.load_data()

        def _err(m):
            ErrorDialog("خطأ", str(m), self).exec()

        run_async(_do, on_result=_ok, on_error=_err)

    def print_record(self):
        """طباعة الملاحظات."""
        if self.permission_service and not self.permission_service.can_print("المتابعة السلوكية"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للطباعة في المتابعة السلوكية"
            )
            return

        QMessageBox.information(
            self, 
            "طباعة", 
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
# ✅ نافذة إضافة/تعديل ملاحظة سلوكية (مع dicts)
# ============================================================

class BehaviorDialog(ModernDialog):
    """نافذة إضافة/تعديل ملاحظة سلوكية - مع تحميل غير متزامن."""
    
    def __init__(self, academic_year_id: int, 
                 record_data: Optional[dict] = None, parent=None):
        super().__init__(
            "تعديل ملاحظة" if record_data else "إضافة ملاحظة سلوكية",
            "fa5s.comments",
            parent,
            width=500,
            height=700
        )
        
        # ✅ تخزين ID فقط
        self.academic_year_id = academic_year_id
        self.record_data = record_data
        self.record_id = record_data['id'] if record_data else None
        
        # ✅ dicts
        self.students_data: List[Dict] = []
        self.selected_student_id: Optional[int] = None
        
        # ✅ debounce للبحث
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self._search_students_now)
        
        self.setup_form()
        
        # ✅ تحميل أولي
        QTimer.singleShot(50, self._load_initial_data)
    
    def setup_form(self):
        """إعداد النموذج."""
        # بحث عن طالب
        self.add_widget(self._create_label("البحث عن طالب:"))
        
        search_layout = QHBoxLayout()
        self.student_search = QLineEditPlus(placeholder="ابحث بالاسم أو الرقم...")
        self.student_search.textChanged.connect(self._on_search_text_changed)
        search_layout.addWidget(self.student_search)
        
        search_btn = GradientButton("بحث", 'fa5s.search')
        search_btn.clicked.connect(self._search_students_now)
        search_layout.addWidget(search_btn)
        
        self.add_widget(self._create_widget(search_layout))
        
        # قائمة الطلاب
        self.students_list = QListWidget()
        self.students_list.setMaximumHeight(120)
        self.add_widget(self.students_list)
        
        # نوع السلوك
        self.add_widget(self._create_label("نوع السلوك:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["تميز", "مخالفة", "تنبيه أخصائي"])
        self.add_widget(self.type_combo)
        
        # العنوان
        self.add_widget(self._create_label("عنوان الملاحظة:"))
        self.title_input = QLineEditPlus(placeholder="أدخل عنوان الملاحظة")
        self.add_widget(self.title_input)
        
        # التفاصيل
        self.add_widget(self._create_label("التفاصيل:"))
        self.details_input = QTextEdit()
        self.details_input.setMaximumHeight(60)
        self.add_widget(self.details_input)
        
        # الإجراء المتخذ
        self.add_widget(self._create_label("الإجراء المتخذ:"))
        self.action_input = QTextEdit()
        self.action_input.setMaximumHeight(60)
        self.add_widget(self.action_input)
        
        # التاريخ
        self.add_widget(self._create_label("التاريخ:"))
        self.date_input = QDateEditEN()
        self.add_widget(self.date_input)
        
        # الأزرار
        self.add_button("إلغاء", self.reject, "default")
        self.add_button("حفظ", self.save_record, "primary")
        
        self.students_list.itemClicked.connect(self.select_student)
    
    def _create_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            "color: #475569; font-weight: 600; font-size: 12px;"
        )
        return label
    
    def _create_widget(self, layout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def _load_initial_data(self):
        """تحميل البيانات الأولية."""
        if self.record_data:
            # ✅ تحميل بيانات الملاحظة
            d = self.record_data
            
            self.type_combo.setCurrentText(d['behavior_type'])
            self.title_input.setText(d['title'])
            self.details_input.setText(d['details'])
            self.action_input.setText(d['action_taken'])
            
            if d['record_date']:
                self.date_input.setDate(QDate(
                    d['record_date'].year,
                    d['record_date'].month,
                    d['record_date'].day
                ))
            
            # ✅ تخزين ID الطالب المختار
            self.selected_student_id = d['student_id']
            
            # ✅ تحميل اسم الطالب
            self._load_student_info(d['student_id'])
        else:
            # تحميل أولي للطلاب
            self._search_students_now()
    
    def _load_student_info(self, student_id: int):
        """تحميل معلومات الطالب - Local أو Remote."""
        def _fetch_data():
            if OperationsFactory.is_remote():
                from app.services.student_factory import StudentFactory
                service = StudentFactory.get_service()
                data = service.get(student_id)
                return {
                    'id': data['id'],
                    'full_name': data['full_name'],
                    'student_number': data.get('student_number', ''),
                }
            with session_scope() as session:
                student = session.get(Student, student_id)
                if not student:
                    return None
                return {
                    'id': student.id,
                    'full_name': student.full_name or '',
                    'student_number': student.student_number or '',
                }

        def _on_result(data):
            if data:
                self.student_search.setText(
                    f"{data['full_name']} - {data['student_number']}"
                )

        run_async(_fetch_data, on_result=_on_result)

    def _on_search_text_changed(self):
        """عند تغيير نص البحث - debounce."""
        self._search_timer.stop()
        self._search_timer.start()
    
    def _search_students_now(self):
        """البحث عن الطلاب - Local أو Remote."""
        search_text = self.student_search.text().strip()

        def _fetch_data():
            if OperationsFactory.is_remote():
                from app.services.student_factory import StudentFactory
                service = StudentFactory.get_service()
                return service.lookup(
                    search=search_text or None,
                    limit=20,
                )
            with session_scope() as session:
                query = select(Student)
                if search_text:
                    query = query.where(
                        (Student.full_name.ilike(f"%{search_text}%")) |
                        (Student.student_number.ilike(f"%{search_text}%"))
                    )
                students = session.execute(query.limit(20)).scalars().all()
                return [
                    {
                        'id': s.id,
                        'full_name': s.full_name or '',
                        'student_number': s.student_number or '',
                    }
                    for s in students
                ]

        def _on_result(data):
            self.students_data = data
            self.students_list.clear()
            for student in data:
                item = QListWidgetItem(
                    f"{student['full_name']} - {student['student_number']}"
                )
                item.setData(Qt.ItemDataRole.UserRole, student['id'])
                self.students_list.addItem(item)

        run_async(_fetch_data, on_result=_on_result)

    def select_student(self, item: QListWidgetItem):
        """اختيار طالب."""
        self.selected_student_id = item.data(Qt.ItemDataRole.UserRole)
    
    def save_record(self):
        """حفظ الملاحظة - Local أو Remote."""
        if not self.selected_student_id:
            ErrorDialog("تنبيه", "اختر طالباً", self).exec()
            return
        if not self.title_input.text().strip():
            ErrorDialog("تنبيه", "أدخل العنوان", self).exec()
            return

        rd = self.date_input.date()
        payload = {
            'academic_year_id': self.academic_year_id,
            'student_id': self.selected_student_id,
            'behavior_type': self.type_combo.currentText(),
            'title': self.title_input.text().strip(),
            'details': self.details_input.toPlainText().strip() or None,
            'action_taken': self.action_input.toPlainText().strip() or None,
            'record_date': date(
                rd.year(), rd.month(), rd.day()
            ).isoformat(),
        }

        try:
            if OperationsFactory.is_remote():
                service = OperationsFactory.get_service()
                if self.record_id:
                    service.update_behavior(self.record_id, payload)
                else:
                    service.create_behavior(payload)
            else:
                self._save_local(payload)
            self.accept()
        except Exception as e:
            ErrorDialog("خطأ", str(e), self).exec()

    def _save_local(self, payload):
        with session_scope() as session:
            if self.record_id:
                record = session.get(BehavioralRecord, self.record_id)
            else:
                record = BehavioralRecord()
                session.add(record)
            record.student_id = payload['student_id']
            record.academic_year_id = payload['academic_year_id']
            record.behavior_type = payload['behavior_type']
            record.title = payload['title']
            record.details = payload['details']
            record.action_taken = payload['action_taken']
            record.record_date = date.fromisoformat(payload['record_date'])
            session.commit()