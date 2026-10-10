"""
نماذج نظام المزامنة - Sync Queue, Conflicts, Metadata.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    DateTime, ForeignKey, Integer, String, Text, Boolean,
    UniqueConstraint, CheckConstraint, Index, JSON, func
)
from sqlalchemy.orm import Mapped, mapped_column
import uuid as uuid_lib

from .base import Base, TimestampMixin


class SyncQueue(Base, TimestampMixin):
    """
    طابور المزامنة - يسجل كل عملية تحتاج مزامنة.
    
    دورة حياة العملية:
    PENDING → PROCESSING → SYNCED (نجحت)
                       ↓
                     FAILED (فشلت) → PENDING (إعادة محاولة)
                       ↓
                   CONFLICT (تعارض)
    """
    
    __tablename__ = "sync_queue"
    __table_args__ = (
        CheckConstraint(
            "operation IN ('INSERT', 'UPDATE', 'DELETE')",
            name="ck_sync_queue_operation"
        ),
        CheckConstraint(
            "status IN ('pending', 'processing', 'synced', 'failed', 'conflict')",
            name="ck_sync_queue_status"
        ),
        CheckConstraint(
            "direction IN ('to_cloud', 'to_local')",
            name="ck_sync_queue_direction"
        ),
        Index('idx_sync_queue_status', 'status'),
        Index('idx_sync_queue_direction', 'direction'),
        Index('idx_sync_queue_entity', 'entity_type', 'entity_uuid'),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # معلومات العملية
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_uuid: Mapped[str] = mapped_column(String(36), nullable=False)
    entity_local_id: Mapped[Optional[int]] = mapped_column(Integer)
    operation: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # الاتجاه: من المحلي إلى السحابة أو العكس
    direction: Mapped[str] = mapped_column(String(20), default='to_cloud', nullable=False)
    
    # البيانات كـ JSON
    payload: Mapped[Optional[dict]] = mapped_column(JSON)
    old_payload: Mapped[Optional[dict]] = mapped_column(JSON)  # للـ UPDATE/DELETE
    
    # الحالة
    status: Mapped[str] = mapped_column(String(20), default='pending', nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    
    # معلومات الفشل
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    error_code: Mapped[Optional[str]] = mapped_column(String(50))
    
    # الأولوية (1 = عالية، 10 = منخفضة)
    priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    
    # التتبع الزمني
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # معرف التسجيل الأصلي (لمنع التسجيل المزدوج)
    source_instance_id: Mapped[Optional[str]] = mapped_column(String(50))
    
    # معلومات إضافية
    sync_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    @property
    def is_ready(self) -> bool:
        """هل العملية جاهزة للمعالجة؟"""
        if self.status != 'pending':
            return False
        
        if self.next_retry_at and self.next_retry_at > datetime.now():
            return False
        
        if self.attempts >= self.max_attempts:
            return False
        
        return True
    
    @property
    def age_seconds(self) -> float:
        """عمر العملية بالثواني."""
        if not self.created_at:
            return 0
        return (datetime.now() - self.created_at).total_seconds()


class SyncConflict(Base, TimestampMixin):
    """
    سجل التعارضات في المزامنة.
    
    عند حدوث تعارض، يُسجل هنا للمراجعة اليدوية أو الحل التلقائي.
    """
    
    __tablename__ = "sync_conflicts"
    __table_args__ = (
        CheckConstraint(
            "resolution_strategy IN ('local_wins', 'cloud_wins', 'merge', 'manual', 'pending')",
            name="ck_conflict_resolution_strategy"
        ),
        CheckConstraint(
            "status IN ('open', 'resolved', 'ignored')",
            name="ck_conflict_status"
        ),
        Index('idx_sync_conflict_status', 'status'),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # مرجع للعملية
    sync_queue_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sync_queue.id", ondelete="SET NULL")
    )
    
    # معلومات الكيان
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_uuid: Mapped[str] = mapped_column(String(36), nullable=False)
    
    # البيانات المتعارضة
    local_version: Mapped[Optional[dict]] = mapped_column(JSON)
    cloud_version: Mapped[Optional[dict]] = mapped_column(JSON)
    base_version: Mapped[Optional[dict]] = mapped_column(JSON)  # آخر نسخة متزامنة
    
    # الحل
    resolution_strategy: Mapped[str] = mapped_column(
        String(20), default='pending', nullable=False
    )
    resolved_data: Mapped[Optional[dict]] = mapped_column(JSON)
    resolved_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL")
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # الحالة
    status: Mapped[str] = mapped_column(String(20), default='open', nullable=False)
    
    # السبب
    conflict_reason: Mapped[Optional[str]] = mapped_column(Text)
    
    # أرقام النسخ للتوضيح
    local_version_number: Mapped[Optional[int]] = mapped_column(Integer)
    cloud_version_number: Mapped[Optional[int]] = mapped_column(Integer)
    
    @property
    def is_open(self) -> bool:
        return self.status == 'open'


class SyncMetadata(Base):
    """
    بيانات وصفية للمزامنة - تخزن معلومات عامة.
    
    مثال:
    - آخر وقت مزامنة لكل جدول
    - آخر UUID تم توليده
    - حالة الاتصال
    """
    
    __tablename__ = "sync_metadata"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[Optional[str]] = mapped_column(Text)
    value_json: Mapped[Optional[dict]] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    
    @classmethod
    def get(cls, session, key: str, default=None):
        """الحصول على قيمة."""
        record = session.query(cls).filter_by(key=key).first()
        if record:
            return record.value_json if record.value_json else record.value
        return default
    
    @classmethod
    def set(cls, session, key: str, value, as_json: bool = False):
        """تعيين قيمة."""
        record = session.query(cls).filter_by(key=key).first()
        if not record:
            record = cls(key=key)
            session.add(record)
        
        if as_json:
            record.value_json = value
            record.value = None
        else:
            record.value = str(value)
            record.value_json = None
        
        session.flush()
        return record


class SyncInstance(Base):
    """
    سجل النسخ (Instances) - كل نسخة من النظام لها معرف فريد.
    
    مفيد لمنع المزامنة مع النفس أو معالجة الحالات المتعددة.
    """
    
    __tablename__ = "sync_instances"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instance_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False,
        default=lambda: str(uuid_lib.uuid4())
    )
    instance_name: Mapped[str] = mapped_column(String(100), nullable=False)
    instance_type: Mapped[str] = mapped_column(
        String(20), default='local', nullable=False
    )  # local, cloud
    
    # معلومات الشبكة
    hostname: Mapped[Optional[str]] = mapped_column(String(100))
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    
    # الحالة
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # الإصدار
    app_version: Mapped[Optional[str]] = mapped_column(String(20))
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )