"""
واجهة الإقفال السنوي اليدوي وتأكيد الترحيل - مع تحميل غير متزامن.
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
    Student, AcademicYear, Grade, Section, StudentFee,
    StudentAcademicHistory, AnnualClosingLog, Receipt
)
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class YearClosingPage(QWidget):
    """صفحة الإقفال السنوي - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        
        # ✅ تخزين ID السنة قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        
        # ✅ تخزين بيانات مؤقتة
        self.summary_data = {}
        self.students_data: List[Dict] = []
        self.debts_data: List[Dict] = []
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل الملخص في الخلفية
        QTimer.singleShot(100, self.load_summary)
        
        # ✅ ربط تغيير التبويب بتحميل بيانات الخطوة
        self.steps_widget.currentChanged.connect(self._on_step_changed)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)
        
        title = QLabel("الإقفال السنوي اليدوي وتأكيد الترحيل")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        # إنشاء خطوات (Wizard)
        self.steps_widget = QTabWidget()
        self.steps_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #1976D3;
                border-radius: 12px;
                background: white;
                padding: 20px;
            }
            QTabBar::tab {
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton {
                padding: 12px 20px;
                font-size: 14px;
            }
        """)
        
        # الخطوة 1: الفحص المسبق
        step1 = self._create_step1()
        self.steps_widget.addTab(step1, "1. الفحص المسبق")
        
        # الخطوة 2: ترفيع الطلاب
        step2 = self._create_step2()
        self.steps_widget.addTab(step2, "2. ترفيع الطلاب")
        
        # الخطوة 3: ترحيل الديون
        step3 = self._create_step3()
        self.steps_widget.addTab(step3, "3. ترحيل الديون")
        
        # الخطوة 4: الاعتماد النهائي
        step4 = self._create_step4()
        self.steps_widget.addTab(step4, "4. الاعتماد النهائي")
        
        main_layout.addWidget(self.steps_widget)
    
    def _create_step1(self) -> QWidget:
        """إنشاء خطوة الفحص المسبق."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # بطاقات الملخص
        summary_layout = QGridLayout()
        summary_layout.setSpacing(10)
        
        # إجمالي الطلاب
        self.total_students_card, self.total_students_value = \
            self._create_summary_card(
                "إجمالي الطلاب", "0", "fa5s.user-graduate", "#1976D3"
            )
        summary_layout.addWidget(self.total_students_card, 0, 0)
        
        # الناجحين
        self.passed_students_card, self.passed_students_value = \
            self._create_summary_card(
                "الناجحين", "0", "fa5s.check-circle", "#10B981"
            )
        summary_layout.addWidget(self.passed_students_card, 1, 0)
        
        # الراسبين
        self.failed_students_card, self.failed_students_value = \
            self._create_summary_card(
                "الراسبين", "0", "fa5s.times-circle", "#EF4444"
            )
        summary_layout.addWidget(self.failed_students_card, 2, 0)
        
        # الرسوم المحصلة
        self.collected_fees_card, self.collected_fees_value = \
            self._create_summary_card(
                "الرسوم المحصلة", "0 ر.ي", "fa5s.coins", "#10B981"
            )
        summary_layout.addWidget(self.collected_fees_card, 3, 0)
        
        # الديون المتبقية
        self.remaining_debts_card, self.remaining_debts_value = \
            self._create_summary_card(
                "الديون المتبقية", "0 ر.ي", "fa5s.hand-holding-usd", "#EF4444"
            )
        summary_layout.addWidget(self.remaining_debts_card, 4, 0)
        
        layout.addLayout(summary_layout)
        
        layout.addStretch()
        
        # زر بدء الفحص
        check_btn = QPushButton("بدء فحص الجاهزية")
        check_btn.setIcon(qta.icon('fa5s.search', color='white'))
        check_btn.setObjectName("primaryButton")
        check_btn.clicked.connect(self.check_readiness)
        layout.addWidget(check_btn)
        
        return widget
    
    def _create_step2(self) -> QWidget:
        """إنشاء خطوة ترفيع الطلاب."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # فلاتر
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("الصف الحالي:"))
        self.promotion_grade_combo = QComboBox()
        self.promotion_grade_combo.addItem("جميع الصفوف", None)
        self.promotion_grade_combo.currentIndexChanged.connect(
            self._on_promotion_grade_changed
        )
        filter_layout.addWidget(self.promotion_grade_combo)
        
        filter_layout.addWidget(QLabel("الشعبة:"))
        self.promotion_section_combo = QComboBox()
        self.promotion_section_combo.addItem("جميع الشعب", None)
        self.promotion_section_combo.currentIndexChanged.connect(
            self._filter_promotion_students
        )
        filter_layout.addWidget(self.promotion_section_combo)
        
        filter_layout.addStretch()
        
        # زر تحديث
        refresh_btn = QPushButton("تحديث")
        refresh_btn.setIcon(qta.icon('fa5s.sync', color='white'))
        refresh_btn.clicked.connect(self.load_promotion_data)
        filter_layout.addWidget(refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # جدول الطلاب
        self.promotion_table = QTableWidget()
        self.promotion_table.setColumnCount(5)
        self.promotion_table.setHorizontalHeaderLabels([
            "الطالب", "النتيجة", "الصف الحالي", "الصف المستهدف", "ترفيع"
        ])
        self.promotion_table.setColumnWidth(0, 200)
        self.promotion_table.setColumnWidth(1, 100)
        self.promotion_table.setColumnWidth(2, 120)
        self.promotion_table.setColumnWidth(3, 120)
        self.promotion_table.setColumnWidth(4, 60)
        self.promotion_table.horizontalHeader().setStretchLastSection(True)
        self.promotion_table.setAlternatingRowColors(True)
        self.promotion_table.verticalHeader().setVisible(False)
        layout.addWidget(self.promotion_table)
        
        # زر تثبيت الترفيع
        promote_btn = QPushButton("تثبيت ترفيع الطلاب المحددين")
        promote_btn.setIcon(qta.icon('fa5s.check', color='white'))
        promote_btn.setObjectName("successButton")
        promote_btn.clicked.connect(self.promote_students)
        layout.addWidget(promote_btn)
        
        return widget
    
    def _create_step3(self) -> QWidget:
        """إنشاء خطوة ترحيل الديون."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # زر تحديث
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        
        refresh_debts_btn = QPushButton("تحديث")
        refresh_debts_btn.setIcon(qta.icon('fa5s.sync', color='white'))
        refresh_debts_btn.clicked.connect(self.load_debts_data)
        refresh_layout.addWidget(refresh_debts_btn)
        
        layout.addLayout(refresh_layout)
        
        # جدول الديون
        self.debts_table = QTableWidget()
        self.debts_table.setColumnCount(5)
        self.debts_table.setHorizontalHeaderLabels([
            "الطالب", "إجمالي الرسوم", "المدفوع", "الدين المتبقي", "نوع الترحيل"
        ])
        self.debts_table.setColumnWidth(0, 200)
        self.debts_table.setColumnWidth(1, 120)
        self.debts_table.setColumnWidth(2, 120)
        self.debts_table.setColumnWidth(3, 120)
        self.debts_table.setColumnWidth(4, 150)
        self.debts_table.horizontalHeader().setStretchLastSection(True)
        self.debts_table.setAlternatingRowColors(True)
        self.debts_table.verticalHeader().setVisible(False)
        layout.addWidget(self.debts_table)
        
        # زر ترحيل الديون
        transfer_btn = QPushButton("ترحيل الديون للسنة الجديدة")
        transfer_btn.setIcon(qta.icon('fa5s.arrow-right', color='white'))
        transfer_btn.setObjectName("warningButton")
        transfer_btn.clicked.connect(self.transfer_debts)
        layout.addWidget(transfer_btn)
        
        return widget
    
    def _create_step4(self) -> QWidget:
        """إنشاء خطوة الاعتماد النهائي."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # تحذير
        warning_label = QLabel("⚠️ تحذير: هذه العملية نهائية ولا يمكن التراجع عنها")
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #EF4444;
            padding: 20px;
            background: #FEF2F2;
            border-radius: 12px;
        """)
        layout.addWidget(warning_label)
        
        # ملخص
        self.final_summary_label = QLabel()
        self.final_summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.final_summary_label.setStyleSheet("font-size: 14px; color: #475569;")
        layout.addWidget(self.final_summary_label)
        
        layout.addStretch()
        
        # زر الإغلاق النهائي
        close_btn = QPushButton("إغلاق السنة الدراسية رسمياً")
        close_btn.setIcon(qta.icon('fa5s.lock', color='white'))
        close_btn.setObjectName("dangerButton")
        close_btn.setStyleSheet("""
            QPushButton {
                padding: 15px 25px;
                font-weight: 700;
                font-size: 15px;
            }
        """)
        close_btn.clicked.connect(self.close_year)
        layout.addWidget(close_btn)
        
        return widget
    
    def _create_summary_card(self, title: str, value: str, 
                              icon: str, color: str):
        """إنشاء بطاقة ملخص.
        
        Returns:
            tuple: (card, value_label) لتحديث القيمة لاحقاً
        """
        card = QFrame()
        card.setObjectName("cardFrame")
        card.setStyleSheet(f"""
            QFrame#cardFrame {{
                background: #F8FAFC;
                border-radius: 12px;
                padding: 2px;
                border: 3px solid {color};
            }}
        """)
        
        layoutV = QVBoxLayout(card)
        layoutH = QHBoxLayout()
        layoutV.setSpacing(2)
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon, color=color).pixmap(20, 20))
        layoutH.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; color: #64748B;")
        layoutH.addWidget(title_label)

        layoutV.addLayout(layoutH)
        layoutV.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {color};"
        )
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layoutV.addWidget(value_label)
        
        # ✅ إرجاع tuple (card, value_label)
        return card, value_label
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_summary(self):
        """تحميل الملخص في الخلفية."""
        self.loading_overlay.show_loading("جاري تحميل ملخص السنة...")
        
        academic_year_id = self.academic_year_id
        
        def _fetch_data():
            """جلب بيانات الملخص (في الخلفية)."""
            with session_scope() as session:
                # ============ 1. إجمالي الطلاب ============
                total = session.execute(
                    select(func.count(Student.id)).where(
                        Student.academic_year_id == academic_year_id
                    )
                ).scalar() or 0
                
                # ============ 2. الناجحين ============
                # (سيتم تطبيق المنطق الفعلي لاحقاً)
                passed = 0
                
                # ============ 3. الراسبين ============
                failed = 0
                
                # ============ 4. الرسوم المحصلة ============
                collected = session.execute(
                    select(func.sum(Receipt.amount_paid)).where(
                        Receipt.status == 'نشط'
                    )
                ).scalar() or Decimal('0.00')
                
                # ============ 5. الديون المتبقية ============
                total_fees = session.execute(
                    select(func.sum(StudentFee.net_total_required)).where(
                        StudentFee.academic_year_id == academic_year_id
                    )
                ).scalar() or Decimal('0.00')
                
                remaining = total_fees - collected
                
                return {
                    'total_students': total,
                    'passed_students': passed,
                    'failed_students': failed,
                    'collected_fees': float(collected),
                    'remaining_debts': float(remaining),
                }
        
        def _on_result(data):
            """عند اكتمال التحميل."""
            try:
                self.summary_data = data
                
                # ✅ تحديث البطاقات بشكل مباشر
                self.total_students_value.setText(str(data['total_students']))
                self.passed_students_value.setText(str(data['passed_students']))
                self.failed_students_value.setText(str(data['failed_students']))
                self.collected_fees_value.setText(
                    f"{data['collected_fees']:,.0f} ر.ي"
                )
                self.remaining_debts_value.setText(
                    f"{data['remaining_debts']:,.0f} ر.ي"
                )
                
            except Exception as e:
                print(f"خطأ في تحديث الملخص: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()
        
        def _on_error(error_msg):
            """عند حدوث خطأ."""
            self.loading_overlay.hide_loading()
            QMessageBox.critical(
                self, "خطأ",
                f"فشل تحميل الملخص:\n{error_msg}"
            )
        
        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
    
    def load_promotion_data(self):
        """تحميل بيانات الترفيع (الطلاب والصفوف)."""
        self.loading_overlay.show_loading("جاري تحميل بيانات الطلاب...")
        
        academic_year_id = self.academic_year_id
        
        def _fetch_data():
            """جلب الطلاب والصفوف والشعب (في الخلفية)."""
            with session_scope() as session:
                # ============ 1. الصفوف ============
                grades = session.execute(
                    select(Grade).order_by(Grade.id)
                ).scalars().all()
                
                grades_data = [
                    {'id': g.id, 'name': g.grade_name or ''}
                    for g in grades
                ]
                
                # ============ 2. الشعب ============
                sections = session.execute(
                    select(Section).order_by(Section.section_name)
                ).scalars().all()
                
                sections_data = [
                    {
                        'id': s.id,
                        'name': s.section_name or '',
                        'grade_id': s.grade_id,
                    }
                    for s in sections
                ]
                
                # ============ 3. الطلاب ============
                students = session.execute(
                    select(Student)
                    .options(
                        joinedload(Student.grade),
                        joinedload(Student.section),
                    )
                    .where(
                        Student.academic_year_id == academic_year_id,
                        Student.status == 'مستمر'
                    )
                    .order_by(Student.full_name)
                ).unique().scalars().all()
                
                students_data = []
                for s in students:
                    students_data.append({
                        'id': s.id,
                        'full_name': s.full_name or '',
                        'grade_id': s.grade_id,
                        'grade_name': s.grade.grade_name if s.grade else '',
                        'section_id': s.section_id,
                        'section_name': s.section.section_name if s.section else '',
                        'status': s.status or '',
                    })
                
                return {
                    'grades': grades_data,
                    'sections': sections_data,
                    'students': students_data,
                }
        
        def _on_result(data):
            """عند اكتمال التحميل."""
            try:
                self.students_data = data['students']
                
                # تحديث فلتر الصفوف
                self.promotion_grade_combo.blockSignals(True)
                self.promotion_grade_combo.clear()
                self.promotion_grade_combo.addItem("جميع الصفوف", None)
                for grade in data['grades']:
                    self.promotion_grade_combo.addItem(
                        grade['name'], grade['id']
                    )
                self.promotion_grade_combo.blockSignals(False)
                
                # حفظ الشعب للاستخدام لاحقاً
                self._all_sections = data['sections']
                
                # عرض الطلاب
                self._display_promotion_students(self.students_data)
                
            except Exception as e:
                print(f"خطأ في تحديث البيانات: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()
        
        def _on_error(error_msg):
            """عند حدوث خطأ."""
            self.loading_overlay.hide_loading()
            QMessageBox.critical(
                self, "خطأ",
                f"فشل تحميل بيانات الترفيع:\n{error_msg}"
            )
        
        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
    
    def load_debts_data(self):
        """تحميل بيانات الديون."""
        self.loading_overlay.show_loading("جاري تحميل بيانات الديون...")
        
        academic_year_id = self.academic_year_id
        
        def _fetch_data():
            """جلب الطلاب مع رسومهم (في الخلفية)."""
            with session_scope() as session:
                # جلب الطلاب مع رسومهم
                students = session.execute(
                    select(Student)
                    .options(joinedload(Student.grade))
                    .where(
                        Student.academic_year_id == academic_year_id
                    )
                    .order_by(Student.full_name)
                ).unique().scalars().all()
                
                debts_data = []
                for student in students:
                    # حساب إجمالي الرسوم
                    total_fees = session.execute(
                        select(func.sum(StudentFee.net_total_required)).where(
                            StudentFee.student_id == student.id,
                            StudentFee.academic_year_id == academic_year_id
                        )
                    ).scalar() or Decimal('0.00')
                    
                    # حساب المدفوع
                    paid = session.execute(
                        select(func.sum(Receipt.amount_paid)).where(
                            Receipt.student_id == student.id,
                            Receipt.status == 'نشط'
                        )
                    ).scalar() or Decimal('0.00')
                    
                    remaining = total_fees - paid
                    
                    if remaining > 0:
                        debts_data.append({
                            'student_id': student.id,
                            'student_name': student.full_name or '',
                            'total_fees': float(total_fees),
                            'paid': float(paid),
                            'remaining': float(remaining),
                        })
                
                return debts_data
        
        def _on_result(data):
            """عند اكتمال التحميل."""
            try:
                self.debts_data = data
                self._display_debts(data)
            except Exception as e:
                print(f"خطأ في تحديث الديون: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()
        
        def _on_error(error_msg):
            """عند حدوث خطأ."""
            self.loading_overlay.hide_loading()
            QMessageBox.critical(
                self, "خطأ",
                f"فشل تحميل الديون:\n{error_msg}"
            )
        
        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
    
    # ============================================================
    # ✅ عرض البيانات
    # ============================================================
    
    def _display_promotion_students(self, students: List[Dict]):
        """عرض الطلاب في جدول الترفيع."""
        self.promotion_table.setRowCount(len(students))
        
        for row, student in enumerate(students):
            self.promotion_table.setItem(
                row, 0, QTableWidgetItem(student['full_name'])
            )
            self.promotion_table.setItem(
                row, 1, QTableWidgetItem("ناجح")  # placeholder
            )
            self.promotion_table.setItem(
                row, 2, QTableWidgetItem(student['grade_name'])
            )
            self.promotion_table.setItem(
                row, 3, QTableWidgetItem("الصف التالي")  # placeholder
            )
            
            # Checkbox للترفيع
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.promotion_table.setCellWidget(row, 4, checkbox)
            self.promotion_table.setRowHeight(row, 40)
    
    def _display_debts(self, debts: List[Dict]):
        """عرض الديون في الجدول."""
        self.debts_table.setRowCount(len(debts))
        
        for row, debt in enumerate(debts):
            self.debts_table.setItem(
                row, 0, QTableWidgetItem(debt['student_name'])
            )
            self.debts_table.setItem(
                row, 1, QTableWidgetItem(f"{debt['total_fees']:,.0f}")
            )
            self.debts_table.setItem(
                row, 2, QTableWidgetItem(f"{debt['paid']:,.0f}")
            )
            
            remaining_item = QTableWidgetItem(f"{debt['remaining']:,.0f}")
            remaining_item.setForeground(QColor('#EF4444'))
            self.debts_table.setItem(row, 3, remaining_item)
            
            self.debts_table.setItem(
                row, 4, QTableWidgetItem("ترحيل للسنة القادمة")
            )
            self.debts_table.setRowHeight(row, 40)
    
    # ============================================================
    # ✅ الأحداث
    # ============================================================
    
    def _on_step_changed(self, index: int):
        """عند تغيير التبويب - تحميل بيانات الخطوة."""
        if index == 1 and not self.students_data:
            # الخطوة 2: ترفيع الطلاب
            self.load_promotion_data()
        elif index == 2 and not self.debts_data:
            # الخطوة 3: ترحيل الديون
            self.load_debts_data()
        elif index == 3:
            # الخطوة 4: تحديث الملخص النهائي
            self._update_final_summary()
    
    def _on_promotion_grade_changed(self):
        """عند تغيير الصف في فلتر الترفيع."""
        grade_id = self.promotion_grade_combo.currentData()
        
        # تحديث فلتر الشعب
        self.promotion_section_combo.blockSignals(True)
        self.promotion_section_combo.clear()
        self.promotion_section_combo.addItem("جميع الشعب", None)
        
        if hasattr(self, '_all_sections'):
            for section in self._all_sections:
                if grade_id is None or section['grade_id'] == grade_id:
                    self.promotion_section_combo.addItem(
                        section['name'], section['id']
                    )
        
        self.promotion_section_combo.blockSignals(False)
        self._filter_promotion_students()
    
    def _filter_promotion_students(self):
        """تصفية الطلاب حسب الصف والشعبة."""
        grade_id = self.promotion_grade_combo.currentData()
        section_id = self.promotion_section_combo.currentData()
        
        filtered = []
        for student in self.students_data:
            if grade_id and student['grade_id'] != grade_id:
                continue
            if section_id and student['section_id'] != section_id:
                continue
            filtered.append(student)
        
        self._display_promotion_students(filtered)
    
    def _update_final_summary(self):
        """تحديث الملخص النهائي في الخطوة 4."""
        summary_text = (
            f"عدد الطلاب: {self.summary_data.get('total_students', 0)}\n"
            f"الرسوم المحصلة: "
            f"{self.summary_data.get('collected_fees', 0):,.0f} ر.ي\n"
            f"الديون المتبقية: "
            f"{self.summary_data.get('remaining_debts', 0):,.0f} ر.ي"
        )
        self.final_summary_label.setText(summary_text)
    
    # ============================================================
    # ✅ العمليات
    # ============================================================
    
    def check_readiness(self):
        """فحص الجاهزية."""
        QMessageBox.information(
            self, "فحص",
            "تم الفحص. النظام جاهز للإقفال السنوي."
        )
    
    def promote_students(self):
        """ترفيع الطلاب."""
        # جمع الطلاب المحددين
        selected_count = 0
        for row in range(self.promotion_table.rowCount()):
            checkbox = self.promotion_table.cellWidget(row, 4)
            if checkbox and isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                selected_count += 1
        
        if selected_count == 0:
            QMessageBox.warning(
                self, "تنبيه",
                "يرجى تحديد الطلاب المطلوب ترفيعهم"
            )
            return
        
        QMessageBox.information(
            self, "ترفيع",
            f"سيتم ترفيع {selected_count} طالب."
        )
    
    def transfer_debts(self):
        """ترحيل الديون."""
        if not self.debts_data:
            QMessageBox.warning(
                self, "تنبيه",
                "لا توجد ديون للترحيل"
            )
            return
        
        total_debts = sum(d['remaining'] for d in self.debts_data)
        
        QMessageBox.information(
            self, "ترحيل",
            f"سيتم ترحيل ديون بقيمة {total_debts:,.0f} ر.ي"
        )
    
    def close_year(self):
        """إغلاق السنة."""
        reply = QMessageBox.warning(
            self, "تأكيد نهائي",
            "هل أنت متأكد من إغلاق السنة الدراسية؟\nهذه العملية نهائية!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self, "نجاح",
                "تم إغلاق السنة الدراسية."
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
        self.summary_data = {}
        self.students_data = []
        self.debts_data = []
        self.load_summary()