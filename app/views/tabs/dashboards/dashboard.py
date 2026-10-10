"""
لوحة التحكم الرئيسية - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Dict, Optional
import qtawesome as qta
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.database.models.finance import StudentFee
from app.database.session import session_scope
from app.database.models import (
    Student, Receipt, ExpenseVoucher, PayrollRecord,
    DailyAttendance, Grade, Section, Notification
)
from app.services.dashboard_factory import DashboardFactory
from app.views.widgets.custom_widgets import (
    KPICard, Card, PageHeader, Badge, AvatarLabel
)
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload


class DashboardPage(QWidget):
    """صفحة لوحة التحكم الرئيسية - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        
        # ✅ تخزين القيم آمنة قبل فقدان الجلسة
        self.user_display_name = self._get_user_display_name()
        self.year_display_name = self._get_year_display_name()
        
        # إعداد الواجهة
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل البيانات في الخلفية
        QTimer.singleShot(100, self.load_data)
    
    def _get_user_display_name(self) -> str:
        """الحصول على اسم المستخدم بشكل آمن."""
        try:
            if self.user and hasattr(self.user, 'display_name'):
                return self.user.display_name
        except Exception:
            pass
        try:
            return self.user.username if self.user else "المستخدم"
        except Exception:
            return "المستخدم"
    
    def _get_year_display_name(self) -> str:
        """الحصول على اسم السنة الدراسية بشكل آمن."""
        try:
            if self.academic_year and hasattr(self.academic_year, 'display_name'):
                return self.academic_year.display_name
        except Exception:
            pass
        try:
            return self.academic_year.year_name_gregorian if self.academic_year else ""
        except Exception:
            return ""
    
    def setup_ui(self):
        """إعداد واجهة لوحة التحكم."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)

        title = QLabel("لوحة التحكم")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        subtitle = QLabel(f"مرحباً {self.user_display_name} - {self.year_display_name}")
        subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(subtitle)

        # منطقة التمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)
        
        # بطاقات KPI
        kpi_section = self._create_kpi_section()
        scroll_layout.addWidget(kpi_section)
        
        # الرسوم البيانية
        charts_section = self._create_charts_section()
        scroll_layout.addWidget(charts_section)
        
        # الجداول والإشعارات
        bottom_section = self._create_bottom_section()
        scroll_layout.addWidget(bottom_section)
        
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
    
    def _create_kpi_section(self) -> QWidget:
        """إنشاء قسم بطاقات KPI."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        
        layout = QGridLayout(widget)
        layout.setSpacing(20)
        
        self.students_card = KPICard(
            "إجمالي الطلاب", "0", "fa5s.user-graduate", "#1976D3", "+5% هذا الشهر"
        )
        layout.addWidget(self.students_card, 0, 0)
        
        self.attendance_card = KPICard(
            "نسبة الحضور اليومي", "0%", "fa5s.clipboard-check", "#10B981", "محدث تلقائياً"
        )
        layout.addWidget(self.attendance_card, 0, 1)
        
        self.revenue_card = KPICard(
            "المبالغ المحصلة اليوم", "0 ر.ي", "fa5s.money-bill-wave", "#F59E0B", "سندات قبض اليوم"
        )
        layout.addWidget(self.revenue_card, 0, 2)
        
        self.debt_card = KPICard(
            "إجمالي المتبقي", "0 ر.ي", "fa5s.hand-holding-usd", "#EF4444", "الديون المستحقة"
        )
        layout.addWidget(self.debt_card, 0, 3)
        
        return widget
    
    def _create_charts_section(self) -> QWidget:
        """إنشاء قسم الرسوم البيانية."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(widget)
        layout.setSpacing(20)
        
        # رسم بياني للتحصيل المالي
        financial_card = Card("التحصيل المالي الشهري")
        financial_card.setObjectName("financialCard")
        financial_card.setStyleSheet("""
            Card#financialCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 10px 15px;
            }
        """)
        self.financial_chart = BarChartWidget()
        financial_card.add_widget(self.financial_chart)
        layout.addWidget(financial_card)
        
        return widget
    
    def _create_bottom_section(self) -> QWidget:
        """إنشاء القسم السفلي."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(widget)
        layout.setSpacing(20)
        
        # رسم بياني لتوزيع الطلاب
        distribution_card = Card("توزيع الطلاب حسب الصفوف")
        distribution_card.setObjectName("distributionCard")
        distribution_card.setStyleSheet("""
            Card#distributionCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 0px 15px 10px 15px;
            }
        """)        
        self.distribution_chart = PieChartWidget()
        distribution_card.add_widget(self.distribution_chart)
        layout.addWidget(distribution_card, 4)

        # آخر الإشعارات
        notifications_card = Card("آخر الإشعارات")
        notifications_card.setObjectName("notificationsCard")
        notifications_card.setStyleSheet("""
            Card#notificationsCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 10px 15px;
            }
        """)
        self.notifications_list = QListWidget()
        self.notifications_list.setStyleSheet("""
            QListWidget {
                border: none;
                background: transparent;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #F1F5F9;
            }
            QListWidget::item:hover {
                background: #F8FAFC;
            }
        """)
        notifications_card.add_widget(self.notifications_list)
        layout.addWidget(notifications_card, 3)
        
        return widget
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_data(self):
        """تحميل البيانات - Local أو Remote."""
        self.loading_overlay.show_loading("جاري تحميل البيانات...")

        academic_year_id = (
            self.academic_year.id if self.academic_year else None
        )

        def _fetch_data():
            """جلب البيانات."""
            if DashboardFactory.is_remote():
                # ✅ Remote
                service = DashboardFactory.get_service()
                data = service.summary(academic_year_id)

                # تحويل grades_data من [{'name': .., 'count': ..}]
                #   إلى [(name, count), ...]
                grades_data = [
                    (g['name'], g['count'])
                    for g in data.get('grades_data', [])
                ]

                return {
                    'total_students': data.get('total_students', 0),
                    'attendance_rate': data.get('attendance_rate', 0),
                    'today_revenue': data.get('today_revenue', 0),
                    'remaining': data.get('remaining', 0),
                    'months_data': data.get('months_data', []),
                    'months_labels': data.get('months_labels', []),
                    'grades_data': grades_data,
                    'notifications': data.get('notifications', []),
                }
            else:
                # ✅ Local (الكود القديم - مُصغّر)
                from app.database.session import session_scope
                from app.database.models import (
                    Student, Receipt, DailyAttendance, Grade,
                    Notification, StudentFee,
                )
                from sqlalchemy import select, func
                from decimal import Decimal
                from datetime import date, datetime, timedelta

                today = date.today()

                with session_scope() as session:
                    total_students = session.execute(
                        select(func.count(Student.id)).where(
                            Student.academic_year_id == academic_year_id,
                            Student.status == 'مستمر',
                        )
                    ).scalar() or 0

                    total_attendance = session.execute(
                        select(func.count(DailyAttendance.id)).where(
                            DailyAttendance.attendance_date == today,
                            DailyAttendance.academic_year_id == academic_year_id,
                        )
                    ).scalar() or 0

                    present_count = session.execute(
                        select(func.count(DailyAttendance.id)).where(
                            DailyAttendance.attendance_date == today,
                            DailyAttendance.status == 'حاضر',
                            DailyAttendance.academic_year_id == academic_year_id,
                        )
                    ).scalar() or 0

                    attendance_rate = (
                        (present_count / total_attendance * 100)
                        if total_attendance > 0 else 0
                    )

                    today_start = datetime.combine(today, datetime.min.time())
                    today_revenue = session.execute(
                        select(func.sum(Receipt.amount_paid)).where(
                            Receipt.payment_date >= today_start,
                            Receipt.status == 'نشط',
                        )
                    ).scalar() or Decimal('0.00')

                    total_fees = session.execute(
                        select(func.sum(StudentFee.net_total_required)).where(
                            StudentFee.academic_year_id == academic_year_id,
                        )
                    ).scalar() or Decimal('0.00')

                    total_paid = session.execute(
                        select(func.sum(Receipt.amount_paid)).where(
                            Receipt.status == 'نشط',
                        )
                    ).scalar() or Decimal('0.00')

                    remaining = float(total_fees) - float(total_paid)

                    ARABIC_MONTHS = {
                        1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
                        5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
                        9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر",
                    }

                    months_data = []
                    months_labels = []
                    for i in range(5, -1, -1):
                        month_date = today.replace(day=1) - timedelta(days=30 * i)
                        month_start = datetime.combine(
                            month_date, datetime.min.time()
                        )
                        next_month = (
                            month_date.replace(day=28) + timedelta(days=4)
                        ).replace(day=1)
                        month_end = datetime.combine(
                            next_month, datetime.min.time()
                        )
                        revenue = session.execute(
                            select(func.sum(Receipt.amount_paid)).where(
                                Receipt.payment_date >= month_start,
                                Receipt.payment_date < month_end,
                                Receipt.status == 'نشط',
                            )
                        ).scalar() or Decimal('0.00')
                        months_data.append(float(revenue))
                        months_labels.append(ARABIC_MONTHS[month_date.month])

                    grades_data = []
                    grades = session.execute(
                        select(Grade).order_by(Grade.grade_name)
                    ).scalars().all()
                    for grade in grades:
                        count = session.execute(
                            select(func.count(Student.id)).where(
                                Student.grade_id == grade.id,
                                Student.academic_year_id == academic_year_id,
                                Student.status == 'مستمر',
                            )
                        ).scalar() or 0
                        if count > 0:
                            grades_data.append((grade.grade_name, count))

                    notifications = session.execute(
                        select(Notification)
                        .order_by(Notification.created_at.desc())
                        .limit(10)
                    ).scalars().all()

                    notifications_data = [
                        {
                            'type': n.notification_type or 'عام',
                            'title': n.title or '',
                            'created_at': (
                                n.created_at.strftime("%Y/%m/%d %H:%M")
                                if n.created_at else ''
                            ),
                        }
                        for n in notifications
                    ]

                    return {
                        'total_students': total_students,
                        'attendance_rate': attendance_rate,
                        'today_revenue': today_revenue,
                        'remaining': remaining,
                        'months_data': months_data,
                        'months_labels': months_labels,
                        'grades_data': grades_data,
                        'notifications': notifications_data,
                    }

        def _on_result(data):
            try:
                self.students_card.findChild(QLabel, "kpiValue").setText(
                    str(data['total_students'])
                )
                self.attendance_card.findChild(QLabel, "kpiValue").setText(
                    f"{data['attendance_rate']:.1f}%"
                )
                self.revenue_card.findChild(QLabel, "kpiValue").setText(
                    f"{data['today_revenue']:,.0f} ر.ي"
                )
                self.debt_card.findChild(QLabel, "kpiValue").setText(
                    f"{data['remaining']:,.0f} ر.ي"
                )

                self.financial_chart.set_data(
                    data['months_data'], data['months_labels']
                )
                self.distribution_chart.set_data(data['grades_data'])
                self._display_notifications(data['notifications'])
            except Exception as e:
                print(f"خطأ في تحديث الواجهة: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(
                self, "خطأ",
                f"فشل تحميل بيانات لوحة التحكم:\n{error_msg}"
            )

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
        
    def _display_notifications(self, notifications_data: List[Dict]):
        """عرض الإشعارات في القائمة."""
        self.notifications_list.clear()
        
        if not notifications_data:
            # عرض رسالة "لا توجد إشعارات"
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 50))
            
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(5, 5, 5, 5)
            
            empty_label = QLabel("لا توجد إشعارات حالياً")
            empty_label.setStyleSheet(
                "color: #94A3B8; font-size: 12px; font-style: italic;"
            )
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(empty_label)
            
            widget.setLayout(layout)
            self.notifications_list.setItemWidget(item, widget)
            return
        
        icon_map = {
            'حضور': ('fa5s.user-check', '#10B981'),
            'غياب': ('fa5s.user-times', '#EF4444'),
            'واجبات': ('fa5s.tasks', '#1976D3'),
            'سلوك': ('fa5s.exclamation-triangle', '#F59E0B'),
            'نتائج': ('fa5s.graduation-cap', '#42A5F5'),
            'رسوم': ('fa5s.money-bill', '#10B981'),
            'عام': ('fa5s.bullhorn', '#64748B'),
        }
        
        for notification in notifications_data:
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 50))
            
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(5, 5, 5, 5)
            
            # أيقونة حسب النوع
            icon_name, icon_color = icon_map.get(
                notification['type'],
                ('fa5s.bell', '#64748B')
            )
            icon_label = QLabel()
            icon_label.setPixmap(
                qta.icon(icon_name, color=icon_color).pixmap(20, 20)
            )
            layout.addWidget(icon_label)
            
            # النص
            text_layout = QVBoxLayout()
            title = QLabel(notification['title'])
            title.setStyleSheet(
                "font-weight: 600; color: #0F172A; font-size: 12px;"
            )
            text_layout.addWidget(title)
            
            time_label = QLabel(notification['created_at'])
            time_label.setStyleSheet("color: #94A3B8; font-size: 10px;")
            text_layout.addWidget(time_label)
            
            layout.addLayout(text_layout)
            layout.addStretch()
            
            widget.setLayout(layout)
            self.notifications_list.setItemWidget(item, widget)
    
    def resizeEvent(self, event):
        """تحديث حجم طبقة التحميل."""
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())
    
    def refresh(self):
        """إعادة تحميل البيانات (يمكن استدعاؤها من الخارج)."""
        self.load_data()


