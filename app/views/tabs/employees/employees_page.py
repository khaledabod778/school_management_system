"""
واجهة إدارة الموظفين والمعلمين - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Dict, Optional
import qtawesome as qta
from datetime import date, datetime
from decimal import Decimal

from app.database.session import session_scope
from app.database.models import Employee, User, Role
from app.services.hr_users_factory import HrUsersFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import (
    KPICard, PageHeader, Card, QDateEditEN, QDoubleSpinBoxEN, 
    QLineEditPlus, SearchBox, ModernTable, Badge,
    GradientButton, IconButton, AvatarLabel
)
from app.views.widgets.dialogs import (
    ConfirmationDialog, SuccessDialog, ErrorDialog, ModernDialog
)
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select, func


class EmployeesPage(QWidget):
    """صفحة إدارة الموظفين - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ dicts بدلاً من ORM objects
        self.all_employees: List[Dict] = []
        self.current_filtered_employees: List[Dict] = []
        
        # ✅ debounce للبحث
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self.filter_employees)
        
        # ✅ مراجع لقيم KPI
        self.total_value_label = None
        self.active_value_label = None
        self.teachers_value_label = None
        self.on_leave_value_label = None
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل البيانات في الخلفية
        QTimer.singleShot(100, self.load_data)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)
        
        # رأس الصفحة
        title = QLabel("إدارة الموظفين والمعلمين")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("إدارة بيانات الكادر التعليمي والإداري")
        subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(subtitle)
        
        # بطاقات إحصائية
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.total_employees_card = KPICard(
            "إجمالي الموظفين", "0", "fa5s.users", "#1976D3"
        )
        stats_layout.addWidget(self.total_employees_card)
        
        self.active_employees_card = KPICard(
            "الموظفون النشطون", "0", "fa5s.user-check", "#10B981"
        )
        stats_layout.addWidget(self.active_employees_card)
        
        self.teachers_card = KPICard(
            "المعلمون", "0", "fa5s.chalkboard-teacher", "#42A5F5"
        )
        stats_layout.addWidget(self.teachers_card)
        
        self.on_leave_card = KPICard(
            "في إجازة", "0", "fa5s.user-clock", "#F59E0B"
        )
        stats_layout.addWidget(self.on_leave_card)
        
        main_layout.addWidget(self._create_widget(stats_layout))
        
        # ✅ اكتشاف مراجع قيم KPI
        self._find_kpi_value_labels()
        
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

        self.search_box = SearchBox("بحث عن موظف...")
        self.search_box.textChanged.connect(self._on_search_text_changed)
        filter_layout.addWidget(self.search_box)
        
        filter_layout.addWidget(QLabel("المسمى الوظيفي:"))
        self.job_filter = QComboBox()
        self.job_filter.addItem("جميع المسميات", None)
        self.job_filter.currentIndexChanged.connect(self.filter_employees)
        filter_layout.addWidget(self.job_filter)
        
        filter_layout.addWidget(QLabel("الحالة:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["جميع الحالات", "نشط", "إجازة", "مستقيل"])
        self.status_filter.currentIndexChanged.connect(self.filter_employees)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch()
        
        add_btn = GradientButton("إضافة موظف", "fa5s.plus")
        add_btn.clicked.connect(self.add_employee)
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
        
        self.count_label = QLabel("إجمالي الموظفين: 0")
        self.count_label.setObjectName("count_label")       
        toolbar.addWidget(self.count_label)
        
        toolbar.addStretch()
        
        edit_btn = IconButton('fa5s.edit', "تعديل", color='#1976D3')
        edit_btn.clicked.connect(self.edit_employee)
        toolbar.addWidget(edit_btn)
        
        delete_btn = IconButton('fa5s.trash', "حذف", color='#EF4444')
        delete_btn.clicked.connect(self.delete_employee)
        toolbar.addWidget(delete_btn)
        
        print_btn = IconButton('fa5s.print', "طباعة", color='#10B981')
        print_btn.clicked.connect(self.print_employee)
        toolbar.addWidget(print_btn)

        card_layout.addLayout(toolbar)
                
        # الجدول
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "صورة", "الاسم", "المسمى", "الهاتف", "الراتب",
            "الحالة", "تاريخ التعاقد", "إجراء"
        ])
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 190)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 100)
        self.table.setColumnWidth(7, 80)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)        
        self.table.doubleClicked.connect(self.edit_employee)
        card_layout.addWidget(self.table)
        
        main_layout.addWidget(table_card)
    
    def _create_widget(self, layout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    def _find_kpi_value_labels(self):
        """✅ البحث عن مراجع قيم KPI بشكل آمن."""
        try:
            cards = [
                (self.total_employees_card, 'total'),
                (self.active_employees_card, 'active'),
                (self.teachers_card, 'teachers'),
                (self.on_leave_card, 'on_leave'),
            ]
            
            for card, key in cards:
                labels = card.findChildren(QLabel)
                value_label = None
                for lbl in labels:
                    if lbl.text() == "0":
                        value_label = lbl
                        break
                
                if key == 'total':
                    self.total_value_label = value_label
                elif key == 'active':
                    self.active_value_label = value_label
                elif key == 'teachers':
                    self.teachers_value_label = value_label
                elif key == 'on_leave':
                    self.on_leave_value_label = value_label
        except Exception as e:
            print(f"خطأ في البحث عن مراجع KPI: {str(e)}")
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_data(self):
        """تحميل - Local أو Remote."""
        self.loading_overlay.show_loading("جاري تحميل الموظفين...")

        def _fetch():
            if HrUsersFactory.is_remote():
                service = HrUsersFactory.get_service()
                return service.list_employees()
            else:
                from app.database.session import session_scope
                from app.database.models import Employee
                from sqlalchemy import select
                with session_scope() as session:
                    employees = session.execute(
                        select(Employee).filter(
                            Employee.deleted_at.is_(None)
                        ).order_by(Employee.full_name)
                    ).scalars().all()
                    return [
                        {
                            'id': e.id,
                            'full_name': e.full_name or '',
                            'job_title': e.job_title or '',
                            'qualification': e.qualification or '',
                            'primary_phone': e.primary_phone or '',
                            'secondary_phone': e.secondary_phone or '',
                            'status': e.status or '',
                            'basic_salary': float(e.basic_salary or 0),
                            'contract_start_date_str': (
                                e.contract_start_date.strftime("%Y/%m/%d")
                                if e.contract_start_date else ''
                            ),
                            'gender': e.gender or 'ذكر',
                            'marital_status': e.marital_status or 'أعزب',
                            'address': e.address or '',
                            'national_id': e.national_id or '',
                            'id_issue_place': e.id_issue_place or '',
                            'birth_village': e.birth_village or '',
                            'birth_district': e.birth_district or '',
                            'birth_governorate': e.birth_governorate or '',
                            'payment_method': e.payment_method or 'نقداً',
                            'bank_account_number': e.bank_account_number or '',
                            'id_issue_date': e.id_issue_date.isoformat() if e.id_issue_date else None,
                            'birth_date': e.birth_date.isoformat() if e.birth_date else None,
                            'contract_start_date': e.contract_start_date.isoformat() if e.contract_start_date else None,
                            'contract_end_date': e.contract_end_date.isoformat() if e.contract_end_date else None,
                        }
                        for e in employees
                    ]

        def _ok(data):
            try:
                self.all_employees = data
                self.current_filtered_employees = list(self.all_employees)

                # فلتر المسميات
                titles_set = sorted({e['job_title'] for e in data if e['job_title']})
                self.job_filter.blockSignals(True)
                self.job_filter.clear()
                self.job_filter.addItem("جميع المسميات", None)
                for t in titles_set:
                    self.job_filter.addItem(t, t)
                self.job_filter.blockSignals(False)

                # إحصائيات
                self._update_stats_display({
                    'total': len(data),
                    'active': sum(1 for e in data if e['status'] == 'نشط'),
                    'teachers': sum(
                        1 for e in data
                        if 'معلم' in (e['job_title'] or '')
                        or 'مدرس' in (e['job_title'] or '')
                    ),
                    'on_leave': sum(1 for e in data if e['status'] == 'إجازة'),
                })

                self.display_employees(self.all_employees)
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            ErrorDialog("خطأ", f"فشل: {m}", self).exec()

        run_async(_fetch, on_result=_ok, on_error=_err)
        
    # ============================================================
    # ✅ عرض البيانات
    # ============================================================
    
    def display_employees(self, employees: List[Dict]):
        """عرض الموظفين."""
        self.table.setRowCount(len(employees))
        
        status_colors = {
            'نشط': '#10B981',
            'إجازة': '#F59E0B',
            'مستقيل': '#EF4444'
        }
        
        for row, employee in enumerate(employees):
            # صورة الموظف
            avatar_widget = QWidget()
            avatar_widget.setStyleSheet("background: transparent;")
            avatar_layout = QHBoxLayout(avatar_widget)
            avatar_layout.setContentsMargins(5, 2, 5, 2)
            avatar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            avatar = AvatarLabel(employee['full_name'], 30, '#42A5F5')
            avatar_layout.addWidget(avatar)
            
            self.table.setCellWidget(row, 0, avatar_widget)
            self.table.setItem(
                row, 1, QTableWidgetItem(employee['full_name'])
            )
            self.table.setItem(
                row, 2, QTableWidgetItem(employee['job_title'])
            )
            self.table.setItem(
                row, 3, QTableWidgetItem(employee['primary_phone'])
            )
            
            # الراتب
            salary_item = QTableWidgetItem(f"{employee['basic_salary']:,.2f}")
            salary_item.setForeground(QColor('#10B981'))
            self.table.setItem(row, 4, salary_item)
            
            # الحالة
            status_item = QTableWidgetItem(employee['status'])
            status_item.setForeground(
                QColor(status_colors.get(employee['status'], '#64748B'))
            )
            self.table.setItem(row, 5, status_item)
            
            self.table.setItem(
                row, 6, 
                QTableWidgetItem(employee['contract_start_date_str'])
            )
            
            # زر التفاصيل
            details_btn = QPushButton()
            details_btn.setIcon(qta.icon('fa5s.info-circle', color='#1976D3'))
            details_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            details_btn.setStyleSheet("""
                QPushButton {
                    background: #F1F5F9;
                    border: none;
                    border-radius: 6px;
                    padding: 0px 5px;
                }
                QPushButton:hover {
                    background: #E2E8F0;
                }
            """)
            # ✅ تمرير ID
            details_btn.clicked.connect(
                lambda checked, eid=employee['id']: 
                self.show_employee_details(eid)
            )
            self.table.setCellWidget(row, 7, details_btn)

            self.table.setRowHeight(row, 45)
        
        self.count_label.setText(f"إجمالي الموظفين: {len(employees)}")
    
    def _update_stats_display(self, stats: Dict):
        """تحديث بطاقات الإحصائيات."""
        try:
            if self.total_value_label:
                self.total_value_label.setText(str(stats['total']))
            if self.active_value_label:
                self.active_value_label.setText(str(stats['active']))
            if self.teachers_value_label:
                self.teachers_value_label.setText(str(stats['teachers']))
            if self.on_leave_value_label:
                self.on_leave_value_label.setText(str(stats['on_leave']))
        except Exception as e:
            print(f"خطأ في تحديث الإحصائيات: {str(e)}")
    
    # ============================================================
    # ✅ الفلترة
    # ============================================================
    
    def _on_search_text_changed(self):
        """عند تغيير نص البحث - debounce."""
        self._search_timer.stop()
        self._search_timer.start()
    
    def filter_employees(self):
        """تصفية الموظفين."""
        search_text = self.search_box.text().lower().strip()
        job_title = self.job_filter.currentData()
        status = self.status_filter.currentText()
        
        filtered = []
        for employee in self.all_employees:
            # فلتر البحث
            if search_text:
                full_name = employee['full_name'].lower()
                phone = employee['primary_phone'].lower()
                if search_text not in full_name and search_text not in phone:
                    continue
            
            # فلتر المسمى
            if job_title and employee['job_title'] != job_title:
                continue
            
            # فلتر الحالة
            if status != "جميع الحالات" and employee['status'] != status:
                continue
            
            filtered.append(employee)
        
        self.current_filtered_employees = filtered
        self.display_employees(filtered)
    
    # ============================================================
    # ✅ الحصول على الموظف المحدد
    # ============================================================
    
    def _get_selected_employee_id(self) -> Optional[int]:
        """الحصول على ID الموظف المحدد."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
        
        if current_row >= len(self.current_filtered_employees):
            return None
        
        return self.current_filtered_employees[current_row]['id']
    
    # ============================================================
    # ✅ العمليات
    # ============================================================
    
    def add_employee(self):
        """إضافة موظف جديد."""
        if self.permission_service and not self.permission_service.can_add("الموظفين والمعلمين"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للإضافة في الموظفين والمعلمين"
            )
            return

        dialog = EmployeeDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            SuccessDialog("نجاح", "تم إضافة الموظف بنجاح", self).exec()
    
    def edit_employee(self):
        if (self.permission_service
                and not self.permission_service.can_edit("الموظفين والمعلمين")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        eid = self._get_selected_employee_id()
        if not eid:
            ErrorDialog("تنبيه", "اختر موظفاً", self).exec()
            return

        try:
            if HrUsersFactory.is_remote():
                employee_data = HrUsersFactory.get_service().get_employee(eid)
            else:
                from app.database.session import session_scope
                from app.database.models import Employee
                with session_scope() as session:
                    e = session.get(Employee, eid)
                    if not e:
                        return
                    employee_data = {
                        'id': e.id,
                        'full_name': e.full_name or '',
                        'job_title': e.job_title or '',
                        'qualification': e.qualification or '',
                        'gender': e.gender or 'ذكر',
                        'marital_status': e.marital_status or 'أعزب',
                        'primary_phone': e.primary_phone or '',
                        'secondary_phone': e.secondary_phone or '',
                        'status': e.status or 'نشط',
                        'address': e.address or '',
                        'national_id': e.national_id or '',
                        'id_issue_place': e.id_issue_place or '',
                        'id_issue_date': e.id_issue_date,
                        'birth_date': e.birth_date,
                        'birth_village': e.birth_village or '',
                        'birth_district': e.birth_district or '',
                        'birth_governorate': e.birth_governorate or '',
                        'contract_start_date': e.contract_start_date,
                        'contract_end_date': e.contract_end_date,
                        'basic_salary': float(e.basic_salary or 0),
                        'payment_method': e.payment_method or '',
                        'bank_account_number': e.bank_account_number or '',
                    }

            dialog = EmployeeDialog(employee_data=employee_data, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_data()
                SuccessDialog("نجاح", "تم التحديث", self).exec()
        except Exception as ex:
            ErrorDialog("خطأ", f"فشل: {ex}", self).exec()

    def delete_employee(self):
        if (self.permission_service
                and not self.permission_service.can_delete("الموظفين والمعلمين")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        eid = self._get_selected_employee_id()
        if not eid:
            return

        emp = next((e for e in self.all_employees if e['id'] == eid), None)
        if not emp:
            return

        if ConfirmationDialog(
            "حذف موظف", f"حذف: {emp['full_name']}؟", self
        ).exec() != QDialog.DialogCode.Accepted:
            return

        try:
            if HrUsersFactory.is_remote():
                HrUsersFactory.get_service().delete_employee(eid)
            else:
                from app.database.session import session_scope
                from app.database.models import Employee
                with session_scope() as session:
                    e = session.get(Employee, eid)
                    if e:
                        session.delete(e)
            SuccessDialog("نجاح", "تم الحذف", self).exec()
            self.load_data()
        except Exception as ex:
            ErrorDialog("خطأ", f"فشل: {ex}", self).exec()

    def print_employee(self):
        """طباعة بيانات موظف."""
        if self.permission_service and not self.permission_service.can_print("الموظفين والمعلمين"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية للطباعة في الموظفين والمعلمين"
            )
            return

        employee_id = self._get_selected_employee_id()
        if not employee_id:
            ErrorDialog("تنبيه", "يرجى اختيار موظف للطباعة", self).exec()
            return
        
        QMessageBox.information(
            self, 
            "طباعة", 
            "سيتم تنفيذ الطباعة في مرحلة التقارير"
        )
    
    def show_employee_details(self, employee_id: int):
        try:
            if HrUsersFactory.is_remote():
                data = HrUsersFactory.get_service().get_employee(employee_id)
                # حوّل contract_start_date إلى str للعرض
                csd = data.get('contract_start_date')
                data['contract_start_date_str'] = csd or '-'
            else:
                from app.database.session import session_scope
                from app.database.models import Employee
                with session_scope() as session:
                    e = session.get(Employee, employee_id)
                    if not e:
                        return
                    data = {
                        'full_name': e.full_name or '',
                        'job_title': e.job_title or '',
                        'qualification': e.qualification or '',
                        'primary_phone': e.primary_phone or '',
                        'status': e.status or '',
                        'basic_salary': float(e.basic_salary or 0),
                        'contract_start_date_str': (
                            e.contract_start_date.strftime("%Y/%m/%d")
                            if e.contract_start_date else '-'
                        ),
                        'payment_method': e.payment_method or '',
                    }
            EmployeeDetailsDialog(data, parent=self).exec()
        except Exception as ex:
            ErrorDialog("خطأ", f"فشل: {ex}", self).exec()

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
# ✅ نافذة إضافة/تعديل موظف (مع dicts)
# ============================================================

class EmployeeDialog(ModernDialog):
    """نافذة إضافة/تعديل موظف."""
    
    def __init__(self, employee_data: Optional[dict] = None, parent=None):
        super().__init__(
            "تعديل موظف" if employee_data else "إضافة موظف جديد",
            "fa5s.user-tie",
            parent,
            width=650,
            height=550
        )
        
        # ✅ تخزين dict بدلاً من ORM
        self.employee_data = employee_data
        self.employee_id = employee_data['id'] if employee_data else None
        
        self.setup_form()
        
        if employee_data:
            self.load_employee_data()
    
    def setup_form(self):
        """إعداد النموذج."""
        self.tabs = QTabWidget()
        
        personal_tab = self._create_personal_tab()
        self.tabs.addTab(personal_tab, "البيانات الشخصية")
        
        identity_tab = self._create_identity_tab()
        self.tabs.addTab(identity_tab, "بيانات الهوية")
        
        financial_tab = self._create_financial_tab()
        self.tabs.addTab(financial_tab, "البيانات المالية")
        
        self.add_widget(self.tabs)
        
        self.add_button("إلغاء", self.reject, "default")
        self.add_button("حفظ", self.save_employee, "primary")
    
    def _create_personal_tab(self) -> QWidget:
        """إنشاء تبويب البيانات الشخصية."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        layout.addWidget(self._create_label("الاسم الكامل:"))
        self.full_name_input = QLineEditPlus("أدخل الاسم الرباعي")
        layout.addWidget(self.full_name_input)
        
        row1 = QHBoxLayout()
        
        row1.addWidget(self._create_label("المسمى الوظيفي:"))
        self.job_title_input = QLineEditPlus("مثال: معلم رياضيات")
        row1.addWidget(self.job_title_input)
        
        row1.addWidget(self._create_label("المؤهل العلمي:"))
        self.qualification_input = QLineEditPlus("مثال: بكالوريوس")
        row1.addWidget(self.qualification_input)
        
        layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        
        row2.addWidget(self._create_label("الجنس:"))
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["ذكر", "أنثى"])
        row2.addWidget(self.gender_combo)
        
        row2.addWidget(self._create_label("الحالة الاجتماعية:"))
        self.marital_combo = QComboBox()
        self.marital_combo.addItems(["أعزب", "متزوج", "مطلق", "أرمل"])
        row2.addWidget(self.marital_combo)
        
        layout.addLayout(row2)
        
        row3 = QHBoxLayout()
        
        row3.addWidget(self._create_label("الهاتف الرئيسي:"))
        self.primary_phone_input = QLineEditPlus()
        row3.addWidget(self.primary_phone_input)
        
        row3.addWidget(self._create_label("الهاتف الثانوي:"))
        self.secondary_phone_input = QLineEditPlus()
        row3.addWidget(self.secondary_phone_input)
        
        layout.addLayout(row3)
        
        row4 = QHBoxLayout()
        
        row4.addWidget(self._create_label("الحالة:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["نشط", "إجازة", "مستقيل"])
        row4.addWidget(self.status_combo)
        
        row4.addWidget(self._create_label("العنوان:"))
        self.address_input = QLineEditPlus()
        row4.addWidget(self.address_input)
        
        layout.addLayout(row4)
        
        layout.addStretch()
        
        return widget
    
    def _create_identity_tab(self) -> QWidget:
        """إنشاء تبويب بيانات الهوية."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        layout.addWidget(self._create_label("رقم البطاقة/الهوية:"))
        self.national_id_input = QLineEditPlus()
        layout.addWidget(self.national_id_input)
        
        row1 = QHBoxLayout()
        
        row1.addWidget(self._create_label("مكان الإصدار:"))
        self.id_issue_place_input = QLineEditPlus()
        row1.addWidget(self.id_issue_place_input)
        
        row1.addWidget(self._create_label("تاريخ الإصدار:"))
        self.id_issue_date_input = QDateEditEN()
        row1.addWidget(self.id_issue_date_input)
        
        layout.addLayout(row1)
        
        layout.addWidget(self._create_label("تاريخ الميلاد:"))
        self.birth_date_input = QDateEditEN(QDate(1990, 1, 1))
        layout.addWidget(self.birth_date_input)
        
        row2 = QHBoxLayout()
        
        row2.addWidget(self._create_label("القرية:"))
        self.village_input = QLineEditPlus()
        row2.addWidget(self.village_input)
        
        row2.addWidget(self._create_label("المديرية:"))
        self.district_input = QLineEditPlus()
        row2.addWidget(self.district_input)
        
        layout.addLayout(row2)
        
        layout.addWidget(self._create_label("المحافظة:"))
        self.governorate_input = QLineEditPlus()
        layout.addWidget(self.governorate_input)
        
        layout.addStretch()
        
        return widget
    
    def _create_financial_tab(self) -> QWidget:
        """إنشاء تبويب البيانات المالية."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        row1 = QHBoxLayout()
        
        row1.addWidget(self._create_label("بداية العقد:"))
        self.contract_start_input = QDateEditEN()
        row1.addWidget(self.contract_start_input)
        
        row1.addWidget(self._create_label("نهاية العقد:"))
        self.contract_end_input = QDateEditEN(QDate.currentDate().addYears(1))
        row1.addWidget(self.contract_end_input)
        
        layout.addLayout(row1)
        
        layout.addWidget(self._create_label("الراتب الأساسي:"))
        self.basic_salary_input = QDoubleSpinBoxEN()
        self.basic_salary_input.setStyleSheet("""
            QDoubleSpinBox {
                border: 2px solid #10B981;
                border-radius: 8px;
                padding: 8px;
                font-weight: 700;
                font-size: 16px;
                color: #059669;
                background: #ECFDF5;
            }
        """)
        layout.addWidget(self.basic_salary_input)
        
        row2 = QHBoxLayout()
        
        row2.addWidget(self._create_label("طريقة الصرف:"))
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems([
            "حساب بنكي", "محفظة إلكترونية", "نقداً"
        ])
        row2.addWidget(self.payment_method_combo)
        
        row2.addWidget(self._create_label("رقم الحساب:"))
        self.bank_account_input = QLineEditPlus()
        row2.addWidget(self.bank_account_input)
        
        layout.addLayout(row2)
        
        layout.addStretch()
        
        return widget
    
    def _create_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            "color: #475569; font-weight: 600; font-size: 12px;"
        )
        return label
    
    def load_employee_data(self):
        """تحميل بيانات الموظف (من dict)."""
        if not self.employee_data:
            return
        
        def _set_date(input_widget, value):
            if not value:
                return
            if isinstance(value, str):
                try:
                    value = date.fromisoformat(value)
                except Exception:
                    return
            input_widget.setDate(QDate(value.year, value.month, value.day))        
        
        d = self.employee_data
        
        self.full_name_input.setText(d['full_name'])
        self.job_title_input.setText(d['job_title'])
        self.qualification_input.setText(d['qualification'])
        self.gender_combo.setCurrentText(d['gender'])
        self.marital_combo.setCurrentText(d['marital_status'])
        self.primary_phone_input.setText(d['primary_phone'])
        self.secondary_phone_input.setText(d['secondary_phone'])
        self.status_combo.setCurrentText(d['status'])
        self.address_input.setText(d['address'])
        
        self.national_id_input.setText(d['national_id'])
        self.id_issue_place_input.setText(d['id_issue_place'])

        _set_date(self.id_issue_date_input, d.get('id_issue_date'))
        
        _set_date(self.birth_date_input, d.get('birth_date'))
                
        self.village_input.setText(d['birth_village'])
        self.district_input.setText(d['birth_district'])
        self.governorate_input.setText(d['birth_governorate'])
        
        _set_date(self.contract_start_input, d.get('contract_start_date'))
        
        _set_date(self.contract_end_input, d.get('contract_end_date'))        
        
        self.basic_salary_input.setValue(d['basic_salary'])
        self.payment_method_combo.setCurrentText(d['payment_method'])
        self.bank_account_input.setText(d['bank_account_number'])
    
    def save_employee(self):
        if not self.full_name_input.text().strip():
            ErrorDialog("تنبيه", "أدخل الاسم", self).exec()
            return
        if not self.job_title_input.text().strip():
            ErrorDialog("تنبيه", "أدخل المسمى", self).exec()
            return

        def _to_iso(qdate):
            return date(qdate.year(), qdate.month(), qdate.day()).isoformat()

        payload = {
            'full_name': self.full_name_input.text().strip(),
            'job_title': self.job_title_input.text().strip(),
            'qualification': self.qualification_input.text().strip() or None,
            'gender': self.gender_combo.currentText(),
            'marital_status': self.marital_combo.currentText(),
            'primary_phone': self.primary_phone_input.text().strip() or None,
            'secondary_phone': self.secondary_phone_input.text().strip() or None,
            'status': self.status_combo.currentText(),
            'address': self.address_input.text().strip() or None,
            'national_id': self.national_id_input.text().strip() or None,
            'id_issue_place': self.id_issue_place_input.text().strip() or None,
            'id_issue_date': _to_iso(self.id_issue_date_input.date()),
            'birth_date': _to_iso(self.birth_date_input.date()),
            'birth_village': self.village_input.text().strip() or None,
            'birth_district': self.district_input.text().strip() or None,
            'birth_governorate': self.governorate_input.text().strip() or None,
            'contract_start_date': _to_iso(self.contract_start_input.date()),
            'contract_end_date': _to_iso(self.contract_end_input.date()),
            'basic_salary': float(self.basic_salary_input.value()),
            'payment_method': self.payment_method_combo.currentText(),
            'bank_account_number': self.bank_account_input.text().strip() or None,
        }

        try:
            if HrUsersFactory.is_remote():
                service = HrUsersFactory.get_service()
                if self.employee_id:
                    service.update_employee(self.employee_id, payload)
                else:
                    service.create_employee(payload)
            else:
                self._save_local(payload)
            self.accept()
        except Exception as ex:
            ErrorDialog("خطأ", f"فشل: {ex}", self).exec()

    def _save_local(self, payload):
        from app.database.session import session_scope
        from app.database.models import Employee
        with session_scope() as session:
            if self.employee_id:
                e = session.get(Employee, self.employee_id)
            else:
                e = Employee()
                session.add(e)
            for k, v in payload.items():
                if k in ('id_issue_date', 'birth_date',
                         'contract_start_date', 'contract_end_date'):
                    setattr(e, k, date.fromisoformat(v) if v else None)
                elif k == 'basic_salary':
                    e.basic_salary = Decimal(str(v))
                else:
                    setattr(e, k, v)


# ============================================================
# ✅ نافذة تفاصيل الموظف (مع dicts)
# ============================================================

class EmployeeDetailsDialog(ModernDialog):
    """نافذة تفاصيل الموظف."""
    
    def __init__(self, employee_data: dict, parent=None):
        super().__init__(
            f"تفاصيل الموظف: {employee_data.get('full_name', '')}",
            "fa5s.user-tie",
            parent,
            width=500,
            height=400
        )
        
        # ✅ dict بدلاً من ORM
        d = employee_data
        
        # عرض المعلومات في شبكة
        info_widget = QWidget()
        info_layout = QGridLayout(info_widget)
        info_layout.setSpacing(10)
        
        details = [
            ("الاسم:", d.get('full_name', '-')),
            ("المسمى:", d.get('job_title', '-')),
            ("المؤهل:", d.get('qualification') or '-'),
            ("الهاتف:", d.get('primary_phone') or '-'),
            ("الحالة:", d.get('status', '-')),
            ("الراتب:", f"{d.get('basic_salary', 0):,.2f} ر.ي"),
            ("تاريخ التعاقد:", d.get('contract_start_date_str', '-')),
            ("طريقة الصرف:", d.get('payment_method', '-')),
        ]
        
        for row, (label, value) in enumerate(details):
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #64748B; font-weight: 600;")
            info_layout.addWidget(label_widget, row, 0)
            
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #0F172A; font-weight: 500;")
            info_layout.addWidget(value_widget, row, 1)
        
        self.add_widget(info_widget)
        
        # زر إغلاق
        self.add_button("إغلاق", self.accept, "primary")