"""
نماذج الإشعارات والتنبيهات.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer, String, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .sync_mixin import SyncableMixin

from .base import Base, TimestampMixin


class Notification(Base, SyncableMixin, TimestampMixin):
    """جدول الإشعارات المرسلة."""
    
    __tablename__ = "notifications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    sender_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL")
    )
    target_type: Mapped[str] = mapped_column(
        String(30), default='all', nullable=False
    )
    target_grade_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("grades.id", ondelete="SET NULL")
    )
    target_section_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sections.id", ondelete="SET NULL")
    )
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # العلاقات
    sender: Mapped[Optional["User"]] = relationship()
    logs: Mapped[List["NotificationLog"]] = relationship(
        back_populates="notification", cascade="all, delete-orphan"
    )
    
    @property
    def is_sent(self) -> bool:
        """التحقق من إرسال الإشعار."""
        return self.sent_at is not None
    
    @property
    def is_scheduled(self) -> bool:
        """التحقق من كون الإشعار مجدولاً."""
        return self.scheduled_at is not None and self.sent_at is None
    
    @property
    def status_display(self) -> str:
        """عرض حالة الإشعار."""
        if self.is_sent:
            return "تم الإرسال"
        elif self.is_scheduled:
            return "مجدول"
        return "جديد"


class NotificationLog(Base, SyncableMixin, TimestampMixin):
    """سجل تسليم وقراءة الإشعارات."""
    
    __tablename__ = "notification_logs"
    __table_args__ = (
        # يمكن إضافة CheckConstraint هنا
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    notification_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    delivery_status: Mapped[str] = mapped_column(
        String(20), default='sent', nullable=False
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # العلاقات
    notification: Mapped["Notification"] = relationship(back_populates="logs")
    parent: Mapped["Parent"] = relationship(back_populates="notification_logs")
    
    @property
    def is_read(self) -> bool:
        """التحقق من قراءة الإشعار."""
        return self.read_at is not None
    
    @property
    def status_display(self) -> str:
        """عرض حالة التسليم."""
        status_map = {
            'sent': 'مرسل',
            'delivered': 'تم التسليم',
            'failed': 'فشل',
            'read': 'تمت القراءة'
        }
        return status_map.get(self.delivery_status, self.delivery_status)