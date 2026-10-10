"""
مؤشر تحميل بسيط.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, 
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter


class LoadingOverlay(QWidget):
    """طبقة تحميل شبه شفافة."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setVisible(False)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # صندوق مركزي
        container = QWidget()
        container.setFixedSize(320, 120)
        container.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 12px;
            }
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.setSpacing(15)
        
        # النص
        self.label = QLabel("جاري التحميل...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #0F172A;
            background: transparent;
        """)
        container_layout.addWidget(self.label)
        
        # شريط التقدم
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background: #E2E8F0;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #1976D3, stop:1 #1E88E5);
                border-radius: 3px;
            }
        """)
        container_layout.addWidget(self.progress)
        
        layout.addWidget(container)
        
        # ظل
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        container.setGraphicsEffect(shadow)
    
    def paintEvent(self, event):
        """خلفية شبه شفافة."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(15, 23, 42, 100))
    
    def show_loading(self, message: str = "جاري تحميل البيانات..."):
        """إظهار الطبقة."""
        self.label.setText(message)
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.raise_()
        self.setVisible(True)
    
    def hide_loading(self):
        """إخفاء الطبقة."""
        self.setVisible(False)
    
    def resizeEvent(self, event):
        """تحديث الحجم."""
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().resizeEvent(event)