# ============================================================
# الرسوم البيانية (بدون تغيير)
# ============================================================

class BarChartWidget(QWidget):
    """رسم بياني شريطي مخصص."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.labels = []
        self.setMinimumHeight(250)
    
    def set_data(self, data: List[float], labels: List[str]):
        """تحديد البيانات."""
        self.data = data
        self.labels = labels
        self.update()
    
    def paintEvent(self, event):
        """رسم الرسم البياني."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if not self.data:
            painter.setPen(QColor('#CBD5E1'))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "لا توجد بيانات"
            )
            return
        
        width = self.width()
        height = self.height()
        bar_width = width / (len(self.data) * 2)
        max_value = max(self.data) if max(self.data) > 0 else 1
        
        for i, value in enumerate(self.data):
            x = i * bar_width * 2 + bar_width / 2
            bar_height = (value / max_value) * (height - 60)
            y = height - bar_height - 30
            
            gradient = QLinearGradient(x, y, x, height - 30)
            gradient.setColorAt(0, QColor('#1976D3'))
            gradient.setColorAt(1, QColor('#42A5F5'))
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            
            rect = QRectF(x, y, bar_width, bar_height)
            painter.drawRoundedRect(rect, 5, 5)
            
            painter.setPen(QColor('#0F172A'))
            painter.drawText(
                QRectF(x - bar_width / 2, y - 20, bar_width * 2, 20),
                Qt.AlignmentFlag.AlignCenter,
                f"{value:,.0f}"
            )
            
            painter.setPen(QColor('#64748B'))
            painter.drawText(
                QRectF(x - bar_width / 2, height - 25, bar_width * 2, 20),
                Qt.AlignmentFlag.AlignCenter,
                self.labels[i] if i < len(self.labels) else ""
            )


