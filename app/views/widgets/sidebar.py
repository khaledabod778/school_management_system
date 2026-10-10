"""
الشريط الجانبي - نسخة كاملة مع قوائم منسدلة قابلة للطي (وضع الأكورديون).
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Dict, Optional
import qtawesome as qta

from app.views.widgets.custom_widgets import GradientButton


class SidebarButton(QPushButton):
    """زر القائمة الجانبية."""
    
    def __init__(self, text: str, icon: str, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(True)
        self.setMinimumHeight(40)
        # self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setIcon(qta.icon(icon, color='#94A3B8'))
        self.setIconSize(QSize(18, 18))
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #CBD5E1;
                text-align: center;
                padding: 10px 20px 10px 35px;
                font-size: 13px;
                font-weight: 500;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.05);
                color: white;
            }
            QPushButton:checked {
                background: qlineargradient(x1:1, y1:0, x2:1, y2:0, 
                    stop:0 #1976D3, stop:1 #42A5F5);
                color: white;
                font-weight: 600;
                border-right: 3px solid #1976D3;
            }
        """)


class CollapsibleSection(QWidget):
    """
    قسم قابل للطي والتوسيع (Collapsible Section).
    
    - العنوان بارز مع أيقونة في الوسط
    - السهم على اليسار
    """
    
    # إشارة تُرسل عند تغيير حالة القسم (مفتوح/مغلق)
    toggled = pyqtSignal(bool)
    
    # إشارة تُرسل عند الضغط على العنوان (قبل التبديل)
    header_clicked = pyqtSignal(object)
    
    def __init__(self, title: str, icon: str = "fa5s.folder", 
                 parent=None, expanded: bool = False):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        
        # حالة القسم (مفتوح أم مغلق)
        self._is_expanded = expanded
        self._title = title
        self._icon_name = icon
        
        # التخطيط الرئيسي
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # ===== زر العنوان (قابل للضغط) =====
        self.header_btn = QPushButton()
        self.header_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_btn.setMinimumHeight(35)
        self.header_btn.clicked.connect(self._on_header_clicked)
        
        # تخطيط داخل زر العنوان (سهم يسار + أيقونة + نص وسط)
        header_layout = QHBoxLayout(self.header_btn)
        header_layout.setContentsMargins(10, 5, 10, 5)
        header_layout.setSpacing(8)
        
        # سهم على اليسار
        self.arrow_label = QLabel()
        # self.arrow_label.setStyleSheet("background: transparent;")
        self.arrow_label.setFixedSize(14, 14)
        header_layout.addWidget(self.arrow_label)
        
        # أيقونة القسم
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(18, 18)
        header_layout.addWidget(self.icon_label)
        
        # النص (في الوسط)
        self.title_label = QLabel(title)
        # self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            color: #E2E8F0;
            font-size: 13px;
            font-weight: 700;
            background: transparent;
            padding: 0px 5px;
        """)
        header_layout.addWidget(self.title_label, 1)  # ← stretch = 1 للتوسيط
        
        # عنصر فارغ لموازنة السهم (في RTL)
        spacer = QLabel()
        spacer.setFixedSize(14, 14)
        spacer.setStyleSheet("background: transparent;")
        header_layout.addWidget(spacer)
        
        # ستايل زر العنوان
        self.header_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 6px;
                margin: 2px 5px;
            }
            QPushButton:hover {
                background-color: rgba(66, 165, 245, 0.15);
            }
            QPushButton:pressed {
                background-color: rgba(66, 165, 245, 0.25);
            }
        """)
        
        self.main_layout.addWidget(self.header_btn)
        
        # ===== حاوية الأزرار (قابلة للطي) =====
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        
        self.buttons_layout = QVBoxLayout(self.content_widget)
        self.buttons_layout.setContentsMargins(0, 0, 0, 5)
        self.buttons_layout.setSpacing(2)
        
        self.main_layout.addWidget(self.content_widget)
        
        # تحديث الأيقونات
        self._update_icons()
        
        # تعيين الحالة الأولية
        self.content_widget.setVisible(expanded)
    
    def _update_icons(self):
        """تحديث أيقونة السهم وأيقونة القسم."""
        # السهم
        if self._is_expanded:
            arrow_icon = qta.icon('fa5s.chevron-down', color='#42A5F5')
        else:
            arrow_icon = qta.icon('fa5s.chevron-left', color='#64748B')
        
        self.arrow_label.setPixmap(arrow_icon.pixmap(12, 12))
        
        # أيقونة القسم
        icon_color = '#42A5F5' if self._is_expanded else '#94A3B8'
        section_icon = qta.icon(self._icon_name, color=icon_color)
        self.icon_label.setPixmap(section_icon.pixmap(18, 18))
        
        # تحديث لون العنوان حسب الحالة
        if self._is_expanded:
            self.title_label.setStyleSheet("""
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 700;
                background: transparent;
                padding: 0px 5px;
            """)
        else:
            self.title_label.setStyleSheet("""
                color: #CBD5E1;
                font-size: 13px;
                font-weight: 700;
                background: transparent;
                padding: 0px 5px;
            """)
    
    def _on_header_clicked(self):
        """عند الضغط على العنوان."""
        # إرسال إشارة للشريط الجانبي لإغلاق الأقسام الأخرى
        self.header_clicked.emit(self)
        # تبديل الحالة
        self.toggle()
    
    def toggle(self):
        """تبديل حالة القسم (فتح/إغلاق)."""
        self._is_expanded = not self._is_expanded
        self.content_widget.setVisible(self._is_expanded)
        self._update_icons()
        self.toggled.emit(self._is_expanded)
    
    def expand(self):
        """فتح القسم."""
        if not self._is_expanded:
            self._is_expanded = True
            self.content_widget.setVisible(True)
            self._update_icons()
            self.toggled.emit(True)
    
    def collapse(self):
        """إغلاق القسم."""
        if self._is_expanded:
            self._is_expanded = False
            self.content_widget.setVisible(False)
            self._update_icons()
            self.toggled.emit(False)
    
    def is_expanded(self) -> bool:
        """هل القسم مفتوح؟"""
        return self._is_expanded
    
    def set_expanded(self, expanded: bool):
        """تعيين حالة القسم."""
        if expanded:
            self.expand()
        else:
            self.collapse()
    
    def add_button(self, text: str, icon: str) -> SidebarButton:
        """إضافة زر إلى القسم."""
        btn = SidebarButton(text, icon)
        self.buttons_layout.addWidget(btn)
        return btn
    
    def button_count(self) -> int:
        """عدد الأزرار في القسم."""
        return self.buttons_layout.count()
    
    def set_title(self, title: str):
        """تغيير عنوان القسم."""
        self._title = title
        self.title_label.setText(title)
    
    def get_title(self) -> str:
        """الحصول على عنوان القسم."""
        return self._title


