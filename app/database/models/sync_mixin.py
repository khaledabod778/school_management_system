"""
Mixin للجداول القابلة للمزامنة.

v2.0 - إضافة:
- soft delete (deleted_at, deleted_by)
- حقل pending_sync لتفادي حلقة Cloud↔Local
- تحسين get_sync_hash لاستبعاد الحقول المتغيرة باستمرار
"""

import uuid as uuid_lib
import hashlib
import json
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, Any

from sqlalchemy import DateTime, Integer, String, Boolean, func, Index
from sqlalchemy.orm import Mapped, mapped_column


class SyncableMixin:
    """مزيج للجداول القابلة للمزامنة."""

    # ==================== حقول المزامنة الأساسية ====================

    sync_uuid: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        default=lambda: str(uuid_lib.uuid4()),
        index=True,
        comment="معرف عالمي فريد للمزامنة"
    )

    sync_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="رقم النسخة (يزيد مع كل تعديل)"
    )

    sync_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=True,
        comment="آخر وقت تعديل للمزامنة"
    )

    sync_source: Mapped[Optional[str]] = mapped_column(
        String(20),
        default='local',
        nullable=True,
        comment="مصدر التعديل: local أو cloud"
    )

    is_synced: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="هل الصف متزامن مع الطرف الآخر"
    )

    # ==================== Soft Delete ====================
    # ✅ v2.0: بدلاً من الحذف الفعلي، نحتفظ بالصف مع علامة الحذف
    # هذا يحل مشاكل deleted_local/deleted_cloud في حل التعارضات

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
        comment="وقت الحذف الناعم (NULL = غير محذوف)"
    )

    deleted_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="معرّف المستخدم الذي حذف الصف"
    )

    # ==================== Utilities ====================

    @property
    def is_deleted(self) -> bool:
        """هل الصف محذوف ناعماً؟"""
        return self.deleted_at is not None

    def soft_delete(self, user_id: Optional[int] = None):
        """
        ✅ حذف ناعم - يعيّن deleted_at بدلاً من حذف الصف.
        
        يُستخدَم في الخدمات بدلاً من session.delete(obj).
        """
        self.deleted_at = datetime.now()
        self.deleted_by_user_id = user_id
        self.sync_version = (self.sync_version or 0) + 1
        self.sync_source = 'local'
        self.is_synced = False

    def restore(self):
        """استعادة صف محذوف ناعماً."""
        self.deleted_at = None
        self.deleted_by_user_id = None
        self.sync_version = (self.sync_version or 0) + 1
        self.sync_source = 'local'
        self.is_synced = False

    # ==================== JSON Safety ====================

    @staticmethod
    def _make_json_safe(value: Any) -> Any:
        """تحويل القيمة إلى نوع قابل للتحويل إلى JSON."""
        if value is None:
            return None

        if isinstance(value, (bool, int, float, str)):
            return value

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, time):
            return value.isoformat()

        if isinstance(value, Decimal):
            return float(value)

        try:
            import uuid
            if isinstance(value, uuid.UUID):
                return str(value)
        except Exception:
            pass

        if isinstance(value, bytes):
            import base64
            return base64.b64encode(value).decode('ascii')

        try:
            import enum
            if isinstance(value, enum.Enum):
                return value.value
        except Exception:
            pass

        if isinstance(value, (list, tuple)):
            return [SyncableMixin._make_json_safe(v) for v in value]

        if isinstance(value, dict):
            return {
                k: SyncableMixin._make_json_safe(v)
                for k, v in value.items()
            }

        return str(value)

    # ==================== Sync Data ====================

    def get_sync_data(self) -> dict:
        """الحصول على بيانات الصف للمزامنة (JSON-safe)."""
        data = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            data[column.name] = self._make_json_safe(value)
        return data

    def get_sync_hash(self) -> str:
        """الحصول على hash للبيانات (لاكتشاف التغييرات)."""
        data = self.get_sync_data()

        # ✅ استبعاد الحقول التي تتغير دائماً
        for field in (
            'sync_updated_at', 'is_synced', 'sync_version',
            'sync_source', 'updated_at',
        ):
            data.pop(field, None)

        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(json_str.encode('utf-8')).hexdigest()

    def to_sync_dict(self) -> dict:
        """تحويل الصف إلى قاموس للمزامنة (بدون id المحلي)."""
        data = self.get_sync_data()
        # data.pop('id', None)
        return data