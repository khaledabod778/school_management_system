"""
المكونات المخصصة للنظام - تصميم عصري فاخر.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Optional, List
import qtawesome as qta


class GradientButton(QPushButton):
    """زر بتدرج لوني جميل."""
    
    def __init__(self, text: str = "", icon: str = None, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)
        self.setObjectName("primaryButton")
        
        if icon:
            self.setIcon(qta.icon(icon, color='white'))
            self.setIconSize(QSize(18, 18))
        
        # تأثير الظل
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(99, 102, 241, 100))
        self.setGraphicsEffect(shadow)
    
    def set_gradient(self, color1: str, color2: str):
        """تحديد ألوان التدرج."""
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {color1}, stop:1 {color2});
                border: none;
                color: white;
                font-weight: 600;
                padding: 10px 20px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {color1}, stop:1 {color2});
                opacity: 0.9;
            }}
        """)

class TapBarButton(QPushButton):
    def __init__(self, text: str = "", icon: str = None, parent=None):
        super().__init__(text, parent)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("primaryButton")

        if icon:
            self.setIcon(qta.icon(icon, color='white'))
            self.setIconSize(QSize(18, 18))
        # تأثير الظل
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(99, 102, 241, 100))
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet("""
            QPushButton {
                border-radius: 7px;
                padding: 8px 15px;
                font-size: 13px;
            }
        """) 

class IconButton(QPushButton):
    """زر أيقونة دائري."""
    
    def __init__(self, icon_name: str, toolTip: str = None, color: str = "#64748B", 
                 size: int = 38, parent=None):
        super().__init__(parent)
        self.setIcon(qta.icon(icon_name, color=color))
        self.setIconSize(QSize(size-15, size-15))
        self.setFixedSize(size, size)
        if toolTip:
            self.setToolTip(toolTip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                border-radius: 6px;
                padding: 3px 15px;
            }}
        """)


class KPICard(QFrame):
    """بطاقة مؤشر أداء رئيسي."""
    
    def __init__(self, title: str, value: str, icon: str, 
                 color: str, trend: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("kpiCard")

        self.setStyleSheet(f"""
            QFrame#kpiCard {{
                background: white;
                border-radius: 12px;
                padding: 5px ;
                border: 2px solid {color};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        
        # أيقونة
        icon_label = QLabel()
        icon_label.setObjectName("kpiIcon")
        icon_label.setPixmap(qta.icon(icon, color='white').pixmap(24, 24))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel#kpiIcon {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {color}, stop:1 {color});
                border-radius: 12px;
                padding: 10px;
            }}
        """)
        layout.addWidget(icon_label)
        
        # النص
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setObjectName("kpiLabel")
        title_label.setStyleSheet("color: #64748B; font-size: 14px; font-weight: 600;")
        text_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName("kpiValue")
        value_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 700;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_layout.addWidget(value_label)
        
        if trend:
            trend_label = QLabel(trend)
            trend_label.setObjectName("kpiTrend")
            trend_label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 600;")
            trend_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_layout.addWidget(trend_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()


class SearchBox(QLineEdit):
    """صندوق بحث أنيق."""
    
    def __init__(self, placeholder: str = "بحث...", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        # self.setMaximumWidth(300)
        
        # إضافة أيقونة البحث
        self.addAction(
            qta.icon('fa5s.search', color='#94A3B8'),
            QLineEdit.ActionPosition.LeadingPosition
        )
        
        # زر مسح
        self.clear_action = self.addAction(
            qta.icon('fa5s.times', color='#94A3B8'),
            QLineEdit.ActionPosition.TrailingPosition
        )
        self.clear_action.setVisible(False)
        self.clear_action.triggered.connect(self.clear)
        self.textChanged.connect(self._on_text_changed)
    
    def _on_text_changed(self, text: str):
        """إظهار/إخفاء زر المسح."""
        self.clear_action.setVisible(bool(text))


class ModernTable(QTableWidget):
    """جدول بتصميم عصري."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة الجدول."""
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setShowGrid(False)
        # self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(200)
    
    def set_columns(self, columns: List[str]):
        """تحديد أعمدة الجدول."""
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
    
    def add_row(self, data: List[str], row_color: str = None):
        """إضافة صف إلى الجدول."""
        row = self.rowCount()
        self.insertRow(row)
        
        for col, value in enumerate(data):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if row_color:
                item.setBackground(QColor(row_color))
            
            self.setItem(row, col, item)
    
    def clear_table(self):
        """مسح الجدول."""
        self.setRowCount(0)


class Card(QFrame):
    """بطاقة أنيقة."""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        # self.setObjectName("card")
        
        layout = QVBoxLayout(self)
        # layout.setContentsMargins(20, 20, 20, 20)
        # layout.setSpacing(15)
        
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("cardTitle")
            layout.addWidget(title_label)
        
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
    
    def add_widget(self, widget: QWidget):
        """إضافة عنصر إلى البطاقة."""
        self.content_layout.addWidget(widget)


