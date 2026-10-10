"""
واجهة إدارة السنوات الدراسية.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional
import qtawesome as qta
from datetime import date

from app.database.models.users import User
from app.database.session import session_scope
from app.database.models import AcademicYear
from sqlalchemy import select

from app.services.academic_factory import AcademicFactory
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import GradientButton, QDateEditEN, QLineEditPlus
from app.views.widgets.dialogs import ModernDialog, SuccessDialog


class AcademicYearsPage(QWidget):
    """صفحة إدارة السنوات الدراسية."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.permission_service = permission_service
        self.current_year = academic_year
        self.all_years: List[AcademicYear] = []
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)
        
        # رأس الصفحة
        title = QLabel("إدارة السنوات الدراسية")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("إضافة وتعديل السنوات الدراسية")
        subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(subtitle)
        
        # بطاقة الجدول
        tableCard = QFrame()
        tableCard.setObjectName("tableCard")
        
        card_layout = QVBoxLayout(tableCard)
        
        # شريط الأدوات
        toolbar = QHBoxLayout()
        
        self.count_label = QLabel("عدد السنوات: 0")
        self.count_label.setObjectName("count_label")
        toolbar.addWidget(self.count_label)
        
        toolbar.addStretch()
        
        add_btn = GradientButton("إضافة سنة دراسية", "fa5s.plus")
        add_btn.clicked.connect(self.add_year)
        toolbar.addWidget(add_btn)
        
        card_layout.addLayout(toolbar)
        
        # الجدول
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "السنة الميلادية", "السنة الهجرية", "تاريخ البداية",
            "تاريخ النهاية", "الحالة", "إجراء"
        ])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 150)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        card_layout.addWidget(self.table)
        
        main_layout.addWidget(tableCard)
    
    def load_data(self):
        """تحميل البيانات - Local أو Remote."""
        if AcademicFactory.is_remote():
            try:
                service = AcademicFactory.get_service()
                self.all_years = service.list_years()
                self.display_years()
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل تحميل البيانات: {e}")
        else:
            try:
                from app.database.session import session_scope
                from app.database.models import AcademicYear
                from sqlalchemy import select
                with session_scope() as session:
                    years = session.execute(
                        select(AcademicYear)
                        .order_by(AcademicYear.start_date.desc())
                    ).scalars().all()
                    self.all_years = [
                        {
                            'id': y.id,
                            'year_name_gregorian': y.year_name_gregorian or '',
                            'year_name_hijri': y.year_name_hijri or '',
                            'start_date': y.start_date.isoformat() if y.start_date else '',
                            'end_date': y.end_date.isoformat() if y.end_date else '',
                            'is_current': bool(y.is_current),
                            'is_closed': bool(y.is_closed),
                            'status': y.status or '',
                        }
                        for y in years
                    ]
                    self.display_years()
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل تحميل البيانات: {e}")

    def display_years(self):
        """عرض السنوات."""
        from datetime import date as dt_date
        self.table.setRowCount(len(self.all_years))

        for row, year in enumerate(self.all_years):
            self.table.setItem(row, 0, QTableWidgetItem(year['year_name_gregorian']))
            self.table.setItem(row, 1, QTableWidgetItem(year['year_name_hijri']))
            self.table.setItem(row, 2, QTableWidgetItem(year['start_date']))
            self.table.setItem(row, 3, QTableWidgetItem(year['end_date']))

            status_text = (
                "حالية" if year['is_current']
                else ("مغلقة" if year['is_closed'] else "قادمة")
            )
            status_item = QTableWidgetItem(status_text)
            status_colors = {'حالية': '#10B981', 'مغلقة': '#64748B', 'قادمة': '#F59E0B'}
            status_item.setForeground(QColor(status_colors.get(status_text, '#64748B')))
            self.table.setItem(row, 4, status_item)

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 0, 5, 0)

            if not year['is_current'] and not year['is_closed']:
                set_btn = QPushButton("تحديد كحالية")
                set_btn.setObjectName("successButton")
                set_btn.clicked.connect(
                    lambda checked, y=year: self.set_current_year(y)
                )
                action_layout.addWidget(set_btn)

            edit_btn = QPushButton("تعديل")
            edit_btn.setObjectName("warningButton")
            edit_btn.clicked.connect(
                lambda checked, y=year: self.edit_year(y)
            )
            action_layout.addWidget(edit_btn)

            self.table.setCellWidget(row, 5, action_widget)
            self.table.setRowHeight(row, 45)

        self.count_label.setText(f"عدد السنوات: {len(self.all_years)}")

    def set_current_year(self, year):
        """تحديد السنة كحالية."""
        if not self.permission_service.can_edit("التهيئة الأكاديمية"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return
        try:
            if AcademicFactory.is_remote():
                service = AcademicFactory.get_service()
                service.set_current_year(year['id'])
            else:
                from app.database.session import session_scope
                from app.database.models import AcademicYear
                with session_scope() as session:
                    session.query(AcademicYear).filter(
                        AcademicYear.is_current == True
                    ).update({'is_current': False, 'status': 'closed'})
                    y = session.get(AcademicYear, year['id'])
                    y.is_current = True
                    y.status = 'current'
                    y.is_closed = False
            QMessageBox.information(self, "نجاح", "تم تحديد السنة كحالية")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل: {e}")
            
    def add_year(self):
        """إضافة سنة دراسية."""
        if not self.permission_service.can_add("التهيئة الأكاديمية"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية للإضافة في التهيئة الأكاديمية")
            return
                
        dialog = AcademicYearDialog(self.user, year=None, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            SuccessDialog("نجاح", "تم إضافة سنة دراسية بنجاح", self).exec()
    
    def edit_year(self, year: AcademicYear):
        """تعديل سنة دراسية."""
        if not self.permission_service.can_edit("التهيئة الأكاديمية"):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية للتعديل في التهيئة الأكاديمية")
            return
    
        dialog = AcademicYearDialog(self.user, year=year, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            SuccessDialog("نجاح", "تم تحديث بيانات سنة دراسية بنجاح", self).exec()


class AcademicYearDialog(ModernDialog):
    """نافذة إضافة/تعديل سنة دراسية."""
    
    def __init__(self, user: User, year: Optional[AcademicYear] = None, parent=None):
        super().__init__(
            "تعديل سنة" if year else "إضافة سنة دراسية",
            "fa5s.plus",
            parent,
            width=500,
            height=460
        )
        self.year = year        
        self.setup_ui()
        
    
    def setup_ui(self):
        """إعداد النموذج."""
        layout = QVBoxLayout()
        
        # السنة الميلادية
        self.add_widget(QLabel("السنة الميلادية:"))
        self.gregorian_input = QLineEditPlus(placeholder="مثال: 2025-2026")
        self.add_widget(self.gregorian_input)
        
        # السنة الهجرية
        self.add_widget(QLabel("السنة الهجرية:"))
        self.hijri_input = QLineEditPlus(placeholder="مثال: 1447هـ")
        self.add_widget(self.hijri_input)
        
        # تاريخ البداية
        self.add_widget(QLabel("تاريخ البداية:"))
        self.start_date = QDateEditEN()
        self.add_widget(self.start_date)
        
        # تاريخ النهاية
        self.add_widget(QLabel("تاريخ النهاية:"))
        self.end_date = QDateEditEN(QDate.currentDate().addMonths(10))
        self.add_widget(self.end_date)
                
        # الأزرار
        self.add_button("إلغاء", self.reject, "default")
        self.add_button("حفظ", self.save_year, "primary")

        if self.year:
            self.load_data()
    
    def load_data(self):
        if not self.year:
            return
        self.gregorian_input.setText(self.year['year_name_gregorian'])
        self.hijri_input.setText(self.year['year_name_hijri'])
        sd = self.year.get('start_date', '')
        ed = self.year.get('end_date', '')
        if sd:
            d = date.fromisoformat(sd)
            self.start_date.setDate(QDate(d.year, d.month, d.day))
        if ed:
            d = date.fromisoformat(ed)
            self.end_date.setDate(QDate(d.year, d.month, d.day))
            
    def save_year(self):
        if not self.gregorian_input.text().strip():
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال السنة الميلادية")
            return
        try:
            sd = self.start_date.date()
            ed = self.end_date.date()
            payload = {
                'year_name_gregorian': self.gregorian_input.text().strip(),
                'year_name_hijri': self.hijri_input.text().strip(),
                'start_date': date(sd.year(), sd.month(), sd.day()).isoformat(),
                'end_date': date(ed.year(), ed.month(), ed.day()).isoformat(),
            }
            if AcademicFactory.is_remote():
                service = AcademicFactory.get_service()
                if self.year:
                    service.update_year(self.year['id'], payload)
                else:
                    service.create_year(payload)
            else:
                self._save_local(payload)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل الحفظ: {e}")

    def _save_local(self, payload):
        from app.database.session import session_scope
        from app.database.models import AcademicYear
        with session_scope() as session:
            if self.year:
                y = session.get(AcademicYear, self.year['id'])
            else:
                y = AcademicYear()
                session.add(y)
                y.is_current = False
                y.status = 'upcoming'
                y.is_closed = False
            y.year_name_gregorian = payload['year_name_gregorian']
            y.year_name_hijri = payload['year_name_hijri']
            y.start_date = date.fromisoformat(payload['start_date'])
            y.end_date = date.fromisoformat(payload['end_date'])