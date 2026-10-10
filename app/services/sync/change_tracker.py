"""
متتبع التغييرات - يسجل التعديلات في sync_queue تلقائياً.

v2.0 - إصلاحات حرجة:
- منع حلقة Cloud → Local → Cloud (skip sync_source='cloud')
- استخدام no_autoflush لتفادي recursion
- ضبط is_synced=False على UPDATE
- old_payload فقط لـ UPDATE/DELETE
- تعقّب آمن لـ sync_uuid قبل flush
"""

import logging
from typing import Optional
import uuid
from sqlalchemy import event, select
from sqlalchemy.orm import Session

from app.database.models.sync import SyncQueue
from app.database.models.sync_mixin import SyncableMixin

logger = logging.getLogger(__name__)


class ChangeTracker:
    """
    يتتبع التغييرات في الجداول القابلة للمزامنة.
    يستخدم SQLAlchemy events لتسجيل INSERT/UPDATE/DELETE تلقائياً.
    """

    # ✅ المصدر الوحيد للحقيقة (single source of truth)
    _current_instance_id: str = "local-main"
    _current_source: str = "local"

    # ✅ علم داخلي لمنع التداخل
    _TRACKING_FLAG = "_sync_tracking_in_progress"

    # ✅ جداول مستثناة من المزامنة
    EXCLUDED_TABLES = frozenset({
        'sync_queue', 'sync_conflicts', 'sync_metadata',
        'sync_instances', 'system_audit_logs',
    })

    @classmethod
    def set_instance(cls, instance_id: str, source: str = "local"):
        """تعيين هوية النسخة الحالية."""
        cls._current_instance_id = instance_id
        cls._current_source = source
        logger.info(f"✅ ChangeTracker: instance={instance_id} ({source})")

    @classmethod
    def get_instance_id(cls) -> str:
        """
        ✅ الحصول على معرف النسخة الحالية.

        هذا هو المصدر الوحيد للحقيقة - SyncEngine يجب أن يستخدمه.
        """
        return cls._current_instance_id

    @classmethod
    def setup_listeners(cls):
        """إعداد مستمعي الأحداث لجميع الجداول القابلة للمزامنة."""

        @event.listens_for(Session, "before_flush")
        def before_flush(session, flush_context, instances):
            """
            قبل flush - التقاط التغييرات وتسجيلها في sync_queue.
            """
            # ✅ منع الحلقات المتداخلة
            if session.info.get(cls._TRACKING_FLAG):
                return

            session.info[cls._TRACKING_FLAG] = True
            try:
                # ✅ تعطيل autoflush لتفادي recursion
                with session.no_autoflush:
                    cls._process_changes(session)
            except Exception as e:
                logger.error(f"خطأ في متتبع التغييرات: {e}", exc_info=True)
            finally:
                session.info.pop(cls._TRACKING_FLAG, None)

    # ==================== المعالجة ====================

    @classmethod
    def _process_changes(cls, session: Session):
        """معالجة جميع التغييرات في الجلسة."""

        # INSERT
        for obj in list(session.new):
            if cls._should_skip(obj):
                continue
            if cls._is_syncable(obj):
                cls._handle_insert(session, obj)

        # UPDATE
        for obj in list(session.dirty):
            if cls._should_skip(obj):
                continue
            if cls._is_syncable(obj) and session.is_modified(obj):
                cls._handle_update(session, obj)

        # DELETE
        for obj in list(session.deleted):
            if cls._should_skip(obj):
                continue
            if cls._is_syncable(obj):
                cls._handle_delete(session, obj)

    @classmethod
    def _should_skip(cls, obj) -> bool:
        """
        ✅ هل يجب تخطي هذا الكائن؟

        نتخطى التغييرات التي أتت من السحابة (sync_source='cloud')
        لمنع حلقة Cloud → Local → Cloud → ...
        """
        return getattr(obj, 'sync_source', None) == 'cloud'

    @classmethod
    def _is_syncable(cls, obj) -> bool:
        """هل الكائن قابل للمزامنة؟"""
        return isinstance(obj, SyncableMixin)

    @classmethod
    def _ensure_sync_uuid(cls, obj):
        """
        ✅ ضمان وجود sync_uuid قبل flush.

        نستخدم __dict__ للتحقق من القيمة الفعلية (لا الـ default).
        """
        current = obj.__dict__.get('sync_uuid')
        if not current:
            obj.sync_uuid = str(uuid.uuid4())

    # ==================== Handlers ====================

    @classmethod
    def _handle_insert(cls, session, obj):
        """معالجة إدراج جديد."""
        try:
            cls._ensure_sync_uuid(obj)
            # ✅ INSERT: لا حاجة لـ old_payload
            cls._add_to_queue(session, obj, 'INSERT', include_old=False)
        except Exception as e:
            logger.error(f"فشل تتبع INSERT: {e}", exc_info=True)

    @classmethod
    def _handle_update(cls, session: Session, obj: SyncableMixin):
        """معالجة تعديل."""
        # ✅ زيادة رقم النسخة
        obj.sync_version = (obj.sync_version or 0) + 1
        obj.sync_source = cls._current_source
        obj.is_synced = False  # ✅ لم يعد متزامناً بعد التعديل

        # ✅ UPDATE: احتفظ بالبيانات القديمة
        cls._add_to_queue(session, obj, 'UPDATE', include_old=True)

        logger.debug(f"UPDATE tracked: {obj.__class__.__tablename__}")

    @classmethod
    def _handle_delete(cls, session: Session, obj: SyncableMixin):
        """معالجة حذف."""
        # ✅ DELETE: احتفظ بالبيانات قبل الحذف
        cls._add_to_queue(session, obj, 'DELETE', include_old=True)
        logger.debug(f"DELETE tracked: {obj.__class__.__tablename__}")

    # ==================== إضافة للطابور ====================

    @classmethod
    def _add_to_queue(
        cls,
        session: Session,
        obj: SyncableMixin,
        operation: str,
        include_old: bool = False,
    ):
        """إضافة عملية إلى طابور المزامنة."""
        from app.services.sync.sync_queue_manager import SyncQueueManager

        entity_type = obj.__class__.__tablename__
        entity_uuid = obj.sync_uuid
        # ⚠️ entity_local_id قد يكون None في INSERT (قبل flush)
        entity_local_id = getattr(obj, 'id', None)

        if entity_type in cls.EXCLUDED_TABLES:
            return

        # تحضير البيانات
        if operation != 'DELETE':
            payload = obj.to_sync_dict()
            # ✅ v3: أضف UUIDs لحقول FK
            try:
                from app.services.sync.fk_resolver import FKResolver
                payload = FKResolver.enrich_payload(
                    session, entity_type, payload
                )
            except Exception as e:
                logger.debug(f"FK enrichment فشل: {e}")
        else:
            payload = None

        old_payload = obj.get_sync_data() if include_old else None
        
        # ✅ البحث عن عملية معلقة (بدون autoflush - نحن داخله)
        existing = session.execute(
            select(SyncQueue).where(
                SyncQueue.entity_type == entity_type,
                SyncQueue.entity_uuid == entity_uuid,
                SyncQueue.direction == 'to_cloud',
                SyncQueue.status.in_(['pending', 'processing'])
            ).limit(1)
        ).scalar_one_or_none()

        if existing:
            SyncQueueManager._merge_operation(
                existing, operation, payload, old_payload
            )
        else:
            # ✅ v4: افحص session.new (منع التكرار)
            for obj in session.new:
                if isinstance(obj, SyncQueue):
                    if (obj.entity_type == entity_type
                            and obj.entity_uuid == entity_uuid
                            and obj.direction == 'to_cloud'):
                        # موجود بالفعل
                        return
                    
            queue_item = SyncQueue(
                entity_type=entity_type,
                entity_uuid=entity_uuid,
                entity_local_id=entity_local_id,
                operation=operation,
                direction='to_cloud',
                payload=payload,
                old_payload=old_payload,
                status='pending',
                priority=cls._get_priority(entity_type),
                source_instance_id=cls._current_instance_id,
            )
            session.add(queue_item)

    @classmethod
    def _get_priority(cls, entity_type: str) -> int:
        """تحديد أولوية الكيان."""
        priorities = {
            'students': 3,
            'parents': 3,
            'users': 2,
            'employees': 3,
            'receipts': 2,
            'expense_vouchers': 2,
            'payroll_records': 4,
            'daily_attendance': 6,
            'monthly_evaluations': 7,
            'term_exam_scores': 6,
            'notifications': 5,
        }
        return priorities.get(entity_type, 5)