class Badge(QLabel):
    """شارة ملونة."""
    
    def __init__(self, text: str, color: str = "#1976D3", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QLabel {{
                background: {color};
                color: white;
                border-radius: 12px;
                padding: 2px 10px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumWidth(60)


class AvatarLabel(QLabel):
    """صورة رمزية دائرية."""
    
    def __init__(self, text: str = "", size: int = 40, color: str = "#1976D3", parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {color}, stop:1 {color});
                color: white;
                border-radius: {size//2}px;
                font-size: {size//3}px;
                font-weight: 700;
            }}
        """)
        
        # استخراج الأحرف الأولى
        initials = self._get_initials(text)
        self.setText(initials)
    
    def _get_initials(self, text: str) -> str:
        """استخراج الأحرف الأولى من الاسم."""
        parts = text.split()
        if len(parts) >= 2:
            return parts[0][0] + parts[-1][0]
        elif len(parts) == 1 and parts[0]:
            return parts[0][0]
        return "؟"


class PageHeader(QWidget):
    """رأس الصفحة."""
    
    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("pageHeader")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")
        layout.addWidget(title_label)
        
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("pageSubtitle")
            layout.addWidget(subtitle_label)


class StatisticCard(QFrame):
    """بطاقة إحصائية مع رسم بياني مصغر."""
    
    def __init__(self, title: str, value: str, icon: str, 
                 color: str, sparkline_data: List[float] = None, parent=None):
        super().__init__(parent)
        self.setObjectName("kpiCard")
        self.setMinimumHeight(140)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # الصف العلوي: أيقونة + عنوان
        top_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon, color=color).pixmap(20, 20))
        top_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: #64748B; font-size: 11px; font-weight: 500;")
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        
        layout.addLayout(top_layout)
        
        # القيمة
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 26px; font-weight: 700;")
        layout.addWidget(value_label)
        
        # رسم بياني مصغر
        if sparkline_data:
            sparkline = SparklineWidget(sparkline_data, color)
            sparkline.setFixedHeight(30)
            layout.addWidget(sparkline)


class SparklineWidget(QWidget):
    """رسم بياني خطي مصغر."""
    
    def __init__(self, data: List[float], color: str, parent=None):
        super().__init__(parent)
        self.data = data
        self.color = QColor(color)
        self.setMinimumHeight(30)
    
    def paintEvent(self, event):
        """رسم الخط البياني."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if not self.data:
            return
        
        # حساب النقاط
        width = self.width()
        height = self.height()
        max_val = max(self.data) if max(self.data) > 0 else 1
        min_val = min(self.data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        points = []
        for i, val in enumerate(self.data):
            x = i * (width / (len(self.data) - 1)) if len(self.data) > 1 else 0
            y = height - ((val - min_val) / range_val) * (height - 10) - 5
            points.append(QPointF(x, y))
        
        # رسم الخط
        path = QPainterPath()
        path.moveTo(points[0])
        for point in points[1:]:
            path.lineTo(point)
        
        pen = QPen(self.color)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # رسم التعبئة
        fill_path = QPainterPath(path)
        fill_path.lineTo(points[-1].x(), height)
        fill_path.lineTo(points[0].x(), height)
        fill_path.closeSubpath()
        
        fill_color = QColor(self.color)
        fill_color.setAlpha(30)
        painter.fillPath(fill_path, fill_color)
        
        # رسم النقاط
        for point in points:
            painter.setBrush(self.color)
            painter.drawEllipse(point, 3, 3)

class QLineEditPlus(QLineEdit):
    """مربع نص بتصميم عصري."""
    
    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(35)

class QDoubleSpinBoxEN(QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 999999999999)
        self.setDecimals(2)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))

class QSpinBoxEN(QSpinBox):
    def __init__(self, min: int = None, max: int = None, parent=None):
        super().__init__(parent)
        if min & max:
            self.setRange(min, max)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))

class QDateEditEN(QDateEdit):
    def __init__(self, date: QDate = QDate.currentDate(), parent=None):
        super().__init__(parent)
        self.setDate(date)
        self.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.setDisplayFormat("dd/MM/yyyy")
        self.setCalendarPopup(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(35)
        calendar = QCalendarWidget(self)
        calendar.setLocale(QLocale(QLocale.Language.Arabic, QLocale.Country.Yemen))
        calendar.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )
        calendar.setGridVisible(True)
        calendar.setFirstDayOfWeek(Qt.DayOfWeek.Saturday)
        calendar.setFont(QFont("Tahoma", 10))
        self.setCalendarWidget(calendar)


