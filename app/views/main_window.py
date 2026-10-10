"""
النافذة الرئيسية - نسخة محدثة.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Optional, Dict
import qtawesome as qta

from app.core.config import config_manager
from app.database.models import User, AcademicYear
from app.views.widgets.sidebar import AnimatedSidebar
from app.views.widgets.top_bar import TopBar


class MainWindow(QMainWindow):
    """النافذة الرئيسية للتطبيق."""
    
    # إضافة إشارة لتسجيل الخروج
    logout_requested = pyqtSignal()
    # إشارات متعددة
    add_student_requested = pyqtSignal()
    add_parent_requested = pyqtSignal()
    add_employee_requested = pyqtSignal()
    add_receipt_requested = pyqtSignal()
    add_voucher_requested = pyqtSignal()
    add_allowance_requested = pyqtSignal()
    add_loan_requested = pyqtSignal()
    add_homework_requested = pyqtSignal()
    add_behavior_requested = pyqtSignal()
    
    def __init__(self, user: User, academic_year: AcademicYear):
        super().__init__()
        self.user = user
        self.academic_year = academic_year
        
        self.current_page: Optional[QWidget] = None
        self.pages: Dict[str, QWidget] = {}
        
        # اسم المستخدم
        self.user_display_name = user.username
        try:
            if user.employee and user.employee.full_name:
                self.user_display_name = user.employee.full_name
        except:
            pass
        
        # دور المستخدم
        self.user_role = ""
        try:
            if user.role:
                self.user_role = user.role.role_name
        except:
            pass
        
        self.academic_year_name = academic_year.year_name_gregorian
        
        self.setWindowTitle(f"{config_manager.app_config.app_name}")
        self.setMinimumSize(1200, 700)
        self.showMaximized()

        self.setup_ui()
        self.update_user_info()
    
    def setup_ui(self):
        """إعداد الواجهة الرئيسية."""
        main_widget = QWidget()
        main_widget.setObjectName("mainWidget")
        main_widget.setStyleSheet("""
            QWidget#mainWidget {
                background: #0F172A;
            }
        """)
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # الشريط العلوي
        self.top_bar = TopBar(self)
        # ✅ ربط إشارة الشريط العلوي بإشارة النافذة
        self.top_bar.add_student_requested.connect(self.add_student_requested.emit)
        self.top_bar.add_parent_requested.connect(self.add_parent_requested.emit)
        self.top_bar.add_employee_requested.connect(self.add_employee_requested.emit)
        self.top_bar.add_receipt_requested.connect(self.add_receipt_requested.emit)
        self.top_bar.add_voucher_requested.connect(self.add_voucher_requested.emit)
        self.top_bar.add_allowance_requested.connect(self.add_allowance_requested.emit)
        self.top_bar.add_loan_requested.connect(self.add_loan_requested.emit)
        self.top_bar.add_homework_requested.connect(self.add_homework_requested.emit)
        self.top_bar.add_behavior_requested.connect(self.add_behavior_requested.emit)

        self.top_bar.menu_btn.clicked.connect(self._toggle_sidebar)
        main_layout.addWidget(self.top_bar)
        
        # المحتوى
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # الشريط الجانبي
        self.sidebar = AnimatedSidebar()
        self.sidebar.setStyleSheet("""
            QWidget#sidebar {
                background: #1E293B;
                border: none;
                min-width: 250px;
                max-width: 250px;
            }
        """)
        
        # ربط إشارة تسجيل الخروج
        self.sidebar.logout_requested.connect(self._on_logout_requested)
        
        content_layout.addWidget(self.sidebar)
        
        # منطقة المحتوى
        self.content_area = QWidget()
        self.content_area.setObjectName("contentArea")
        self.content_area.setStyleSheet("""
            QWidget#contentArea {
                background: #F8FAFC;
            }
        """)
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        content_layout.addWidget(self.content_area, 1)
        
        main_layout.addWidget(content_widget)
        
        # شريط الحالة
        self.status_bar = self._create_status_bar()
        main_layout.addWidget(self.status_bar)
        
    def _create_status_bar(self) -> QWidget:
        """إنشاء شريط الحالة."""
        status_widget = QWidget()
        status_widget.setFixedHeight(30)
        status_widget.setStyleSheet("""
            QWidget {
                background: white;
                border-top: 1px solid #E2E8F0;
            }
        """)
        
        layout = QHBoxLayout(status_widget)
        layout.setContentsMargins(15, 0, 15, 0)
        
        self.status_user_label = QLabel()
        self.status_user_label.setStyleSheet("color: #64748B; font-size: 11px;")
        layout.addWidget(self.status_user_label)

        separator = QLabel("|")
        separator.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(separator)

        self.connection_indicator = QLabel()
        self.connection_indicator.setStyleSheet("color: #64748B; font-size: 11px;")
        layout.addWidget(self.connection_indicator)

        layout.addStretch()
        
        self.status_year_label = QLabel()
        self.status_year_label.setStyleSheet("color: #64748B; font-size: 11px;")
        layout.addWidget(self.status_year_label)
        
        separator2 = QLabel("|")
        separator2.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(separator2)
        
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("color: #64748B; font-size: 11px;")
        layout.addWidget(self.clock_label)
        
        timer = QTimer(self)
        timer.timeout.connect(self._update_clock)
        timer.start(1000)
        self._update_clock()
        
        return status_widget
    
    def _update_clock(self):
        """تحديث الساعة."""
        current = QDateTime.currentDateTime()
        self.clock_label.setText(current.toString("yyyy/MM/dd - hh:mm:ss"))
    
    def update_user_info(self):
        """تحديث معلومات المستخدم."""
        self.status_user_label.setText(f"المستخدم: {self.user_display_name}")
        self.status_year_label.setText(f"السنة: {self.academic_year_name}")
        
        # تحديث معلومات المستخدم في الشريط الجانبي
        if hasattr(self, 'sidebar'):
            self.sidebar.set_user_info(self.user_display_name, self.user_role)
    
    def _toggle_sidebar(self):
        """تبديل الشريط الجانبي."""
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()
    
    def _on_logout_requested(self):
        """معالج طلب تسجيل الخروج."""
        reply = QMessageBox.question(
            self,
            "تأكيد تسجيل الخروج",
            "هل أنت متأكد من رغبتك في تسجيل الخروج؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # إرسال إشارة تسجيل الخروج إلى التطبيق الرئيسي
            self.logout_requested.emit()
    
    def closeEvent(self, event):
        """عند إغلاق النافذة."""
        reply = QMessageBox.question(
            self,
            "تأكيد الخروج",
            "هل تريد الخروج من النظام؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()