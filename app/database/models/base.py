"""
النموذج الأساسي المشترك لجميع النماذج في النظام.
يحتوي على الحقول المشتركة والوظائف المساعدة.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """الفئة الأساسية لجميع نماذج قاعدة البيانات."""
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل النموذج إلى قاموس."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def __repr__(self) -> str:
        """تمثيل نصي للنموذج."""
        if hasattr(self, 'id'):
            return f"<{self.__class__.__name__}(id={self.id})>"
        return f"<{self.__class__.__name__}>"


class TimestampMixin:
    """مزيج لإضافة حقول التوقيت للنماذج."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=func.now(),
        nullable=True
    )


class AuditMixin(TimestampMixin):
    """مزيج لإضافة حقول التدقيق للنماذج."""
    
    created_by_user_id: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="معرف المستخدم الذي أنشأ السجل"
    )
    last_modified_by_user_id: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="معرف المستخدم الذي عدل السجل آخر مرة"
    )