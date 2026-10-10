"""
الشريط العلوي المخصص.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import qtawesome as qta

from app.views.tabs.academic.academic_years_page import AcademicYearsPage
from app.views.widgets.custom_widgets import GradientButton, IconButton, TapBarButton


class TopBar(QWidget):
    """شريط علوي مخصص مع تأثيرات."""

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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(60)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        
        # زر القائمة
        self.menu_btn = IconButton('fa5s.bars', "زر القائمة", 'white', 35)
        self.menu_btn.setObjectName("titleBarButton")
        self.menu_btn.setStyleSheet("padding: 0px;")
        layout.addWidget(self.menu_btn)

        add_student = TapBarButton("إضافة طالب", "fa5s.plus")
        add_student.clicked.connect(self.add_student_requested.emit)  # ← ربط الإشارة
        layout.addWidget(add_student)

        add_parent = TapBarButton("إضافة ولي أمر", "fa5s.plus")
        add_parent.clicked.connect(self.add_parent_requested.emit)  # ← ربط الإشارة
        layout.addWidget(add_parent)

        add_employee = TapBarButton("إضافة موظف", "fa5s.plus")
        add_employee.clicked.connect(self.add_employee_requested.emit)  # ← ربط الإشارة
        layout.addWidget(add_employee)

        add_receipt = TapBarButton("إضافة سند قبض", "fa5s.plus")
        add_receipt.clicked.connect(self.add_receipt_requested.emit)  # ← ربط الإشارة
        layout.addWidget(add_receipt)

        add_voucher = TapBarButton("إضافة سند صرف", "fa5s.plus")
        add_voucher.clicked.connect(self.add_voucher_requested.emit)  # ← ربط الإشارة
        layout.addWidget(add_voucher)

        add_allowance = TapBarButton("إضافة بدلات أو خصومات", "fa5s.plus")
        add_allowance.clicked.connect(self.add_allowance_requested.emit)  # ← ربط الإشارة
        layout.addWidget(add_allowance)

        add_loan = TapBarButton("إضافة سلفة مالية", "fa5s.plus")
        add_loan.clicked.connect(self.add_loan_requested.emit)  # ← ربط الإشارة
        layout.addWidget(add_loan)

        add_homework = TapBarButton("إضافة واجب", "fa5s.plus")
        add_homework.clicked.connect(self.add_homework_requested.emit)  # ← ربط الإشارة
        layout.addWidget(add_homework)

        add_behavior = TapBarButton("إضافة متابعة سلوكية", "fa5s.plus")
        add_behavior.clicked.connect(self.add_behavior_requested.emit)  # ← ربط الإشارة
        layout.addWidget(add_behavior)

        # # عنوان التطبيق
        # title = QLabel("نظام إدارة المدرسة")
        # title.setStyleSheet("""
        #     color: white;
        #     font-size: 14px;
        #     font-weight: 600;
        #     background: transparent;
        # """)
        # layout.addWidget(title)
        
        layout.addStretch()
        
        # زر البحث
        # search_btn = QPushButton()
        # search_btn.setObjectName("titleBarButton")
        # search_btn.setIcon(qta.icon('fa5s.search', color='white'))
        # search_btn.setIconSize(QSize(16, 16))
        # search_btn.setFixedSize(35, 35)
        # search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # search_btn.setStyleSheet("""
        #     QPushButton {
        #         background: transparent;
        #         border: none;
        #         border-radius: 8px;
        #     }
        #     QPushButton:hover {
        #         background: rgba(255, 255, 255, 0.15);
        #     }
        # """)
        # layout.addWidget(search_btn)
        
        # زر الإشعارات مع عداد
        self.notification_btn = IconButton('fa5s.bell', "الإشعارات", 'white', 35)
        self.notification_btn.setObjectName("titleBarButton")
        self.notification_btn.setStyleSheet("padding: 0px;")
        layout.addWidget(self.notification_btn)
        
        # # زر التصغير
        # min_btn = QPushButton()
        # min_btn.setIcon(qta.icon('fa5s.minus', color='white'))
        # min_btn.setIconSize(QSize(14, 14))
        # min_btn.setFixedSize(35, 35)
        # min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # min_btn.clicked.connect(parent.showMinimized if parent else None)
        # min_btn.setStyleSheet("""
        #     QPushButton {
        #         background: transparent;
        #         border: none;
        #         border-radius: 8px;
        #     }
        #     QPushButton:hover {
        #         background: rgba(255, 255, 255, 0.15);
        #     }
        # """)
        # layout.addWidget(min_btn)
        
        # # زر التكبير
        # max_btn = QPushButton()
        # max_btn.setIcon(qta.icon('fa5s.square', color='white'))
        # max_btn.setIconSize(QSize(12, 12))
        # max_btn.setFixedSize(35, 35)
        # max_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # max_btn.setStyleSheet("""
        #     QPushButton {
        #         background: transparent;
        #         border: none;
        #         border-radius: 8px;
        #     }
        #     QPushButton:hover {
        #         background: rgba(255, 255, 255, 0.15);
        #     }
        # """)
        # layout.addWidget(max_btn)
        
        # # زر الإغلاق
        # close_btn = QPushButton()
        # close_btn.setObjectName("closeButton")
        # close_btn.setIcon(qta.icon('fa5s.times', color='white'))
        # close_btn.setIconSize(QSize(14, 14))
        # close_btn.setFixedSize(35, 35)
        # close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # close_btn.clicked.connect(parent.close if parent else None)
        # close_btn.setStyleSheet("""
        #     QPushButton {
        #         background: transparent;
        #         border: none;
        #         border-radius: 8px;
        #     }
        #     QPushButton:hover {
        #         background: #EF4444;
        #     }
        # """)
        # layout.addWidget(close_btn)
        
        # تخزين المراجع
        self._drag_pos = None
    
    def mousePressEvent(self, event):
        """بدء سحب النافذة."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """سحب النافذة."""
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """إنهاء السحب."""
        self._drag_pos = None
        event.accept()
    
    def set_notification_count(self, count: int):
        """تحديد عدد الإشعارات."""
        if count > 0:
            self.notification_btn.setIcon(qta.icon('fa5s.bell', color='#F59E0B'))
            self.notification_btn.setToolTip(f"{count} إشعارات جديدة")
        else:
            self.notification_btn.setIcon(qta.icon('fa5s.bell', color='white'))