class AnimatedSidebar(QWidget):
    """شريط جانبي مع قوائم منسدلة (وضع الأكورديون)."""
    
    # إشارة لتسجيل الخروج
    logout_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setMinimumWidth(250)
        self.setMaximumWidth(250)
        self.setStyleSheet("""
            QWidget#sidebar {
                background: #1E293B;
                border: none;
            }
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # الشعار
        self.logo_widget = self._create_logo()
        self.main_layout.addWidget(self.logo_widget)
        
        # منطقة التمرير
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: #0F172A;
                border: none;
            }
            QScrollBar:vertical {
                background: #0F172A;
                width: 6px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #334155;
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #475569;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(0, 5, 0, 5)
        self.scroll_layout.setSpacing(2)
        
        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)
        
        # معلومات المستخدم
        self.user_widget = self._create_user_info()
        self.main_layout.addWidget(self.user_widget)
        
        # تخزين
        self.buttons: Dict[str, SidebarButton] = {}
        self.sections: List[CollapsibleSection] = []
        
        # تخزين مراجع عناصر المستخدم
        self.user_name_label = None
        self.user_role_label = None
        
        # القسم المفتوح حالياً (وضع الأكورديون)
        self.current_section: Optional[CollapsibleSection] = None
        
        # منع إعادة الدخول عند التبديل التلقائي
        self._is_switching = False
    
    def _create_logo(self) -> QWidget:
        """إنشاء الشعار."""
        widget = QWidget()
        widget.setStyleSheet("background: #0F172A;")
        widget.setFixedHeight(70)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 5, 20, 5)
        layout.setSpacing(10)
        
        logo_icon = QLabel()
        logo_icon.setPixmap(qta.icon('fa5s.school', color='#42A5F5').pixmap(30, 30))
        logo_icon.setStyleSheet("background: transparent;")
        layout.addWidget(logo_icon)
        
        title = QLabel("نظام إدارة المدرسة")
        title.setStyleSheet("""
            color: white;
            font-size: 15px;
            font-weight: 700;
            background: transparent;
        """)
        layout.addWidget(title)
        layout.addStretch()
        
        return widget
    
    def _create_user_info(self) -> QWidget:
        """إنشاء معلومات المستخدم."""
        widget = QWidget()
        widget.setObjectName("widget")
        widget.setStyleSheet("""
            QWidget#Widget {
                background: #0F172A;
                border-top: 1px solid #334155;
            }
        """)
        widget.setFixedHeight(70)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        # # صف المستخدم
        # user_row = QHBoxLayout()
        # user_row.setSpacing(10)
        
        # avatar = QLabel("م")
        # avatar.setFixedSize(35, 35)
        # avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # avatar.setStyleSheet("""
        #     QLabel {
        #         background: #1976D3;
        #         color: white;
        #         border-radius: 17px;
        #         font-size: 14px;
        #         font-weight: 700;
        #     }
        # """)
        # user_row.addWidget(avatar)
        
        # معلومات المستخدم
        user_info = QVBoxLayout()
        user_info.setSpacing(2)
        
        self.user_name_label = QLabel("المستخدم")
        self.user_name_label.setStyleSheet(
            "color: white; font-size: 14px; font-weight: 600; background: transparent;"
        )
        user_info.addWidget(self.user_name_label)
        
        self.user_role_label = QLabel("مستخدم")
        self.user_role_label.setStyleSheet(
            "color: #94A3B8; font-size: 12px; background: transparent;"
        )
        user_info.addWidget(self.user_role_label)
        
        # user_row.addLayout(user_info)
        # user_row.addStretch()
        
        # layout.addLayout(user_row)
        layout.addLayout(user_info)
        
        # زر تسجيل الخروج
        # logout_row = QHBoxLayout()
        # logout_row.addStretch()
        
        self.logout_btn = GradientButton("تسجيل الخروج", 'fa5s.sign-out-alt')
        self.logout_btn.setMinimumHeight(30)
        self.logout_btn.setStyleSheet("padding: 5px 10px;")
        self.logout_btn.setObjectName("dangerButton")
        self.logout_btn.clicked.connect(self._on_logout_clicked)
        # logout_row.addWidget(self.logout_btn)
        
        layout.addWidget(self.logout_btn)
        
        return widget
    
    def _on_logout_clicked(self):
        """معالج الضغط على زر تسجيل الخروج."""
        self.logout_requested.emit()
    
    def set_user_info(self, name: str, role: str = ""):
        """تحديث معلومات المستخدم."""
        if self.user_name_label:
            self.user_name_label.setText(name)
        if self.user_role_label:
            self.user_role_label.setText(role or "مستخدم")
    
    def add_section(self, title: str, icon: str = "fa5s.folder", 
                    expanded: bool = False) -> CollapsibleSection:
        """
        إضافة قسم قابل للطي.
        
        Args:
            title: عنوان القسم
            icon: أيقونة القسم (FontAwesome)
            expanded: هل القسم مفتوح افتراضياً؟
        """
        section = CollapsibleSection(title, icon=icon, expanded=expanded)
        
        # ربط إشارة النقر على العنوان (لإغلاق الأقسام الأخرى)
        section.header_clicked.connect(self._on_section_header_clicked)
        
        # ربط إشارة الفتح/الإغلاق
        section.toggled.connect(
            lambda is_open, s=section: self._on_section_toggled(s, is_open)
        )
        
        self.scroll_layout.addWidget(section)
        self.sections.append(section)
        
        # إذا كان هذا القسم مفتوحاً، احفظه كالقسم الحالي
        if expanded:
            self.current_section = section
        
        return section
    
    def _on_section_header_clicked(self, clicked_section: CollapsibleSection):
        """عند الضغط على عنوان قسم، أغلق الأقسام الأخرى."""
        self._is_switching = True
        
        for section in self.sections:
            if section != clicked_section and section.is_expanded():
                section.collapse()
        
        self._is_switching = False
    
    def _on_section_toggled(self, section: CollapsibleSection, is_open: bool):
        """معالج عند فتح/إغلاق قسم."""
        if is_open:
            self.current_section = section
        elif self.current_section == section:
            self.current_section = None
    
    def add_button(self, section_title: str, text: str, icon: str, 
                   key: str = None) -> SidebarButton:
        """إضافة زر إلى قسم."""
        section = None
        for s in self.sections:
            if s.get_title() == section_title:
                section = s
                break
        
        if not section:
            section = self.add_section(section_title)
        
        btn = section.add_button(text, icon)
        key = key or text
        self.buttons[key] = btn
        return btn
    
    def set_active_button(self, key: str):
        """
        تفعيل زر وفتح القسم الذي يحتوي عليه تلقائياً
        مع إغلاق الأقسام الأخرى (وضع الأكورديون).
        """
        # العثور على الزر والقسم الذي يحتويه
        target_section = None
        
        for btn_key, btn in self.buttons.items():
            btn.setChecked(btn_key == key)
            
            if btn_key == key:
                # البحث عن القسم الذي يحتوي هذا الزر
                for section in self.sections:
                    if btn.parent() == section.content_widget:
                        target_section = section
                        break
        
        # فتح القسم المطلوب وإغلاق الباقي
        if target_section:
            self._is_switching = True
            
            for section in self.sections:
                if section == target_section:
                    section.expand()
                else:
                    section.collapse()
            
            self.current_section = target_section
            self._is_switching = False
    
    # def expand_all(self):
    #     """فتح جميع الأقسام."""
    #     for section in self.sections:
    #         section.expand()
    
    # def collapse_all(self):
    #     """إغلاق جميع الأقسام."""
    #     for section in self.sections:
    #         section.collapse()
    #     self.current_section = None
    
    # def get_section(self, title: str) -> Optional[CollapsibleSection]:
    #     """الحصول على قسم بالعنوان."""
    #     for section in self.sections:
    #         if section.get_title() == title:
    #             return section
    #     return None