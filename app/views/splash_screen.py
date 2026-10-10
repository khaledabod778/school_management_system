"""
شاشة البداية - مع ترتيب صحيح للتهيئة.
"""

from PyQt6.QtWidgets import (
    QSplashScreen, QWidget, QVBoxLayout, QLabel, 
    QProgressBar, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QPainter, QLinearGradient, QBrush
import qtawesome as qta


class SplashScreen(QSplashScreen):
    """شاشة بداية فاخرة - لا تُغلق عند النقر."""
    
    def __init__(self):
        # ✅ 1. super() أولاً (بـ pixmap مؤقت)
        super().__init__(QPixmap(1, 1))
        
        # ✅ 2. الآن أنشئ الصورة الحقيقية
        pixmap = QPixmap(600, 400)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        gradient = QLinearGradient(0, 0, 600, 400)
        gradient.setColorAt(0, QColor("#1976D3"))
        gradient.setColorAt(0.5, QColor("#1565C0"))
        gradient.setColorAt(1, QColor("#0D47A1"))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 600, 400, 20, 20)
        painter.end()
        
        # ✅ 3. تعيين الصورة
        self.setPixmap(pixmap)
        
        # ✅ 4. خصائص النافذة
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # ✅ 5. المحتوى
        self._setup_content()
    
    def _setup_content(self):
        """إعداد محتوى الشاشة."""
        content = QWidget(self)
        content.setGeometry(0, 0, 600, 400)
        content.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.addStretch()
        
        # أيقونة المدرسة
        icon_label = QLabel()
        icon_label.setPixmap(
            qta.icon('fa5s.school', color='white').pixmap(80, 80)
        )
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(icon_label)
        
        # اسم التطبيق
        title = QLabel("نظام إدارة المدرسة")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: white;
            font-size: 26px;
            font-weight: 800;
            background: transparent;
        """)
        layout.addWidget(title)
        
        subtitle = QLabel("نظام متكامل لإدارة المدارس")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            font-size: 13px;
            background: transparent;
        """)
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # نص الحالة
        self.status_label = QLabel("جاري تهيئة قاعدة البيانات...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: 600;
            background: transparent;
        """)
        layout.addWidget(self.status_label)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFFFFF, stop:1 #E0F2FE);
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        layout.addSpacing(10)
        
        from app.core.config import config_manager
        version_label = QLabel(
            f"الإصدار {config_manager.app_config.app_version}"
        )
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            font-size: 11px;
            background: transparent;
        """)
        layout.addWidget(version_label)
        
        layout.addStretch()
    
    def set_status(self, text: str, progress: int = None):
        """تحديث النص والتقدم."""
        self.status_label.setText(text)
        if progress is not None:
            self.progress_bar.setValue(progress)
        QApplication.processEvents()
    
    # ============================================================
    # ✅ منع إغلاق الشاشة عند النقر
    # ============================================================
    
    def mousePressEvent(self, event):
        """تجاهل النقر."""
        event.accept()
    
    def mouseReleaseEvent(self, event):
        """تجاهل رفع الزر."""
        event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """تجاهل النقر المزدوج."""
        event.accept()
    
    def keyPressEvent(self, event):
        """تجاهل ضغطات المفاتيح."""
        event.accept()