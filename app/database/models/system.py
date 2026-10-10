"""
نماذج النظام: التدقيق، الأرشيف، السجلات.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    DateTime, ForeignKey, Integer, Numeric, String, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .sync_mixin import SyncableMixin

class SystemAuditLog(Base, TimestampMixin):
    """سجل مراقبة وتدقيق عمليات النظام."""
    
    __tablename__ = "system_audit_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL")
    )
    module_name: Mapped[str] = mapped_column(String(50), nullable=False)
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    record_id: Mapped[Optional[int]] = mapped_column(Integer)
    old_values: Mapped[Optional[str]] = mapped_column(Text)
    new_values: Mapped[Optional[str]] = mapped_column(Text)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    device_name: Mapped[Optional[str]] = mapped_column(String(100))
    
    # العلاقات
    user: Mapped[Optional["User"]] = relationship()
    
    @property
    def display_operation(self) -> str:
        """عرض نوع العملية."""
        operations = {
            'create': 'إضافة',
            'update': 'تعديل',
            'delete': 'حذف',
            'login': 'تسجيل دخول',
            'logout': 'تسجيل خروج',
            'close': 'إغلاق',
            'cancel': 'إلغاء'
        }
        return operations.get(self.operation_type, self.operation_type)


class PrintArchive(Base, SyncableMixin, TimestampMixin):
    """أرشيف عمليات الطباعة."""
    
    __tablename__ = "print_archive"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    document_number: Mapped[Optional[str]] = mapped_column(String(100))
    related_record_id: Mapped[Optional[int]] = mapped_column(Integer)
    printed_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL")
    )
    printed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    
    # العلاقات
    printer: Mapped[Optional["User"]] = relationship()


class ImportExportLog(Base, SyncableMixin, TimestampMixin):
    """سجلات عمليات الاستيراد والتصدير."""
    
    __tablename__ = "import_export_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation_type: Mapped[str] = mapped_column(String(20), nullable=False)
    entity_name: Mapped[str] = mapped_column(String(50), nullable=False)
    file_name: Mapped[Optional[str]] = mapped_column(String(255))
    executed_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL")
    )
    executed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default='success', nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # العلاقات
    executor: Mapped[Optional["User"]] = relationship()


class AnnualClosingLog(Base, SyncableMixin, TimestampMixin):
    """سجل عمليات الإقفال السنوي اليدوي."""
    
    __tablename__ = "annual_closing_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id"), nullable=False
    )
    to_academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id"), nullable=False
    )
    total_students_promoted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_debts_carried_over: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00"), nullable=False
    )
    executed_by_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    execution_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # العلاقات
    from_year: Mapped["AcademicYear"] = relationship(foreign_keys=[from_academic_year_id])
    to_year: Mapped["AcademicYear"] = relationship(foreign_keys=[to_academic_year_id])
    executor: Mapped["User"] = relationship()


class BackupLog(Base, SyncableMixin, TimestampMixin):
    """سجل النسخ الاحتياطي والصيانة."""
    
    __tablename__ = "backup_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    created_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id")
    )
    
    # العلاقات
    creator: Mapped[Optional["User"]] = relationship()