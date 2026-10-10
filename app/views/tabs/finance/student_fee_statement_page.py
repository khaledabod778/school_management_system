"""
واجهة كشف حساب الطالب التفصيلي - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta
from datetime import date
from decimal import Decimal

from app.database.session import session_scope
from app.database.models import (
    Student, StudentFee, FeeInstallment, Receipt, AcademicYear,
    Grade, Section, Parent
)
from app.services.finance_factory import FinanceFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    GradientButton, QLineEditPlus, SearchBox
)
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload


class StudentFeeStatementPage(QWidget):
    """صفحة كشف حساب الطالب التفصيلي - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ تخزين ID السنة قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        
        # ✅ تخزين بيانات الطالب (dicts بدلاً من ORM)
        self.selected_student_id: Optional[int] = None
        self.selected_student_data: Dict = {}
        
        # ✅ بيانات مؤقتة
        self.students_data: List[Dict] = []
        
        # ✅ debounce للبحث
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self.search_students)
        
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
        title = QLabel("كشف حساب الطالب التفصيلي")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #0F172A;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("عرض الأقساط والمدفوعات والمبالغ المتبقية للطالب")
        subtitle.setStyleSheet("font-size: 13px; color: #64748B;")
        main_layout.addWidget(subtitle)
        
        # بطاقة البحث عن طالب
        search_card = QFrame()
        search_card.setObjectName("filterCard")
        search_card.setStyleSheet("""
            QFrame#filterCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        search_layout = QHBoxLayout(search_card)
        search_layout.setSpacing(10)
        
        self.student_search = SearchBox("بحث عن طالب بالاسم أو الرقم...")
        self.student_search.setClearButtonEnabled(True)
        self.student_search.textChanged.connect(self._on_search_text_changed)
        search_layout.addWidget(self.student_search)
        
        search_btn = GradientButton("بحث", "fa5s.search")
        search_btn.clicked.connect(self.search_students)
        search_layout.addWidget(search_btn)
        
        main_layout.addWidget(search_card)
        
        # منطقة التمرير للكشف
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(15)
        
        # قائمة الطلاب
        self.students_list = QListWidget()
        self.students_list.setMaximumHeight(150)
        self.students_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #1976D3;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px 8px;
                border-bottom: 1px solid #F1F5F9;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background: #F1F5F9;
            }
            QListWidget::item:selected {
                background: #EEF2FF;
                color: #0D47A1;
                font-weight: 600;
            }
        """)
        self.students_list.itemClicked.connect(self.select_student)
        scroll_layout.addWidget(self.students_list)

        # بطاقة معلومات الطالب
        self.info_card = QFrame()
        self.info_card.setObjectName("filterCard")
        self.info_card.setStyleSheet("""
            QLabel {
                border: 1px solid #1976D3;
                color: #0F172A; 
                font-size: 12px;
                border-radius: 6px;
                background: #EEF2FF;
                padding: 10px 15px;
            }
        """)
        self.info_card.setVisible(False)
        self._setup_info_card()
        scroll_layout.addWidget(self.info_card)
        
        # بطاقة ملخص الرسوم
        self.summary_card = QFrame()
        self.summary_card.setObjectName("filterCard")
        self.summary_card.setVisible(False)
        self._setup_summary_card()
        scroll_layout.addWidget(self.summary_card)
        
        # بطاقة الأقساط
        self.installments_card = QFrame()
        self.installments_card.setObjectName("tableCard")
        self.installments_card.setVisible(False)
        self._setup_installments_card()
        scroll_layout.addWidget(self.installments_card)
        
        # بطاقة سندات القبض
        self.receipts_card = QFrame()
        self.receipts_card.setObjectName("tableCard")
        self.receipts_card.setVisible(False)
        self._setup_receipts_card()
        scroll_layout.addWidget(self.receipts_card)
        
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # زر الطباعة
        self.print_btn = GradientButton("طباعة كشف الحساب", "fa5s.print")
        self.print_btn.setObjectName("successButton")
        self.print_btn.clicked.connect(self.print_statement)
        self.print_btn.setEnabled(False)  # ✅ معطّل حتى يتم اختيار طالب
        main_layout.addWidget(self.print_btn)
    
    def _setup_info_card(self):
        """إعداد بطاقة معلومات الطالب."""
        layout = QVBoxLayout(self.info_card)
        layout.setSpacing(8)
        
        self.student_name_label = QLabel()
        self.student_name_label.setStyleSheet(
            "font-size: 16px; font-weight: 700; border: none; "
            "padding-top: 0px; background: none;"
        )
        self.student_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.student_name_label)
        
        info_row = QHBoxLayout()
        info_row.addStretch()

        self.student_number_label = QLabel()
        info_row.addWidget(self.student_number_label)
        
        self.student_grade_label = QLabel()
        info_row.addWidget(self.student_grade_label)
        
        self.student_parent_label = QLabel()
        info_row.addWidget(self.student_parent_label)
        
        info_row.addStretch()
        layout.addLayout(info_row)
    
    def _setup_summary_card(self):
        """إعداد بطاقة ملخص الرسوم."""
        layout = QVBoxLayout(self.summary_card)
        layout.setSpacing(20)
        
        title = QLabel("ملخص الحساب")
        title.setObjectName("cardTitle")
        layout.addWidget(title)
        
        summary_grid = QGridLayout()
        summary_grid.setSpacing(1)
        
        summary_grid.addWidget(self._create_label("إجمالي رسوم السنة"), 0, 0)
        self.total_fees_label = self._create_value_label("0.00", "#0F172A")
        summary_grid.addWidget(self.total_fees_label, 1, 0)
        
        summary_grid.addWidget(self._create_label("الرصيد المرحل"), 0, 1)
        self.previous_debt_label = self._create_value_label("0.00", "#EF4444")
        summary_grid.addWidget(self.previous_debt_label, 1, 1)
        
        summary_grid.addWidget(self._create_label("الخصم"), 0, 2)
        self.discount_label = self._create_value_label("0.00", "#F59E0B")
        summary_grid.addWidget(self.discount_label, 1, 2)
        
        summary_grid.addWidget(self._create_label("إجمالي المستحق"), 0, 3)
        self.total_required_label = self._create_value_label(
            "0.00", "#1976D3", "#EEF2FF"
        )
        summary_grid.addWidget(self.total_required_label, 1, 3)
        
        summary_grid.addWidget(self._create_label("إجمالي المدفوع"), 0, 4)
        self.total_paid_label = self._create_value_label(
            "0.00", "#10B981", "#ECFDF5"
        )
        summary_grid.addWidget(self.total_paid_label, 1, 4)
        
        summary_grid.addWidget(self._create_label("المبلغ المتبقي"), 0, 5)
        self.remaining_label = self._create_value_label(
            "0.00", "#EF4444", "#FEF2F2"
        )
        summary_grid.addWidget(self.remaining_label, 1, 5)
        
        layout.addLayout(summary_grid)
    
    def _setup_installments_card(self):
        """إعداد بطاقة الأقساط."""
        layout = QVBoxLayout(self.installments_card)
        layout.setSpacing(10)
        
        title = QLabel("الأقساط المستحقة")
        title.setObjectName("cardTitle")
        layout.addWidget(title)
        
        self.installments_table = QTableWidget()
        self.installments_table.setColumnCount(7)
        self.installments_table.setHorizontalHeaderLabels([
            "رقم القسط", "اسم القسط", "المبلغ", "المدفوع", "المتبقي",
            "تاريخ الاستحقاق", "الحالة"
        ])
        self.installments_table.setColumnWidth(0, 80)
        self.installments_table.setColumnWidth(1, 180)
        self.installments_table.setColumnWidth(2, 100)
        self.installments_table.setColumnWidth(3, 100)
        self.installments_table.setColumnWidth(4, 100)
        self.installments_table.setColumnWidth(5, 120)
        self.installments_table.setColumnWidth(6, 80)
        self.installments_table.horizontalHeader().setStretchLastSection(True)
        self.installments_table.setAlternatingRowColors(True)
        self.installments_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.installments_table.verticalHeader().setVisible(False)
        layout.addWidget(self.installments_table)
    
    def _setup_receipts_card(self):
        """إعداد بطاقة سندات القبض."""
        layout = QVBoxLayout(self.receipts_card)
        layout.setSpacing(10)
        
        title = QLabel("سندات القبض")
        title.setObjectName("cardTitle")
        layout.addWidget(title)
        
        self.receipts_table = QTableWidget()
        self.receipts_table.setColumnCount(7)
        self.receipts_table.setHorizontalHeaderLabels([
            "رقم السند", "التاريخ", "المبلغ", "طريقة الدفع",
            "القسط", "الحالة", "ملاحظات"
        ])
        self.receipts_table.setColumnWidth(0, 110)
        self.receipts_table.setColumnWidth(1, 130)
        self.receipts_table.setColumnWidth(2, 100)
        self.receipts_table.setColumnWidth(3, 100)
        self.receipts_table.setColumnWidth(4, 150)
        self.receipts_table.setColumnWidth(5, 70)
        self.receipts_table.setColumnWidth(6, 150)
        self.receipts_table.horizontalHeader().setStretchLastSection(True)
        self.receipts_table.setAlternatingRowColors(True)
        self.receipts_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.receipts_table.verticalHeader().setVisible(False)
        layout.addWidget(self.receipts_table)
    
    def _create_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            color: #475569; 
            font-weight: 600; 
            font-size: 12px;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 10px;
            margin: 0px 3px;
        """)
        return label
    
    def _create_value_label(self, text: str, color: str, 
                             bg: str = "transparent") -> QLabel:
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"""
            color: {color};
            font-weight: 700;
            font-size: 14px;
            padding: 8px;
            border: 1px solid #E2E8F0;
            background: {bg};
            margin: 0px 3px;
            border-radius: 6px;
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
        """تحميل قائمة الطلاب - Local أو Remote."""
        self.loading_overlay.show_loading("جاري البحث عن الطلاب...")

        academic_year_id = self.academic_year_id

        def _fetch_data():
            """جلب الطلاب (في الخلفية)."""
            # ✅ Remote Mode
            if FinanceFactory.is_remote():
                from app.services.student_factory import StudentFactory
                service = StudentFactory.get_service()
                students = service.list_students(
                    academic_year_id=academic_year_id,
                    search=search_text or None,
                )
                # نُحدّد إلى 30
                return students[:30]

            # ✅ Local Mode (السلوك القديم)
            from app.database.session import session_scope
            from app.database.models import Student
            from sqlalchemy import select
            with session_scope() as session:
                query = select(Student).where(
                    Student.academic_year_id == academic_year_id
                )

                if search_text:
                    query = query.where(
                        (Student.full_name.ilike(f"%{search_text}%")) |
                        (Student.student_number.ilike(f"%{search_text}%"))
                    )

                query = query.order_by(Student.full_name).limit(30)
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
    # ✅ اختيار طالب - تحميل كشف الحساب (Async)
    # ============================================================
    
    def select_student(self, item: QListWidgetItem):
        """اختيار طالب - تحميل كشف حسابه الكامل."""
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
        
        # ✅ تفعيل زر الطباعة
        self.print_btn.setEnabled(True)
        
        # ✅ تحميل كشف الحساب الكامل في طلب واحد
        self._load_student_statement(student_id)
    
    def _load_student_statement(self, student_id: int):
        self.loading_overlay.show_loading("جاري تحميل كشف الحساب...")
        ayid = self.academic_year_id

        def _fetch():
            if FinanceFactory.is_remote():
                return FinanceFactory.get_service().get_statement(
                    student_id, ayid
                )
            else:
                # نفس الكود القديم بالضبط
                from app.database.session import session_scope
                from app.database.models import (
                    Student, StudentFee, FeeInstallment, Receipt,
                )
                from sqlalchemy import select
                from sqlalchemy.orm import joinedload
                with session_scope() as session:
                    student = session.execute(
                        select(Student).options(
                            joinedload(Student.grade),
                            joinedload(Student.section),
                            joinedload(Student.parent),
                        ).where(Student.id == student_id)
                    ).unique().scalar_one_or_none()
                    if not student:
                        return None

                    fee = session.execute(
                        select(StudentFee).where(
                            StudentFee.student_id == student_id,
                            StudentFee.academic_year_id == ayid,
                        )
                    ).scalar_one_or_none()

                    fee_data = None
                    installments = []
                    total_paid = 0.0

                    if fee:
                        fee_data = {
                            'id': fee.id,
                            'current_year_fees': float(fee.current_year_fees or 0),
                            'previous_debt': float(fee.previous_debt or 0),
                            'discount_amount': float(fee.discount_amount or 0),
                            'net_total_required': float(fee.net_total_required or 0),
                        }
                        insts = session.execute(
                            select(FeeInstallment)
                            .where(FeeInstallment.student_fee_id == fee.id)
                            .order_by(FeeInstallment.installment_number)
                        ).scalars().all()
                        for i in insts:
                            paid = float(i.paid_amount or 0)
                            amount = float(i.amount or 0)
                            total_paid += paid
                            due = i.due_date
                            if i.is_paid:
                                status = 'مسدد'
                            elif due and due < date.today():
                                status = 'متأخر'
                            else:
                                status = 'متبقي'
                            installments.append({
                                'number': i.installment_number or 0,
                                'name': i.installment_name or '',
                                'amount': amount,
                                'paid_amount': paid,
                                'remaining': amount - paid,
                                'due_date_str': due.strftime("%Y/%m/%d") if due else '',
                                'is_paid': bool(i.is_paid),
                                'status': status,
                            })

                    receipts = session.execute(
                        select(Receipt).options(joinedload(Receipt.installment))
                        .where(
                            Receipt.student_id == student_id,
                            Receipt.status == 'نشط',
                        )
                        .order_by(Receipt.payment_date.desc())
                    ).unique().scalars().all()

                    return {
                        'student': {
                            'id': student.id,
                            'full_name': student.full_name or '',
                            'student_number': student.student_number or '',
                            'grade_name': student.grade.grade_name if student.grade else '',
                            'section_name': student.section.section_name if student.section else '',
                            'parent_name': student.parent.full_name if student.parent else '',
                        },
                        'fee': fee_data,
                        'installments': installments,
                        'receipts': [
                            {
                                'receipt_number': r.receipt_number or '',
                                'payment_date_str': (
                                    r.payment_date.strftime("%Y/%m/%d %H:%M")
                                    if r.payment_date else ''
                                ),
                                'amount_paid': float(r.amount_paid or 0),
                                'payment_method': r.payment_method or '',
                                'installment_name': (
                                    r.installment.installment_name
                                    if r.installment else ''
                                ),
                                'status': r.status or '',
                                'notes': r.notes or '',
                            }
                            for r in receipts
                        ],
                        'total_paid': total_paid,
                    }

        # نفس _on_result و _on_error
        def _ok(data):
            try:
                if not data:
                    QMessageBox.critical(self, "خطأ", "الطالب غير موجود")
                    return
                self._display_statement(data)
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(self, "خطأ", f"فشل: {m}")

        run_async(_fetch, on_result=_ok, on_error=_err)
        
    # ============================================================
    # ✅ عرض كشف الحساب
    # ============================================================
    
    def _display_statement(self, data: Dict):
        """عرض كشف الحساب من البيانات المحملة."""
        # إظهار البطاقات
        self.info_card.setVisible(True)
        self.summary_card.setVisible(True)
        self.installments_card.setVisible(True)
        self.receipts_card.setVisible(True)
        
        # ============ معلومات الطالب ============
        student = data['student']
        self.student_name_label.setText(student['full_name'])
        self.student_number_label.setText(
            f"رقم الطالب: {student['student_number']}"
        )
        self.student_grade_label.setText(
            f"الصف: {student['grade_name']} - شعبة: {student['section_name']}"
        )
        self.student_parent_label.setText(
            f"ولي الأمر: {student['parent_name']}"
        )
        
        # ============ ملخص الرسوم ============
        fee = data['fee']
        
        if not fee:
            # لا توجد رسوم مسجلة
            self.total_fees_label.setText("0.00")
            self.previous_debt_label.setText("0.00")
            self.discount_label.setText("0.00")
            self.total_required_label.setText("0.00")
            self.total_paid_label.setText("0.00")
            self.remaining_label.setText("0.00")
            self.installments_table.setRowCount(0)
            self.receipts_table.setRowCount(0)
            return
        
        self.total_fees_label.setText(f"{fee['current_year_fees']:,.2f}")
        self.previous_debt_label.setText(f"{fee['previous_debt']:,.2f}")
        self.discount_label.setText(f"{fee['discount_amount']:,.2f}")
        self.total_required_label.setText(f"{fee['net_total_required']:,.2f}")
        
        # إجمالي المدفوع والمتبقي
        total_paid = data['total_paid']
        self.total_paid_label.setText(f"{total_paid:,.2f}")
        remaining_total = fee['net_total_required'] - total_paid
        self.remaining_label.setText(f"{remaining_total:,.2f}")
        
        # ============ الأقساط ============
        installments = data['installments']
        self.installments_table.setRowCount(len(installments))
        
        status_colors = {
            'مسدد': '#10B981',
            'متأخر': '#EF4444',
            'متبقي': '#F59E0B',
        }
        
        for row, inst in enumerate(installments):
            self.installments_table.setItem(
                row, 0, QTableWidgetItem(str(inst['number']))
            )
            self.installments_table.setItem(
                row, 1, QTableWidgetItem(inst['name'])
            )
            
            # المبلغ
            amount_item = QTableWidgetItem(f"{inst['amount']:,.2f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.installments_table.setItem(row, 2, amount_item)
            
            # المدفوع
            paid_item = QTableWidgetItem(f"{inst['paid_amount']:,.2f}")
            paid_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            paid_item.setForeground(QColor('#10B981'))
            self.installments_table.setItem(row, 3, paid_item)
            
            # المتبقي
            remaining_item = QTableWidgetItem(f"{inst['remaining']:,.2f}")
            remaining_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            remaining_item.setForeground(
                QColor('#EF4444') if inst['remaining'] > 0 
                else QColor('#10B981')
            )
            self.installments_table.setItem(row, 4, remaining_item)
            
            # تاريخ الاستحقاق
            self.installments_table.setItem(
                row, 5, QTableWidgetItem(inst['due_date_str'])
            )
            
            # الحالة
            status_item = QTableWidgetItem(inst['status'])
            status_item.setForeground(
                QColor(status_colors.get(inst['status'], '#64748B'))
            )
            self.installments_table.setItem(row, 6, status_item)
            
            self.installments_table.setRowHeight(row, 40)
        
        # ضبط ارتفاع الجدول
        total_height = (
            self.installments_table.horizontalHeader().height() + 
            (len(installments) * 40) + 5
        )
        self.installments_table.setMinimumHeight(total_height)
        
        # ============ سندات القبض ============
        receipts = data['receipts']
        self.receipts_table.setRowCount(len(receipts))
        
        for row, receipt in enumerate(receipts):
            self.receipts_table.setItem(
                row, 0, QTableWidgetItem(receipt['receipt_number'])
            )
            self.receipts_table.setItem(
                row, 1, QTableWidgetItem(receipt['payment_date_str'])
            )
            
            amount_item = QTableWidgetItem(f"{receipt['amount_paid']:,.2f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            amount_item.setForeground(QColor('#10B981'))
            amount_item.setFont(QFont("Cairo", 10, QFont.Weight.Bold))
            self.receipts_table.setItem(row, 2, amount_item)
            
            self.receipts_table.setItem(
                row, 3, QTableWidgetItem(receipt['payment_method'])
            )
            self.receipts_table.setItem(
                row, 4, QTableWidgetItem(receipt['installment_name'])
            )
            
            status_item = QTableWidgetItem(receipt['status'])
            status_item.setForeground(QColor('#10B981'))
            self.receipts_table.setItem(row, 5, status_item)
            
            self.receipts_table.setItem(
                row, 6, QTableWidgetItem(receipt['notes'])
            )
            self.receipts_table.setRowHeight(row, 40)
        
        # ضبط ارتفاع الجدول
        total_height2 = (
            self.receipts_table.horizontalHeader().height() + 
            (len(receipts) * 40) + 5
        )
        self.receipts_table.setMinimumHeight(total_height2)
    
    # ============================================================
    # ✅ الطباعة
    # ============================================================
    
    def print_statement(self):
        """طباعة كشف الحساب."""
        if self.permission_service and not self.permission_service.can_print("كشف حساب طالب"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للطباعة في كشف حساب طالب"
            )
            return

        if not self.selected_student_id:
            QMessageBox.warning(
                self, "تنبيه",
                "يرجى اختيار طالب أولاً"
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
        # إخفاء البطاقات
        self.info_card.setVisible(False)
        self.summary_card.setVisible(False)
        self.installments_card.setVisible(False)
        self.receipts_card.setVisible(False)
        
        # إعادة تعيين الحالة
        self.selected_student_id = None
        self.selected_student_data = {}
        self.print_btn.setEnabled(False)
        
        # إعادة تحميل الطلاب
        self.load_initial_students()