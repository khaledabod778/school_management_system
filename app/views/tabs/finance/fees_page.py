"""
واجهة رسوم الطلاب والأقساط - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Dict, Optional
import qtawesome as qta
from datetime import date, datetime
from decimal import Decimal

from app.database.session import session_scope
from app.database.models import (
    Student, Grade, Section, FeeType, GradeFeeStructure,
    StudentFee, FeeInstallment, AcademicYear
)
from app.services.finance_factory import FinanceFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    PageHeader, Card, QDateEditEN, QDoubleSpinBoxEN, QSpinBoxEN, 
    SearchBox, ModernTable, Badge, GradientButton, KPICard
)
from app.views.widgets.dialogs import (
    ConfirmationDialog, SuccessDialog, ErrorDialog
)
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload


class FeesPage(QWidget):
    """صفحة إدارة رسوم الطلاب - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ تخزين ID السنة قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        
        # ✅ تخزين ID الطالب المحدد (بدلاً من ORM object)
        self.selected_student_id: Optional[int] = None
        self.selected_student_data: Dict = {}
        
        # ✅ بيانات مؤقتة
        self.students_data: List[Dict] = []
        self.grade_fees_data: List[Dict] = []
        self.previous_debt: float = 0.0
        
        # ✅ debounce للبحث
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self.search_students)
        
        # ✅ منع إعادة الحساب أثناء التحميل
        self._is_loading_fees = False
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)

            # ✅ تحميل أولي للطلاب
        QTimer.singleShot(100, self.load_initial_students)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)

        # رأس الصفحة
        header_label = QLabel("رسوم الطلاب والأقساط")
        header_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(header_label)
        
        sub_label = QLabel("إدارة رسوم الطلاب والأقساط والديون")
        sub_label.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(sub_label)        
        
        # منطقة التمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scroll_area")
        scroll_area.setStyleSheet("""
            QScrollArea#scroll_area {
                border: none;
                background: transparent;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)
        
        # ====== بطاقة البحث ======
        search_card = Card("البحث عن طالب")
        search_card.setObjectName("styleCard")
        
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.student_search = SearchBox("ابحث بالاسم أو رقم الطالب...")
        self.student_search.textChanged.connect(self._on_search_text_changed)
        search_layout.addWidget(self.student_search, 1)
        
        search_btn = GradientButton("بحث", "fa5s.search")
        search_btn.setObjectName("primaryButton")
        search_btn.clicked.connect(self.search_students)
        search_layout.addWidget(search_btn, 1)
        
        search_card.add_widget(self._create_widget(search_layout))
        
        # قائمة نتائج البحث
        self.students_list = QListWidget()
        self.students_list.setMaximumHeight(150)
        self.students_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 5px;
                background: #F8FAFC;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #F1F5F9;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background: #E2E8F0;
            }
            QListWidget::item:selected {
                background: #1976D3;
                color: white;
            }
        """)
        self.students_list.itemClicked.connect(self.select_student)
        search_card.add_widget(self.students_list)
        
        scroll_layout.addWidget(search_card)
        
        # ====== بطاقة معلومات الطالب ======
        self.info_card = Card()
        self.info_card.setObjectName("styleCard")
        self.info_card.setVisible(False)
        
        info_layout = QHBoxLayout()
        
        self.student_avatar = QLabel()
        self.student_avatar.setFixedSize(60, 60)
        self.student_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.student_avatar.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #1976D3, stop:1 #42A5F5);
                color: white;
                border-radius: 30px;
                font-size: 24px;
                font-weight: 700;
            }
        """)
        info_layout.addWidget(self.student_avatar)
        
        info_text_layout = QVBoxLayout()
        info_text_layout.setSpacing(5)
        
        self.student_name_label = QLabel()
        self.student_name_label.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #0F172A;"
        )
        info_text_layout.addWidget(self.student_name_label)
        
        self.student_grade_label = QLabel()
        self.student_grade_label.setStyleSheet(
            "font-size: 12px; color: #64748B;"
        )
        info_text_layout.addWidget(self.student_grade_label)
        
        info_layout.addLayout(info_text_layout)
        info_layout.addStretch()
        
        self.previous_debt_label = QLabel()
        self.previous_debt_label.setStyleSheet("""
            padding: 10px 15px;
            background: #FEF2F2;
            border-radius: 8px;
            color: #DC2626;
            font-weight: 700;
            font-size: 14px;
        """)
        info_layout.addWidget(self.previous_debt_label)
        
        self.info_card.add_widget(self._create_widget(info_layout))
        scroll_layout.addWidget(self.info_card)
        
        # ====== بطاقة الرسوم ======
        self.fees_card = Card("رسوم السنة الحالية")
        self.fees_card.setObjectName("styleCard")
        self.fees_card.setVisible(False)
        
        # جدول الرسوم
        self.fees_table = QTableWidget()
        self.fees_table.setColumnCount(4)
        self.fees_table.setHorizontalHeaderLabels([
            "اختيار", "نوع الرسوم", "المبلغ", "إلزامي"
        ])
        self.fees_table.setColumnWidth(0, 50)
        self.fees_table.setColumnWidth(1, 200)
        self.fees_table.setColumnWidth(2, 200)
        self.fees_table.setColumnWidth(3, 100)
        self.fees_table.horizontalHeader().setStretchLastSection(True)
        self.fees_card.add_widget(self.fees_table)
        
        # ملخص الرسوم
        summary_layout = QGridLayout()
        summary_layout.setSpacing(10)
        
        summary_layout.addWidget(self._create_summary_label("مجموع الرسوم:"), 0, 0)
        self.total_fees_label = self._create_summary_value("0.00")
        summary_layout.addWidget(self.total_fees_label, 0, 1)
        
        summary_layout.addWidget(self._create_summary_label("الخصم:"), 1, 0)
        self.discount_input = QDoubleSpinBoxEN()
        self.discount_input.setStyleSheet("""
            QDoubleSpinBox {
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px;
                font-weight: 700;
                color: #F59E0B;
                background: #FFFBEB;
            }
            QDoubleSpinBox:focus {
                border-color: #F59E0B;
            }
        """)
        self.discount_input.valueChanged.connect(self.update_net_total)
        summary_layout.addWidget(self.discount_input, 1, 1)
        
        summary_layout.addWidget(self._create_summary_label("صافي الرسوم:"), 2, 0)
        self.net_fees_label = self._create_summary_value("0.00")
        summary_layout.addWidget(self.net_fees_label, 2, 1)
        
        summary_layout.addWidget(self._create_summary_label("إجمالي المستحق:"), 3, 0)
        self.total_required_label = self._create_summary_value(
            "0.00", "#EF4444", "#FEF2F2"
        )
        summary_layout.addWidget(self.total_required_label, 3, 1)
        
        self.fees_card.add_widget(self._create_widget_grid(summary_layout))
        
        # عدد الأقساط
        installments_layout = QHBoxLayout()
        installments_layout.addWidget(self._create_summary_label("عدد الأقساط:"))
        
        self.installments_count = QSpinBoxEN(1, 12)
        self.installments_count.setValue(3)
        self.installments_count.setStyleSheet("""
            QSpinBox {
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px;
                font-weight: 700;
                min-width: 80px;
            }
            QSpinBox:focus {
                border-color: #1976D3;
            }
        """)
        self.installments_count.valueChanged.connect(self.generate_installments)
        installments_layout.addWidget(self.installments_count)
        installments_layout.addStretch()
        
        self.fees_card.add_widget(self._create_widget(installments_layout))
        
        # جدول الأقساط
        installments_title = QLabel("تفاصيل الأقساط")
        installments_title.setStyleSheet("""
            font-size: 14px;
            font-weight: 700;
            color: #0F172A;
            padding-top: 10px;
            border-top: 2px solid #F1F5F9;
        """)
        self.fees_card.add_widget(installments_title)
        
        self.installments_table = QTableWidget()
        self.installments_table.setColumnCount(4)
        self.installments_table.setHorizontalHeaderLabels([
            "رقم القسط", "اسم القسط", "المبلغ", "تاريخ الاستحقاق"
        ])
        self.installments_table.setColumnWidth(0, 80)
        self.installments_table.setColumnWidth(1, 200)
        self.installments_table.setColumnWidth(2, 150)
        self.installments_table.horizontalHeader().setStretchLastSection(True)
        self.fees_card.add_widget(self.installments_table)
        
        # أزرار الحفظ
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        clear_btn = GradientButton("مسح", "fa5s.eraser")
        clear_btn.set_gradient("#64748B", "#475569")
        clear_btn.clicked.connect(self.clear_form)
        buttons_layout.addWidget(clear_btn)
        
        save_btn = GradientButton("حفظ الرسوم", "fa5s.save")
        save_btn.clicked.connect(self.save_fees)
        buttons_layout.addWidget(save_btn)
        
        self.fees_card.add_widget(self._create_widget(buttons_layout))
        
        scroll_layout.addWidget(self.fees_card)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
    
    # ============================================================
    # ✅ دوال مساعدة
    # ============================================================
    
    def _create_widget(self, layout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    def _create_widget_grid(self, layout: QGridLayout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    def _create_summary_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("""
            color: #475569;
            font-weight: 600;
            font-size: 13px;
            padding: 8px;
        """)
        return label
    
    def _create_summary_value(self, text: str, color: str = "#0F172A", 
                               bg: str = "#F8FAFC") -> QLabel:
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"""
            color: {color};
            font-weight: 700;
            font-size: 14px;
            padding: 8px;
            background: {bg};
            border-radius: 8px;
            border: 1px solid #E2E8F0;
        """)
        return label
    
    # ============================================================
    # ✅ البحث عن الطلاب (Async)
    # ============================================================
    
    def _on_search_text_changed(self):
        """عند تغيير نص البحث - debounce."""
        self._search_timer.stop()
        self._search_timer.start()

    def load_initial_students(self):
        """تحميل أولي للطلاب."""
        self._load_students(search_text="")

    def search_students(self):
        """البحث عن الطلاب (يُستدعى بعد debounce)."""
        search_text = self.student_search.text().strip()
        self._load_students(search_text=search_text)
    
    def _load_students(self, search_text: str):
        """البحث عن الطلاب - Local أو Remote."""

        if not search_text:
            self.loading_overlay.show_loading("جاري تحميل الطلاب...")

        academic_year_id = self.academic_year_id

        def _fetch_data():
            """جلب الطلاب (في الخلفية)."""
            # ✅ Remote Mode
            if FinanceFactory.is_remote():
                from app.services.student_factory import StudentFactory
                service = StudentFactory.get_service()
                # نستخدم lookup مع فلتر academic_year_id
                students = service.list_students(
                    academic_year_id=academic_year_id,
                    search=search_text or None,
                    status='مستمر',
                )
                # نُحدّد إلى 20
                return students[:20]

            # ✅ Local Mode (السلوك القديم)
            from app.database.session import session_scope
            from app.database.models import Student
            from sqlalchemy import select
            with session_scope() as session:
                query = select(Student).where(
                    Student.academic_year_id == academic_year_id,
                    Student.status == 'مستمر',
                )

                if search_text:
                    query = query.where(
                        (Student.full_name.ilike(f"%{search_text}%")) |
                        (Student.student_number.ilike(f"%{search_text}%"))
                    )

                query = query.limit(20)
                students = session.execute(query).scalars().all()

                return [
                    {
                        'id': s.id,
                        'full_name': s.full_name or '',
                        'student_number': s.student_number or '',
                    }
                    for s in students
                ]

        def _on_result(data):
            try:
                self.students_data = data
                self.students_list.clear()

                for student in data:
                    item = QListWidgetItem(
                        f"{student['full_name']} - {student['student_number']}"
                    )
                    item.setData(Qt.ItemDataRole.UserRole, student['id'])
                    self.students_list.addItem(item)
            except Exception as e:
                print(f"خطأ: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            print(f"فشل البحث: {error_msg}")

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
        
    # ============================================================
    # ✅ اختيار طالب (Async)
    # ============================================================
    
    def select_student(self, item: QListWidgetItem):
        """اختيار طالب - تحميل جميع بياناته في الخلفية."""
        student_id = item.data(Qt.ItemDataRole.UserRole)
        
        # ✅ البحث في القائمة المحفوظة
        student = next(
            (s for s in self.students_data if s['id'] == student_id),
            None
        )
        if not student:
            return
        
        self.selected_student_id = student_id
        self.selected_student_data = student
        
        # ✅ تحميل جميع البيانات في طلب واحد
        self._load_student_full_data(student_id)
    
    def _load_student_full_data(self, student_id: int):
        """تحميل بيانات الطالب الكاملة (رسوم + أقساط)."""
        self.loading_overlay.show_loading("جاري تحميل البيانات...")
        academic_year_id = self.academic_year_id

        def _fetch():
            if FinanceFactory.is_remote():
                service = FinanceFactory.get_service()
                remote = service.get_student_fees_data(
                    student_id, academic_year_id
                )
                return {
                    'student': remote['student'],  # ← يحوي كل الحقول الآن
                    'grade_fees': remote['grade_fees'],
                    'existing_fee': remote['existing_fee'],
                }
            else:
                # الكود القديم
                from app.database.session import session_scope
                from app.database.models import (
                    Student, GradeFeeStructure, FeeType, StudentFee,
                )
                from sqlalchemy import select
                from sqlalchemy.orm import joinedload
                with session_scope() as session:
                    student = session.execute(
                        select(Student)
                        .options(
                            joinedload(Student.grade),
                            joinedload(Student.section),
                        )
                        .where(Student.id == student_id)
                    ).unique().scalar_one_or_none()
                    if not student:
                        return None

                    grade_fees_q = session.execute(
                        select(GradeFeeStructure, FeeType)
                        .join(FeeType,
                              GradeFeeStructure.fee_type_id == FeeType.id)
                        .where(
                            GradeFeeStructure.grade_id == student.grade_id,
                            GradeFeeStructure.academic_year_id == academic_year_id,
                        )
                    ).all()

                    grade_fees = [
                        {
                            'id': fs.id,
                            'fee_type_id': ft.id,
                            'fee_type_name': ft.fee_name or '',
                            'amount': float(fs.amount or 0),
                        }
                        for fs, ft in grade_fees_q
                    ]

                    existing = session.execute(
                        select(StudentFee)
                        .options(joinedload(StudentFee.installments))
                        .where(
                            StudentFee.student_id == student_id,
                            StudentFee.academic_year_id == academic_year_id,
                        )
                    ).unique().scalar_one_or_none()

                    fee_data = None
                    if existing:
                        fee_data = {
                            'id': existing.id,
                            'previous_debt': float(existing.previous_debt or 0),
                            'discount_amount': float(existing.discount_amount or 0),
                            'installments': [
                                {
                                    'id': inst.id,
                                    'installment_type': inst.installment_type or 'regular',
                                    'installment_number': inst.installment_number or 0,
                                    'installment_name': inst.installment_name or '',
                                    'amount': float(inst.amount or 0),
                                    'due_date': inst.due_date,
                                }
                                for inst in (existing.installments or [])
                            ],
                        }

                    return {
                        'student': {
                            'id': student.id,
                            'full_name': student.full_name or '',
                            'student_number': student.student_number or '',
                            'grade_id': student.grade_id,
                            'grade_name': student.grade.grade_name if student.grade else '',
                            'section_name': student.section.section_name if student.section else '',
                        },
                        'grade_fees': grade_fees,
                        'existing_fee': fee_data,
                    }

        # نفس _on_result و _on_error كما قبل
        def _ok(data):
            try:
                if not data:
                    ErrorDialog("خطأ", "الطالب غير موجود", self).exec()
                    return
                self.selected_student_data = data['student']
                self.grade_fees_data = data['grade_fees']
                self.previous_debt = (
                    data['existing_fee']['previous_debt']
                    if data['existing_fee'] else 0.0
                )
                self._display_student_info(data['student'])
                self._display_grade_fees(data['grade_fees'])
                self.previous_debt_label.setText(
                    f"رصيد مرحل: {self.previous_debt:,.2f} ر.ي"
                )
                self.info_card.setVisible(True)
                self.fees_card.setVisible(True)
                if data['existing_fee']:
                    self.discount_input.blockSignals(True)
                    self.discount_input.setValue(
                        data['existing_fee']['discount_amount']
                    )
                    self.discount_input.blockSignals(False)
                    # ✅ دعم due_date من string
                    insts = data['existing_fee']['installments']
                    for i in insts:
                        dd = i.get('due_date')
                        if isinstance(dd, str):
                            try:
                                from datetime import date as _d
                                i['due_date'] = _d.fromisoformat(dd)
                            except Exception:
                                i['due_date'] = date.today()
                    self._load_existing_installments(insts)
                else:
                    self.discount_input.setValue(0)
                    self.installments_count.setValue(3)
                    self.update_total_fees()
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            ErrorDialog("خطأ", f"فشل: {m}", self).exec()

        run_async(_fetch, on_result=_ok, on_error=_err)
        
    # ============================================================
    # ✅ عرض البيانات
    # ============================================================
    
    def _display_student_info(self, student: Dict):
        """عرض معلومات الطالب."""
        # الصورة الرمزية
        initials = student['full_name'].split()
        avatar_text = initials[0][0] if initials else "؟"
        if len(initials) > 1:
            avatar_text += initials[-1][0]
        self.student_avatar.setText(avatar_text)
        
        # الاسم
        self.student_name_label.setText(student['full_name'])
        
        # الصف والشعبة
        grade_name = student['grade_name'] or "غير محدد"
        section_name = student['section_name']
        if section_name:
            self.student_grade_label.setText(
                f"{grade_name} - شعبة {section_name}"
            )
        else:
            self.student_grade_label.setText(grade_name)
    
    def _display_grade_fees(self, grade_fees: List[Dict]):
        """عرض رسوم الصف."""
        # ✅ منع إعادة الحساب أثناء التحميل
        self._is_loading_fees = True
        
        self.fees_table.setRowCount(len(grade_fees))
        
        for row, fee in enumerate(grade_fees):
            # مربع اختيار
            checkbox_widget = QWidget()
            checkbox_widget.setStyleSheet("background: transparent;")
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.update_total_fees)
            checkbox.setStyleSheet("""
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid #CBD5E1;
                    border-radius: 4px;
                    background: white;
                }
                QCheckBox::indicator:checked {
                    background: #1976D3;
                    border-color: #1976D3;
                }
            """)
            checkbox_layout.addWidget(checkbox)
            
            self.fees_table.setCellWidget(row, 0, checkbox_widget)
            self.fees_table.setItem(
                row, 1, QTableWidgetItem(fee['fee_type_name'])
            )
            self.fees_table.setItem(
                row, 2, QTableWidgetItem(f"{fee['amount']:,.2f}")
            )
            
            # إلزامي
            is_required = fee['fee_type_name'] in ['رسوم دراسية', 'رسوم تسجيل']
            required_item = QTableWidgetItem("نعم" if is_required else "اختياري")
            required_item.setForeground(
                QColor('#10B981') if is_required else QColor('#64748B')
            )
            self.fees_table.setItem(row, 3, required_item)
            self.fees_table.setRowHeight(row, 35)
        
        # ضبط ارتفاع الجدول
        total_height = (
            self.fees_table.horizontalHeader().height() + 
            (len(grade_fees) * 35) + 5
        )
        self.fees_table.setMinimumHeight(total_height)
        
        self._is_loading_fees = False
        
        # تحديث المجموع
        self.update_total_fees()
    
    # ============================================================
    # ✅ حسابات الرسوم
    # ============================================================
    
    def update_total_fees(self):
        """تحديث مجموع الرسوم."""
        if self._is_loading_fees:
            return
        
        total = 0
        for row in range(self.fees_table.rowCount()):
            checkbox_widget = self.fees_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    amount_text = self.fees_table.item(row, 2).text().replace(',', '')
                    total += float(amount_text)
        
        self.total_fees_label.setText(f"{total:,.2f}")
        self.update_net_total()
    
    def update_net_total(self):
        """تحديث صافي الرسوم."""
        total = float(self.total_fees_label.text().replace(',', ''))
        discount = self.discount_input.value()
        net = total - discount
        
        self.net_fees_label.setText(f"{net:,.2f}")
        
        total_required = net + self.previous_debt
        self.total_required_label.setText(f"{total_required:,.2f}")
        
        # توليد الأقساط
        self.generate_installments()
    
    def generate_installments(self):
        """توليد الأقساط."""
        count = self.installments_count.value()
        net_total = float(self.net_fees_label.text().replace(',', ''))
        
        if net_total <= 0 or count <= 0:
            self.installments_table.setRowCount(0)
            return
        
        has_previous_debt = self.previous_debt > 0
        
        total_rows = count + (1 if has_previous_debt else 0)
        self.installments_table.setRowCount(total_rows)
        
        current_row = 0
        
        # قسط الرصيد المرحل
        if has_previous_debt:
            self.installments_table.setItem(
                current_row, 0, QTableWidgetItem("0")
            )
            self.installments_table.setItem(
                current_row, 1, QTableWidgetItem("قسط رصيد سابقة مرحّل")
            )
            self.installments_table.setItem(
                current_row, 2, 
                QTableWidgetItem(f"{self.previous_debt:,.2f}")
            )
            
            due_date = QDateEditEN()
            due_date.setStyleSheet("""
                QDateEdit {
                    border: 2px solid #EF4444;
                    border-radius: 6px;
                    padding: 5px;
                    color: #DC2626;
                    font-weight: 600;
                    background: #FEF2F2;
                }
            """)
            self.installments_table.setCellWidget(current_row, 3, due_date)
            self.installments_table.setRowHeight(current_row, 35)
            current_row += 1
        
        # أقساط السنة الحالية
        installment_amount = net_total / count
        
        for i in range(count):
            self.installments_table.setItem(
                current_row, 0, QTableWidgetItem(str(i + 1))
            )
            self.installments_table.setItem(
                current_row, 1, QTableWidgetItem(f"قسط {i + 1}")
            )
            self.installments_table.setItem(
                current_row, 2, 
                QTableWidgetItem(f"{installment_amount:,.2f}")
            )
            
            due_date = QDateEditEN(QDate.currentDate().addMonths(i + 1))
            due_date.setStyleSheet("""
                QDateEdit {
                    border: 1px solid #E2E8F0;
                    border-radius: 6px;
                    padding: 5px;
                }
                QDateEdit:focus {
                    border-color: #1976D3;
                }
            """)
            self.installments_table.setCellWidget(current_row, 3, due_date)
            
            current_row += 1
        
        # ضبط ارتفاع الجدول
        total_height = (
            self.installments_table.horizontalHeader().height() + 
            (self.installments_table.rowCount() * 40) + 5
        )
        self.installments_table.setMinimumHeight(total_height)
    
    def _load_existing_installments(self, installments: List[Dict]):
        """تحميل الأقساط الموجودة (من dict)."""
        self.installments_table.setRowCount(len(installments))

        def _set_date(input_widget, value):
            if not value:
                return
            if isinstance(value, str):
                try:
                    value = date.fromisoformat(value)
                except Exception:
                    return
            input_widget.setDate(QDate(value.year, value.month, value.day))     

        for row, inst in enumerate(installments):
            self.installments_table.setItem(
                row, 0, QTableWidgetItem(str(inst['installment_number']))
            )
            self.installments_table.setItem(
                row, 1, QTableWidgetItem(inst['installment_name'])
            )
            self.installments_table.setItem(
                row, 2, QTableWidgetItem(f"{inst['amount']:,.2f}")
            )
            
            due_date = QDateEditEN()
            _set_date(due_date, inst.get('due_date'))

            self.installments_table.setCellWidget(row, 3, due_date)
            self.installments_table.setRowHeight(row, 35)
    
    # ============================================================
    # ✅ مسح النموذج
    # ============================================================
    
    def clear_form(self):
        """مسح النموذج."""
        self.selected_student_id = None
        self.selected_student_data = {}
        self.student_search.clear()
        self.students_list.clear()
        self.info_card.setVisible(False)
        self.fees_card.setVisible(False)
        self.previous_debt_label.setText("")
        self.discount_input.setValue(0)
        self.installments_count.setValue(3)
        self.installments_table.setRowCount(0)
        self.previous_debt = 0.0
    
    # ============================================================
    # ✅ حفظ الرسوم
    # ============================================================
    
    def save_fees(self):
        """حفظ الرسوم."""
        if (self.permission_service
                and not self.permission_service.can_add("رسوم الطلاب")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        if not self.selected_student_id:
            ErrorDialog("تنبيه", "اختر طالباً", self).exec()
            return

        # اجمع الأقساط
        total_fees = float(self.total_fees_label.text().replace(',', ''))
        discount = self.discount_input.value()
        net_total = total_fees - discount + self.previous_debt

        installments = []
        for row in range(self.installments_table.rowCount()):
            num_item = self.installments_table.item(row, 0)
            name_item = self.installments_table.item(row, 1)
            amount_item = self.installments_table.item(row, 2)
            if not (num_item and name_item and amount_item):
                continue
            dd = self.installments_table.cellWidget(row, 3)
            due_date = (
                dd.date().toPython()
                if isinstance(dd, QDateEdit) else date.today()
            )
            installments.append({
                'type': 'previous_debt' if num_item.text() == '0' else 'regular',
                'number': int(num_item.text()),
                'name': name_item.text(),
                'amount': float(amount_item.text().replace(',', '')),
                'due_date': due_date.isoformat(),
            })

        payload = {
            'total_fees': total_fees,
            'discount_amount': discount,
            'previous_debt': self.previous_debt,
            'net_total': net_total,
            'installments': installments,
        }

        def _do():
            if FinanceFactory.is_remote():
                FinanceFactory.get_service().save_student_fees(
                    self.selected_student_id,
                    self.academic_year_id,
                    payload,
                )
            else:
                self._save_local(payload)

        try:
            _do()
            SuccessDialog("نجاح", "تم الحفظ", self).exec()
            self._load_student_full_data(self.selected_student_id)
        except Exception as e:
            ErrorDialog("خطأ", f"فشل: {e}", self).exec()

    def _save_local(self, payload):
        from app.database.session import session_scope
        from app.database.models import StudentFee, FeeInstallment
        from sqlalchemy import select
        from datetime import date as _date
        sid = self.selected_student_id
        ayid = self.academic_year_id
        with session_scope() as session:
            existing = session.execute(
                select(StudentFee).where(
                    StudentFee.student_id == sid,
                    StudentFee.academic_year_id == ayid,
                )
            ).scalar_one_or_none()
            if existing:
                sf = existing
                session.query(FeeInstallment).filter_by(
                    student_fee_id=sf.id
                ).delete()
                session.flush()
            else:
                sf = StudentFee(
                    student_id=sid, academic_year_id=ayid
                )
                session.add(sf)

            sf.current_year_fees = Decimal(str(payload['total_fees']))
            sf.previous_debt = Decimal(str(payload['previous_debt']))
            sf.discount_amount = Decimal(str(payload['discount_amount']))
            sf.net_total_required = Decimal(str(payload['net_total']))
            session.flush()

            for inst in payload['installments']:
                session.add(FeeInstallment(
                    student_fee_id=sf.id,
                    installment_type=inst['type'],
                    installment_number=inst['number'],
                    installment_name=inst['name'],
                    amount=Decimal(str(inst['amount'])),
                    due_date=_date.fromisoformat(inst['due_date']),
                ))

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
        self.clear_form()
        self.load_initial_students()