"""
النوافذ المنبثقة المخصصة - تصميم عصري فاخر.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Optional, List, Dict
import qtawesome as qta

from .custom_widgets import GradientButton, IconButton, QDateEditEN, QSpinBoxEN


class ModernDialog(QDialog):
    """نافذة منبثقة أساسية بتصميم عصري."""
    
    def __init__(self, title: str, icon=None, parent=None, width: int = 500, height: int = 400):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # الحاوية الرئيسية
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # بطاقة الحوار
        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setStyleSheet("""
            QFrame#card {
                background: white;
                border-radius: 16px;
                border: 1px solid #E2E8F0;
                padding: 0;
            }
        """)
        self.main_layout.addWidget(self.card)
        
        # تخطيط البطاقة
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setSpacing(0)
        
        # رأس النافذة
        self.header = self._create_header(title, icon)
        self.card_layout.addWidget(self.header)
        
        # منطقة المحتوى
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(25, 15, 25, 15)
        self.content_layout.setSpacing(10)
        self.card_layout.addWidget(self.content_widget)
        
        # منطقة الأزرار
        self.button_widget = QWidget()
        self.button_layout = QHBoxLayout(self.button_widget)
        self.button_layout.setContentsMargins(25, 0, 25, 20)
        self.button_layout.setSpacing(10)
        self.card_layout.addWidget(self.button_widget)
        
        # تأثير الظل
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.card.setGraphicsEffect(shadow)
        
        self._drag_pos = None
    
    def _create_header(self, title: str, icon: str) -> QWidget:
        """إنشاء رأس النافذة."""
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #1976D3, stop:1 #42A5F5);
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }
            QLabel, IconButton {
                background: transparent;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(15, 0, 15, 0)

        # أيقونة
        if icon != None:
            icon_label = QLabel()
            icon_label.setPixmap(qta.icon(icon, color='white').pixmap(20, 20))
            layout.addWidget(icon_label)
        
        # عنوان
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: 700;
            background: transparent;
        """)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # زر إغلاق
        close_btn = IconButton('fa5s.times', "إغلاق", color='white', size=30)
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 0;
                border-radius: 15px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
            }
        """)
        layout.addWidget(close_btn)
        
        return header
    
    def add_widget(self, widget: QWidget):
        """إضافة عنصر إلى منطقة المحتوى."""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout: QLayout):
        """إضافة تخطيط إلى منطقة المحتوى."""
        self.content_layout.addLayout(layout)
    
    def add_button(self, text: str, callback=None, style: str = "primary"):
        """إضافة زر إلى منطقة الأزرار."""
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(35)
        # btn.setMinimumWidth(100)
        
        if style == "primary":
            btn.setObjectName("primaryButton")
        elif style == "danger":
            btn.setObjectName("dangerButton")
        elif style == "success":
            btn.setObjectName("successButton")
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background: #F1F5F9;
                    border: none;
                    color: #0F172A;
                    font-weight: 500;
                    padding: 8px 20px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background: #E2E8F0;
                }
            """)
        
        if callback:
            btn.clicked.connect(callback)
        
        self.button_layout.addWidget(btn)
    
    def mousePressEvent(self, event):
        """بدء سحب النافذة."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """سحب النافذة."""
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """إنهاء السحب."""
        self._drag_pos = None
        event.accept()


class ConfirmationDialog(ModernDialog):
    """نافذة تأكيد."""
    
    def __init__(self, title: str, message: str, parent=None, icon=None):
        super().__init__(title, icon, parent, width=400, height=200)
        
        # أيقونة تحذير
        icon_layout = QHBoxLayout()
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        warning_icon = QLabel()
        warning_icon.setPixmap(qta.icon('fa5s.exclamation-triangle', color='#F59E0B').pixmap(40, 40))
        warning_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(warning_icon)
        
        self.add_layout(icon_layout)
        
        # الرسالة
        msg_label = QLabel(message)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("""
            color: #0F172A;
            font-size: 13px;
            font-weight: 500;
            line-height: 1.5;
        """)
        self.add_widget(msg_label)
        
        # الأزرار
        self.add_button("إلغاء", self.reject, "default")
        self.add_button("تأكيد", self.accept, "primary")


class SuccessDialog(ModernDialog):
    """نافذة نجاح."""
    
    def __init__(self, title: str, message: str, parent=None, icon=None):
        super().__init__(title, icon, parent, width=400, height=200)
        
        # أيقونة نجاح
        icon_layout = QHBoxLayout()
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        success_icon = QLabel()
        success_icon.setPixmap(qta.icon('fa5s.check-circle', color='#10B981').pixmap(50, 50))
        success_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(success_icon)
        
        self.add_layout(icon_layout)
        
        # الرسالة
        msg_label = QLabel(message)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("""
            color: #0F172A;
            font-size: 14px;
            font-weight: 600;
        """)
        self.add_widget(msg_label)
        
        # زر موافق
        self.add_button("موافق", self.accept, "success")


class ErrorDialog(ModernDialog):
    """نافذة خطأ."""
    
    def __init__(self, title: str, message: str, parent=None, icon=None):
        super().__init__(title, icon, parent, width=400, height=200)
        
        # أيقونة خطأ
        icon_layout = QHBoxLayout()
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        error_icon = QLabel()
        error_icon.setPixmap(qta.icon('fa5s.times-circle', color='#EF4444').pixmap(50, 50))
        error_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(error_icon)
        
        self.add_layout(icon_layout)
        
        # الرسالة
        msg_label = QLabel(message)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("""
            color: #0F172A;
            font-size: 13px;
            font-weight: 500;
        """)
        self.add_widget(msg_label)
        
        # زر موافق
        self.add_button("موافق", self.accept, "danger")


class InputDialog(ModernDialog):
    """نافذة إدخال."""
    
    def __init__(self, title: str, fields: List[Dict], parent=None, icon=None):
        super().__init__(title, icon, parent, width=450, height=300)
        
        self.inputs = {}
        
        for field in fields:
            label = QLabel(field.get('label', ''))
            label.setStyleSheet("color: #475569; font-weight: 500;")
            self.add_widget(label)
            
            if field.get('type') == 'text':
                input_widget = QLineEdit()
                input_widget.setPlaceholderText(field.get('placeholder', ''))
                if field.get('default'):
                    input_widget.setText(str(field['default']))
            elif field.get('type') == 'password':
                input_widget = QLineEdit()
                input_widget.setEchoMode(QLineEdit.EchoMode.Password)
                input_widget.setPlaceholderText(field.get('placeholder', ''))
            elif field.get('type') == 'number':
                input_widget = QSpinBoxEN(field.get('min', 0), field.get('max', 9999999999))
                if field.get('default'):
                    input_widget.setValue(int(field['default']))
            elif field.get('type') == 'combo':
                input_widget = QComboBox()
                input_widget.addItems(field.get('options', []))
            elif field.get('type') == 'textarea':
                input_widget = QTextEdit()
                input_widget.setMaximumHeight(80)
            elif field.get('type') == 'date':
                input_widget = QDateEditEN()
            else:
                input_widget = QLineEdit()
            
            self.inputs[field.get('key', field.get('label', ''))] = input_widget
            self.add_widget(input_widget)
        
        self.add_button("إلغاء", self.reject, "default")
        self.add_button("حفظ", self.accept, "primary")
    
    def get_values(self) -> Dict:
        """الحصول على قيم الإدخال."""
        values = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                values[key] = widget.text()
            elif isinstance(widget, QSpinBox):
                values[key] = widget.value()
            elif isinstance(widget, QComboBox):
                values[key] = widget.currentText()
            elif isinstance(widget, QTextEdit):
                values[key] = widget.toPlainText()
            elif isinstance(widget, QDateEdit):
                values[key] = widget.date().toString("yyyy-MM-dd")
        return values


class ProgressDialog(ModernDialog):
    """نافذة تقدم."""
    
    def __init__(self, title: str, message: str, parent=None, icon=None):
        super().__init__(title, icon, parent, width=400, height=150)
        
        # الرسالة
        msg_label = QLabel(message)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setStyleSheet("color: #0F172A; font-size: 13px; font-weight: 500;")
        self.add_widget(msg_label)
        
        # شريط التقدم
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # وضع غير محدد
        self.progress.setMinimumHeight(8)
        self.add_widget(self.progress)
    
    def set_progress(self, value: int, maximum: int = 100):
        """تحديد قيمة التقدم."""
        self.progress.setRange(0, maximum)
        self.progress.setValue(value)