"""
نافذة إضافة/تعديل طالب - تعمل Local أو Remote.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Optional, Dict, List
import qtawesome as qta
from datetime import date

from app.services.student_factory import StudentFactory
from app.views.widgets.custom_widgets import (
    QDateEditEN, QLineEditPlus, SearchBox
)
from app.views.widgets.dialogs import ModernDialog, ErrorDialog


class StudentDialog(ModernDialog):
    """نافذة إضافة/تعديل طالب - Local أو Remote."""

    def __init__(self, academic_year, user,
                 student=None, parent=None):
        super().__init__(
            "تعديل بيانات طالب" if student else "إضافة طالب جديد",
            "fa5s.plus",
            parent,
            width=700,
            height=600,
        )

        self.academic_year = academic_year
        self.user = user
        self.student = student
        self.parent_data: Optional[Dict] = None
        self._all_sections: List[Dict] = []

        self.setup_form()

        if student:
            QTimer.singleShot(100, self.load_student_data)

    def setup_form(self):
        """إعداد النموذج."""
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab { padding: 8px 15px; margin-right: 5px; }
        """)

        self.tabs.addTab(self._create_basic_tab(), "البيانات الأساسية")
        self.tabs.addTab(self._create_birth_tab(), "بيانات الميلاد")
        self.tabs.addTab(self._create_parent_tab(), "ولي الأمر")

        self.add_widget(self.tabs)
        self.add_button("إلغاء", self.reject, "default")
        self.add_button("حفظ", self.save_student, "primary")

    # ==================== Tabs ====================

    def _create_basic_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        layout.addWidget(self._label("رقم الطالب"))
        self.student_number_input = QLineEditPlus("مثال: ST-2024-001")
        layout.addWidget(self.student_number_input)

        layout.addWidget(self._label("الاسم الكامل"))
        self.full_name_input = QLineEditPlus("أدخل الاسم الرباعي")
        layout.addWidget(self.full_name_input)

        layout.addWidget(self._label("اسم الأم"))
        self.mother_name_input = QLineEditPlus("أدخل اسم الأم")
        layout.addWidget(self.mother_name_input)

        gender_layout = QHBoxLayout()
        gender_layout.addWidget(self._label("الجنس"))
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["ذكر", "أنثى"])
        gender_layout.addWidget(self.gender_combo)

        gender_layout.addWidget(self._label("الجنسية"))
        self.nationality_input = QLineEditPlus()
        self.nationality_input.setText("يمني")
        gender_layout.addWidget(self.nationality_input)
        layout.addLayout(gender_layout)

        status_layout = QHBoxLayout()
        status_layout.addWidget(self._label("حالة الطالب"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["مستمر", "انسحاب", "موقف", "خريج"])
        status_layout.addWidget(self.status_combo)

        status_layout.addWidget(self._label("نوع القيد"))
        self.enrollment_combo = QComboBox()
        self.enrollment_combo.addItems(["مستجد", "محول", "باقي"])
        status_layout.addWidget(self.enrollment_combo)
        layout.addLayout(status_layout)

        academic_layout = QHBoxLayout()
        academic_layout.addWidget(self._label("الصف"))
        self.grade_combo = QComboBox()
        academic_layout.addWidget(self.grade_combo)

        academic_layout.addWidget(self._label("الشعبة"))
        self.section_combo = QComboBox()
        academic_layout.addWidget(self.section_combo)
        layout.addLayout(academic_layout)

        layout.addStretch()

        # ✅ ربط الأحداث
        self.grade_combo.currentIndexChanged.connect(
            self._on_grade_changed
        )

        # ✅ تحميل الصفوف في الخلفية
        QTimer.singleShot(50, self._load_grades_and_sections)

        return widget

    def _create_birth_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        layout.addWidget(self._label("تاريخ الميلاد"))
        self.birth_date_input = QDateEditEN()
        layout.addWidget(self.birth_date_input)

        layout.addWidget(self._label("القرية"))
        self.village_input = QLineEditPlus()
        layout.addWidget(self.village_input)

        layout.addWidget(self._label("المديرية"))
        self.district_input = QLineEditPlus()
        layout.addWidget(self.district_input)

        layout.addWidget(self._label("المحافظة"))
        self.governorate_input = QLineEditPlus()
        layout.addWidget(self.governorate_input)

        layout.addStretch()
        return widget

    def _create_parent_tab(self) -> QWidget:
        """إنشاء تبويب ولي الأمر - محسّن."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # ==================== بحث ====================
        search_layout = QHBoxLayout()

        self.parent_search = SearchBox(
            "بحث عن ولي أمر بالاسم أو الهاتف..."
        )
        self.parent_search.textChanged.connect(self._on_parent_search_changed)
        search_layout.addWidget(self.parent_search)

        search_btn = QPushButton("بحث")
        search_btn.setIcon(qta.icon('fa5s.search'))
        search_btn.clicked.connect(self._search_parents)
        search_layout.addWidget(search_btn)

        layout.addLayout(search_layout)

        # ==================== قائمة أولياء الأمور ====================
        self.parents_list = QListWidget()
        self.parents_list.setMaximumHeight(180)
        self.parents_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F1F5F9;
            }
            QListWidget::item:selected {
                background: #1976D3;
                color: white;
                border-radius: 4px;
            }
        """)
        self.parents_list.itemClicked.connect(self._select_parent)
        layout.addWidget(self.parents_list)

        # ==================== معلومات ولي الأمر المختار ====================
        info_row = QHBoxLayout()

        self.parent_info = QLabel("لم يتم اختيار ولي أمر")
        self.parent_info.setWordWrap(True)
        self.parent_info.setStyleSheet("""
            padding: 10px;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            color: #64748B;
            font-size: 12px;
        """)
        info_row.addWidget(self.parent_info, 1)

        # ✅ زر إزالة ولي الأمر
        self.clear_parent_btn = QPushButton("إزالة")
        self.clear_parent_btn.setIcon(qta.icon('fa5s.times', color='#EF4444'))
        self.clear_parent_btn.setStyleSheet("""
            QPushButton {
                background: #FEF2F2;
                color: #EF4444;
                border: 1px solid #FCA5A5;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: 600;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #FEE2E2;
            }
            QPushButton:disabled {
                background: #F1F5F9;
                color: #94A3B8;
                border-color: #E2E8F0;
            }
        """)
        self.clear_parent_btn.setEnabled(False)
        self.clear_parent_btn.clicked.connect(self._clear_parent)
        info_row.addWidget(self.clear_parent_btn)

        layout.addLayout(info_row)
        layout.addStretch()

        # ✅ تحميل أولياء الأمور عند فتح التبويب (بعد ظهور الواجهة)
        QTimer.singleShot(100, self._preload_parents)

        return widget
    
    def _label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            "color: #475569; font-weight: 600; font-size: 12px;"
        )
        return label

    # ==================== Load Data ====================

    def _load_grades_and_sections(self):
        """تحميل الصفوف (Local أو Remote)."""
        try:
            if StudentFactory.is_remote():
                service = StudentFactory.get_service()
                grades = service.list_grades()
                self._all_sections = service.list_sections()
            else:
                from app.database.session import session_scope
                from app.database.models import Grade, Section
                from sqlalchemy import select
                with session_scope() as session:
                    grades_objs = session.execute(
                        select(Grade).order_by(Grade.grade_name)
                    ).scalars().all()
                    grades = [
                        {'id': g.id, 'name': g.grade_name or ''}
                        for g in grades_objs
                    ]
                    sections_objs = session.execute(
                        select(Section)
                    ).scalars().all()
                    self._all_sections = [
                        {
                            'id': s.id,
                            'name': s.section_name or '',
                            'grade_id': s.grade_id,
                            'grade_name': '',
                        }
                        for s in sections_objs
                    ]

            self.grade_combo.blockSignals(True)
            self.grade_combo.clear()
            for g in grades:
                self.grade_combo.addItem(g['name'], g['id'])
            self.grade_combo.blockSignals(False)

            self._on_grade_changed()

        except Exception as e:
            print(f"خطأ في تحميل الصفوف: {e}")

    def _on_grade_changed(self):
        """عند تغيير الصف - تحميل الشعب."""
        grade_id = self.grade_combo.currentData()
        self.section_combo.blockSignals(True)
        self.section_combo.clear()
        if grade_id:
            for s in self._all_sections:
                if s.get('grade_id') == grade_id:
                    self.section_combo.addItem(s['name'], s['id'])
        self.section_combo.blockSignals(False)

    # ==================== أولياء الأمور ====================

    def _on_parent_search_changed(self, text: str):
        """عند تغيير نص البحث - debounce."""
        if not hasattr(self, '_parent_search_timer'):
            self._parent_search_timer = QTimer()
            self._parent_search_timer.setSingleShot(True)
            self._parent_search_timer.setInterval(300)
            self._parent_search_timer.timeout.connect(self._search_parents)

        self._parent_search_timer.stop()
        self._parent_search_timer.start()

    def _preload_parents(self):
        """تحميل أولياء الأمور عند فتح التبويب (بدون بحث)."""
        self._search_parents()

    def _search_parents(self):
        """بحث أولياء الأمور - Local أو Remote."""
        search_text = self.parent_search.text().strip()

        try:
            if StudentFactory.is_remote():
                service = StudentFactory.get_service()
                parents = service.search_parents(search_text, limit=30)
            else:
                from app.database.session import session_scope
                from app.database.models import Parent
                from sqlalchemy import select, or_

                with session_scope() as session:
                    query = select(Parent).where(Parent.deleted_at.is_(None))
                    if search_text:
                        p = f"%{search_text}%"
                        query = query.where(
                            or_(
                                Parent.full_name.ilike(p),
                                Parent.primary_phone.ilike(p),
                            )
                        )
                    query = query.order_by(Parent.full_name).limit(30)
                    parents_objs = session.execute(query).scalars().all()
                    parents = [
                        {
                            'id': p.id,
                            'full_name': p.full_name or '',
                            'primary_phone': p.primary_phone or '',
                            'category': p.category or 'عادي',
                        }
                        for p in parents_objs
                    ]

            self._render_parents_list(parents)

        except Exception as e:
            print(f"خطأ في البحث عن أولياء الأمور: {e}")

    def _render_parents_list(self, parents: List[Dict]):
        """عرض أولياء الأمور في القائمة."""
        self.parents_list.clear()

        # ✅ إذا كان هناك ولي أمر مختار، ضعه في الأعلى دائماً
        current_parent_id = (
            self.parent_data['id'] if self.parent_data else None
        )

        # تأكد من وجود ولي الأمر الحالي في القائمة
        current_parent_in_list = any(
            p['id'] == current_parent_id for p in parents
        ) if current_parent_id else True

        if current_parent_id and not current_parent_in_list:
            # ابحث عن ولي الأمر الحالي وأضفه
            try:
                current_parent = self._fetch_parent_by_id(current_parent_id)
                if current_parent:
                    parents.insert(0, current_parent)
            except Exception as e:
                print(f"فشل جلب ولي الأمر الحالي: {e}")

        # عرض القائمة
        for p in parents:
            label = f"{p['full_name']} - {p['primary_phone']}"
            if p.get('category') and p['category'] != 'عادي':
                label += f" ({p['category']})"

            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, p)

            # ✅ علّم ولي الأمر المختار حالياً
            if p['id'] == current_parent_id:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setForeground(QColor('#059669'))

            self.parents_list.addItem(item)

    def _fetch_parent_by_id(self, parent_id: int) -> Optional[Dict]:
        """جلب ولي أمر بـ ID."""
        try:
            if StudentFactory.is_remote():
                from app.services.auth_factory import AuthFactory
                client = AuthFactory.get_api_client()
                return client.get(f"/api/parents/{parent_id}")
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
                        'category': parent.category or 'عادي',
                    }
        except Exception as e:
            print(f"فشل جلب ولي الأمر #{parent_id}: {e}")
            return None

    def _select_parent(self, item):
        """اختيار ولي أمر من القائمة."""
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return

        self.parent_data = data
        self._display_parent_info(data)

    def _display_parent_info(self, parent_data: Dict):
        """عرض معلومات ولي الأمر المختار."""
        category = parent_data.get('category', 'عادي')
        category_badge = ''
        if category == 'VIP':
            category_badge = ' 🌟 VIP'
        elif category == 'كفالة':
            category_badge = ' 🤝 كفالة'

        self.parent_info.setText(
            f"✅ <b>{parent_data['full_name']}</b>{category_badge}<br>"
            f"📞 {parent_data['primary_phone']}"
        )
        self.parent_info.setStyleSheet("""
            padding: 10px;
            background: #ECFDF5;
            border: 1px solid #6EE7B7;
            border-radius: 8px;
            color: #065F46;
            font-size: 12px;
        """)
        self.clear_parent_btn.setEnabled(True)

    def _clear_parent(self):
        """إزالة ولي الأمر."""
        self.parent_data = None
        self.parent_info.setText("لم يتم اختيار ولي أمر")
        self.parent_info.setStyleSheet("""
            padding: 10px;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            color: #64748B;
            font-size: 12px;
        """)
        self.clear_parent_btn.setEnabled(False)

        # أزل التحديد من القائمة
        self.parents_list.clearSelection()

    def load_student_data(self):
        """تحميل بيانات الطالب للتعديل - مع تحميل ولي الأمر."""
        if not self.student:
            return

        s = self.student

        # ==================== البيانات الأساسية ====================
        self.student_number_input.setText(s.student_number or "")
        self.full_name_input.setText(s.full_name or "")
        self.mother_name_input.setText(
            getattr(s, 'mother_name', '') or ""
        )
        self.gender_combo.setCurrentText(
            getattr(s, 'gender', None) or "ذكر"
        )
        self.nationality_input.setText(
            getattr(s, 'nationality', None) or "يمني"
        )
        self.status_combo.setCurrentText(
            getattr(s, 'status', None) or "مستمر"
        )
        self.enrollment_combo.setCurrentText(
            getattr(s, 'enrollment_type', None) or "مستجد"
        )

        # ==================== الصف والشعبة ====================
        if getattr(s, 'grade_id', None):
            idx = self.grade_combo.findData(s.grade_id)
            if idx >= 0:
                self.grade_combo.setCurrentIndex(idx)
                self._on_grade_changed()

        if getattr(s, 'section_id', None):
            idx = self.section_combo.findData(s.section_id)
            if idx >= 0:
                self.section_combo.setCurrentIndex(idx)

        # ==================== بيانات الميلاد ====================
        birth_date = getattr(s, 'birth_date', None)
        if birth_date:
            if isinstance(birth_date, str):
                try:
                    birth_date = date.fromisoformat(birth_date)
                except Exception:
                    birth_date = None
            if birth_date:
                self.birth_date_input.setDate(QDate(
                    birth_date.year,
                    birth_date.month,
                    birth_date.day,
                ))

        self.village_input.setText(
            getattr(s, 'birth_village', '') or ""
        )
        self.district_input.setText(
            getattr(s, 'birth_district', '') or ""
        )
        self.governorate_input.setText(
            getattr(s, 'birth_governorate', '') or ""
        )

        # ==================== ولي الأمر ====================
        parent_id = getattr(s, 'parent_id', None)
        if parent_id:
            try:
                parent_data = self._fetch_parent_by_id(parent_id)
                if parent_data:
                    self.parent_data = parent_data
                    self._display_parent_info(parent_data)
                    # أضف ولي الأمر للقائمة في الأعلى
                    QTimer.singleShot(150, lambda: self._render_parents_list(
                        self._get_current_parents_list_with_current()
                    ))
            except Exception as e:
                print(f"فشل تحميل ولي الأمر: {e}")

    def _get_current_parents_list_with_current(self) -> List[Dict]:
        """اجلب القائمة الحالية + أضف ولي الأمر الحالي في الأعلى."""
        # نسخة مبسطة: تُعيد قائمة جديدة بها ولي الأمر الحالي في المقدمة
        result = []
        if self.parent_data:
            result.append(self.parent_data)

        # أضف باقي العناصر من القائمة (بعد الإزالة المكررة)
        for i in range(self.parents_list.count()):
            item = self.parents_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            if data and (not self.parent_data or data['id'] != self.parent_data['id']):
                result.append(data)

        return result
    
    # ==================== Save ====================

    def save_student(self):
        """حفظ البيانات."""
        if not self.student_number_input.text().strip():
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال رقم الطالب")
            return
        if not self.full_name_input.text().strip():
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال اسم الطالب")
            return

        birth_date = self.birth_date_input.date()
        birth_date_str = date(
            birth_date.year(), birth_date.month(), birth_date.day()
        ).isoformat()

        parent_id = (
            self.parent_data['id']
            if self.parent_data
            else getattr(self.student, 'parent_id', None)
        )

        payload = {
            'student_number': self.student_number_input.text().strip(),
            'full_name': self.full_name_input.text().strip(),
            'mother_name': self.mother_name_input.text().strip() or None,
            'gender': self.gender_combo.currentText(),
            'nationality': self.nationality_input.text().strip() or 'يمني',
            'status': self.status_combo.currentText(),
            'enrollment_type': self.enrollment_combo.currentText(),
            'academic_year_id': self.academic_year.id,
            'grade_id': self.grade_combo.currentData(),
            'section_id': self.section_combo.currentData(),
            'parent_id': parent_id,
            'birth_date': birth_date_str,
            'birth_village': self.village_input.text().strip() or None,
            'birth_district': self.district_input.text().strip() or None,
            'birth_governorate': (
                self.governorate_input.text().strip() or None
            ),
        }

        try:
            if StudentFactory.is_remote():
                service = StudentFactory.get_service()
                if self.student and getattr(self.student, 'id', None):
                    service.update(self.student.id, payload)
                else:
                    service.create(payload)
            else:
                self._save_local(payload)

            self.accept()

        except Exception as e:
            ErrorDialog(
                "خطأ", f"فشل حفظ البيانات: {str(e)}", self
            ).exec()

    def _save_local(self, payload: dict):
        """حفظ في Local DB (legacy)."""
        from app.database.session import session_scope
        from app.database.models import Student
        from app.services.audit_service import AuditService
        from sqlalchemy import select

        with session_scope() as session:
            if self.student and getattr(self.student, 'id', None):
                student = session.get(Student, self.student.id)
                if not student:
                    raise Exception("الطالب غير موجود")
            else:
                existing = session.execute(
                    select(Student).where(
                        Student.student_number
                        == payload['student_number']
                    )
                ).scalar_one_or_none()
                if existing:
                    raise Exception("رقم الطالب موجود مسبقاً")
                student = Student()
                session.add(student)

            for key, value in payload.items():
                if value is None:
                    setattr(student, key, None)
                elif key == 'birth_date':
                    setattr(
                        student, key,
                        date.fromisoformat(value) if value else None
                    )
                else:
                    setattr(student, key, value)

            session.flush()