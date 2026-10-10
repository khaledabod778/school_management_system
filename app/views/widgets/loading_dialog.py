"""
حوار تحميل بسيط مع شريط تقدم.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QGraphicsDropShadowEffect, QApplication, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QMovie
import qtawesome as qta


class LoadingDialog(QDialog):
    """حوار تحميل مع شريط تقدم متحرك."""
    
    def __init__(self, parent=None, title="جاري التحميل", 
                 message="الرجاء الانتظار..."):
        super().__init__(parent)
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedSize(380, 180)
        
        # توسيط في الشاشة
        if parent:
            parent_geo = parent.geometry()
            self.move(
                parent_geo.center().x() - self.width() // 2,
                parent_geo.center().y() - self.height() // 2
            )
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # الحاوية
        container = QFrame()
        container.setObjectName("loadingContainer")
        container.setStyleSheet("""
            QFrame#loadingContainer {
                background: white;
                border-radius: 16px;
            }
        """)
        
        # ظل
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(25, 25, 25, 25)
        container_layout.setSpacing(15)
        
        # العنوان مع أيقونة
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        
        icon_label = QLabel()
        icon_label.setPixmap(
            qta.icon('fa5s.spinner', color='#1976D3').pixmap(24, 24)
        )
        title_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #0F172A;
            font-size: 15px;
            font-weight: 700;
        """)
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        container_layout.addLayout(title_layout)
        
        # الرسالة
        self.message_label = QLabel(message)
        self.message_label.setStyleSheet("""
            color: #64748B;
            font-size: 12px;
        """)
        self.message_label.setWordWrap(True)
        container_layout.addWidget(self.message_label)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # indeterminate
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: #E2E8F0;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1976D3, stop:1 #42A5F5);
                border-radius: 3px;
            }
        """)
        container_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(container)
    
    def set_message(self, message: str):
        """تحديث الرسالة."""
        self.message_label.setText(message)
        QApplication.processEvents()
    
    def set_success(self):
        """تغيير الحوار ليعرض النجاح."""
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: #D1FAE5;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: #10B981;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        QApplication.processEvents()
    
    def paintEvent(self, event):
        """خلفية شبه شفافة."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))