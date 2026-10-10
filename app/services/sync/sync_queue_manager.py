"""
مدير طابور المزامنة.
يتعامل مع إضافة وقراءة وتحديث العمليات.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session

from app.database.session import session_scope
from app.database.models.sync import SyncQueue, SyncConflict, SyncMetadata
from app.database.models.sync_mixin import SyncableMixin

logger = logging.getLogger(__name__)


class SyncQueueManager:
    """مدير طابور المزامنة."""
    
    # استراتيجية إعادة المحاولة (backoff exponential)
    RETRY_DELAYS = [5, 15, 60, 300, 900, 1800, 3600, 7200]  # ثواني
    
    @staticmethod
    def enqueue(
        session: Session,
        entity: SyncableMixin,
        operation: str,
        direction: str = 'to_cloud',
        old_payload: Optional[dict] = None,
        priority: int = 5
    ) -> Optional[SyncQueue]:
        """
        إضافة عملية إلى طابور المزامنة.
        
        Returns:
            كائن SyncQueue أو None إذا وُجد مسبقاً في session.new
        """
        entity_type = entity.__class__.__tablename__
        entity_uuid = entity.sync_uuid
        entity_local_id = getattr(entity, 'id', None)

        # ✅ v4: افحص session.new أولاً (منع التكرار)
        for obj in session.new:
            if isinstance(obj, SyncQueue):
                if (obj.entity_type == entity_type
                        and obj.entity_uuid == entity_uuid
                        and obj.direction == direction):
                    # موجود بالفعل في session.new
                    return obj
        
        # استبعاد الحقول التي لا تحتاج مزامنة
        payload = entity.to_sync_dict() if operation != 'DELETE' else None
        
        # إذا كانت العملية تحديثاً، نجمع البيانات القديمة
        if operation == 'UPDATE' and old_payload is None:
            old_payload = entity.get_sync_data()
        
        # التحقق من وجود عملية معلقة لنفس الكيان
        existing = session.execute(
            select(SyncQueue).where(
                SyncQueue.entity_type == entity_type,
                SyncQueue.entity_uuid == entity_uuid,
                SyncQueue.direction == direction,
                SyncQueue.status.in_(['pending', 'processing'])
            ).order_by(SyncQueue.created_at.desc()).limit(1)
        ).scalar_one_or_none()
        
        if existing:
            # دمج العمليات
            merged = SyncQueueManager._merge_operation(
                existing, operation, payload, old_payload
            )
            logger.debug(f"تم دمج العملية مع المعلقة: {entity_type}/{entity_uuid}")
            return merged
        
        # إنشاء عملية جديدة
        queue_item = SyncQueue(
            entity_type=entity_type,
            entity_uuid=entity_uuid,
            entity_local_id=entity_local_id,
            operation=operation,
            direction=direction,
            payload=payload,
            old_payload=old_payload,
            status='pending',
            priority=priority,
            next_retry_at=datetime.now()
        )
        
        session.add(queue_item)
        
        logger.info(f"تم إضافة عملية: {operation} {entity_type}/{entity_uuid[:8]}")
        return queue_item
    
    @staticmethod
    def _merge_operation(
        existing: SyncQueue,
        new_operation: str,
        new_payload: Optional[dict],
        old_payload: Optional[dict]
    ) -> SyncQueue:
        """دمج عملية جديدة مع عملية معلقة موجودة."""
        
        # قواعد الدمج:
        # INSERT + UPDATE = INSERT (بالبيانات الجديدة)
        # INSERT + DELETE = إلغاء العملية (لا شيء)
        # UPDATE + UPDATE = UPDATE (بالبيانات الجديدة)
        # UPDATE + DELETE = DELETE
        # DELETE + أي شيء = DELETE
        
        if existing.operation == 'INSERT':
            if new_operation == 'DELETE':
                # إلغاء العملية
                existing.status = 'synced'
                existing.processed_at = datetime.now()
                existing.notes = 'ألغيت: إضافة ثم حذف'
                return existing
            else:
                # INSERT مع تحديث
                existing.payload = new_payload
                existing.updated_at = datetime.now()
                # ✅ جدول إعادة المحاولة فوراً عند الدمج
                existing.next_retry_at = datetime.now()
                return existing
        
        elif existing.operation == 'UPDATE':
            if new_operation == 'DELETE':
                existing.operation = 'DELETE'
                existing.payload = None
                existing.old_payload = existing.old_payload or old_payload
                existing.updated_at = datetime.now()
                existing.next_retry_at = datetime.now()                
                return existing
            else:
                # UPDATE مع تحديث
                existing.payload = new_payload
                existing.updated_at = datetime.now()
                existing.next_retry_at = datetime.now()
                return existing
        
        elif existing.operation == 'DELETE':
            # تبقى DELETE
            return existing
        
        return existing
    
    @staticmethod
    def get_pending_operations(
        session: Session,
        direction: str = 'to_cloud',
        limit: int = 100,
        entity_type: Optional[str] = None
    ) -> List[SyncQueue]:
        """
        الحصول على العمليات المعلقة الجاهزة للمعالجة.
        مرتبة حسب الأولوية والوقت.
        """
        now = datetime.now()
        
        query = select(SyncQueue).where(
            SyncQueue.direction == direction,
            SyncQueue.status == 'pending',
            SyncQueue.attempts < SyncQueue.max_attempts,
            or_(
                SyncQueue.next_retry_at.is_(None),
                SyncQueue.next_retry_at <= now
            )
        )
        
        if entity_type:
            query = query.where(SyncQueue.entity_type == entity_type)
        
        query = query.order_by(
            SyncQueue.priority.asc(),
            SyncQueue.created_at.asc()
        ).limit(limit)
        
        return list(session.execute(query).scalars().all())
    
    @staticmethod
    def mark_processing(session: Session, item: SyncQueue):
        """تعليم عملية قيد المعالجة."""
        item.status = 'processing'
        item.attempts += 1
        item.processed_at = datetime.now()
    
    @staticmethod
    def mark_synced(session: Session, item: SyncQueue):
        """تعليم عملية كمتزامنة."""
        item.status = 'synced'
        item.processed_at = datetime.now()
        item.last_error = None
        
        logger.debug(f"متزامنة: {item.operation} {item.entity_type}/{item.entity_uuid[:8]}")
    
    @staticmethod
    def mark_failed(
        session: Session,
        item: SyncQueue,
        error: str,
        error_code: Optional[str] = None
    ):
        """تعليم عملية كفاشلة مع جدولة إعادة المحاولة."""
        # ✅ v2: زيادة العداد إذا لم يُزَد بعد (منع attempts=0)
        if item.status != 'processing':
            item.attempts += 1

        item.status = (
            'failed' if item.attempts >= item.max_attempts else 'pending'
        )
        item.last_error = error[:2000]
        item.error_code = error_code
        item.processed_at = datetime.now()

        # جدولة إعادة المحاولة
        if item.attempts < item.max_attempts:
            # ✅ v2: max(0, ...) لمنع الفهرس السالب
            delay_idx = min(
                max(0, item.attempts - 1),
                len(SyncQueueManager.RETRY_DELAYS) - 1
            )
            delay = SyncQueueManager.RETRY_DELAYS[delay_idx]
            item.next_retry_at = datetime.now() + timedelta(seconds=delay)

            logger.warning(
                f"⚠️ فشلت (محاولة {item.attempts}/{item.max_attempts}): "
                f"{item.entity_type}/{item.entity_uuid[:8]} - "
                f"إعادة بعد {delay}s"
            )
        else:
            item.next_retry_at = None
            logger.error(
                f"❌ فشلت نهائياً بعد {item.attempts} محاولات: "
                f"{item.entity_type}/{item.entity_uuid[:8]}"
            )
    
    @staticmethod
    def mark_conflict(
        session: Session,
        item: SyncQueue,
        local_data: dict,
        cloud_data: dict,
        reason: str
    ) -> SyncConflict:
        """تعليم عملية كمتضاربة وإنشاء سجل تعارض."""
        item.status = 'conflict'
        item.processed_at = datetime.now()
        
        # إنشاء سجل التعارض
        conflict = SyncConflict(
            sync_queue_id=item.id,
            entity_type=item.entity_type,
            entity_uuid=item.entity_uuid,
            local_version=local_data,
            cloud_version=cloud_data,
            base_version=item.old_payload,
            status='open',
            conflict_reason=reason,
            resolution_strategy='pending'
        )
        
        session.add(conflict)
        
        logger.warning(
            f"تعارض: {item.entity_type}/{item.entity_uuid[:8]} - {reason}"
        )
        
        return conflict
    
    @staticmethod
    def cleanup_synced(session: Session, older_than_days: int = 7) -> int:
        """حذف العمليات المتزامنة القديمة."""
        cutoff = datetime.now() - timedelta(days=older_than_days)
        
        result = session.execute(
            select(SyncQueue).where(
                SyncQueue.status == 'synced',
                SyncQueue.processed_at < cutoff
            )
        ).scalars().all()
        
        count = len(result)
        for item in result:
            session.delete(item)
        
        session.flush()
        logger.info(f"تم حذف {count} عملية متزامنة قديمة")
        return count
    
    @staticmethod
    def get_stats(session: Session) -> Dict[str, int]:
        """إحصائيات طابور المزامنة."""
        stats = {}
        
        for status in ['pending', 'processing', 'synced', 'failed', 'conflict']:
            count = session.execute(
                select(func.count(SyncQueue.id)).where(SyncQueue.status == status)
            ).scalar() or 0
            stats[status] = count
        
        return stats