class PieChartWidget(QWidget):
    """رسم بياني دائري مخصص."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.colors = [
            QColor('#1976D3'), QColor('#10B981'), QColor('#F59E0B'),
            QColor('#EF4444'), QColor('#42A5F5'), QColor('#06B6D4'),
            QColor('#EC4899'), QColor('#84CC16')
        ]
        self.setMinimumHeight(500)
    
    def set_data(self, data: List[tuple]):
        """تحديد البيانات [(label, value), ...]."""
        self.data = data
        self.update()
    
    def paintEvent(self, event):
        """رسم الرسم البياني الدائري."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if not self.data:
            painter.setPen(QColor('#CBD5E1'))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "لا توجد بيانات"
            )
            return
        
        total = sum(value for _, value in self.data)
        if total == 0:
            painter.setPen(QColor('#CBD5E1'))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "لا توجد بيانات"
            )
            return
        
        center_x = self.width() * 0.35
        center_y = self.height() / 2
        radius = min(self.width(), self.height()) * 0.3
        
        start_angle = 90
        
        for i, (label, value) in enumerate(self.data):
            span_angle = -360 * (value / total)
            color = self.colors[i % len(self.colors)]
            
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            
            painter.drawPie(
                QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2),
                int(start_angle * 16),
                int(span_angle * 16)
            )
            
            start_angle += span_angle
        
        legend_x = self.width() * 0.65
        legend_y = self.height() * 0.15
        
        for i, (label, value) in enumerate(self.data):
            color = self.colors[i % len(self.colors)]
            percentage = (value / total) * 100
            
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(int(legend_x), int(legend_y + i * 30), 15, 15)
            
            painter.setPen(QColor('#0F172A'))
            painter.drawText(
                QRectF(legend_x + 20, legend_y + i * 30 - 5, 150, 25),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                f"{label} ({percentage:.1f}%)"
            )