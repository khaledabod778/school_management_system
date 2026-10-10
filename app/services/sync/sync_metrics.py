"""
مقاييس المزامنة - للمراقبة والتشخيص.

يوفر إحصائيات دقيقة عن:
- حجم الطابور حسب الحالة
- معدل الفشل
- زمن دورة المزامنة
- أكثر الجداول تأثراً
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.orm import Session

from app.database.models.sync import SyncQueue, SyncConflict, SyncMetadata

logger = logging.getLogger(__name__)


@dataclass
class QueueMetrics:
    """مقاييس الطابور."""
    total: int = 0
    pending: int = 0
    processing: int = 0
    synced: int = 0
    failed: int = 0
    conflict: int = 0
    oldest_pending_seconds: float = 0
    avg_attempts: float = 0


@dataclass
class TableMetrics:
    """مقاييس جدول معيّن."""
    entity_type: str
    pending: int = 0
    failed: int = 0
    synced_last_hour: int = 0


class SyncMetrics:
    """مقاييس المزامنة."""

    @classmethod
    def get_queue_metrics(cls, session: Session) -> QueueMetrics:
        """مقاييس شاملة للطابور."""
        metrics = QueueMetrics()

        # ✅ العدّ حسب الحالة
        stats = session.execute(
            select(
                SyncQueue.status,
                func.count(SyncQueue.id).label('count')
            ).group_by(SyncQueue.status)
        ).all()

        for status, count in stats:
            metrics.total += count
            if hasattr(metrics, status):
                setattr(metrics, status, count)

        # ✅ عمر أقدم عملية معلقة
        oldest = session.execute(
            select(SyncQueue.created_at)
            .where(SyncQueue.status == 'pending')
            .order_by(SyncQueue.created_at.asc())
            .limit(1)
        ).scalar_one_or_none()

        if oldest:
            metrics.oldest_pending_seconds = (
                datetime.now() - oldest
            ).total_seconds()

        # ✅ متوسط المحاولات
        avg = session.execute(
            select(func.avg(SyncQueue.attempts))
            .where(SyncQueue.status.in_(['pending', 'failed']))
        ).scalar()
        metrics.avg_attempts = float(avg or 0)

        return metrics

    @classmethod
    def get_top_tables(
        cls,
        session: Session,
        limit: int = 10,
    ) -> List[TableMetrics]:
        """أكثر الجداول ازدحاماً أو فشلاً."""
        # المعلّقة
        pending_rows = session.execute(
            select(
                SyncQueue.entity_type,
                func.count(SyncQueue.id).label('count')
            )
            .where(SyncQueue.status == 'pending')
            .group_by(SyncQueue.entity_type)
            .order_by(func.count(SyncQueue.id).desc())
            .limit(limit)
        ).all()

        pending_map = {row[0]: row[1] for row in pending_rows}

        # الفاشلة
        failed_rows = session.execute(
            select(
                SyncQueue.entity_type,
                func.count(SyncQueue.id).label('count')
            )
            .where(SyncQueue.status == 'failed')
            .group_by(SyncQueue.entity_type)
            .order_by(func.count(SyncQueue.id).desc())
            .limit(limit)
        ).all()

        failed_map = {row[0]: row[1] for row in failed_rows}

        # المزامنة خلال الساعة الأخيرة
        hour_ago = datetime.now() - timedelta(hours=1)
        synced_rows = session.execute(
            select(
                SyncQueue.entity_type,
                func.count(SyncQueue.id).label('count')
            )
            .where(
                SyncQueue.status == 'synced',
                SyncQueue.processed_at >= hour_ago,
            )
            .group_by(SyncQueue.entity_type)
        ).all()

        synced_map = {row[0]: row[1] for row in synced_rows}

        # دمج
        all_tables = (
            set(pending_map) | set(failed_map) | set(synced_map)
        )

        results = [
            TableMetrics(
                entity_type=t,
                pending=pending_map.get(t, 0),
                failed=failed_map.get(t, 0),
                synced_last_hour=synced_map.get(t, 0),
            )
            for t in all_tables
        ]

        results.sort(
            key=lambda x: (x.failed, x.pending),
            reverse=True,
        )
        return results[:limit]

    @classmethod
    def get_conflicts_summary(cls, session: Session) -> Dict[str, Any]:
        """ملخص التعارضات."""
        open_count = session.execute(
            select(func.count(SyncConflict.id))
            .where(SyncConflict.status == 'open')
        ).scalar() or 0

        resolved_today = session.execute(
            select(func.count(SyncConflict.id))
            .where(
                SyncConflict.status == 'resolved',
                SyncConflict.resolved_at >= datetime.now().replace(
                    hour=0, minute=0, second=0
                )
            )
        ).scalar() or 0

        by_table = session.execute(
            select(
                SyncConflict.entity_type,
                func.count(SyncConflict.id)
            )
            .where(SyncConflict.status == 'open')
            .group_by(SyncConflict.entity_type)
        ).all()

        return {
            'open': open_count,
            'resolved_today': resolved_today,
            'by_table': {row[0]: row[1] for row in by_table},
        }

    @classmethod
    def get_health_status(cls, session: Session) -> Dict[str, Any]:
        """
        حالة صحية شاملة.
        
        يُستخدَم في لوحة المراقبة / Health checks.
        """
        queue = cls.get_queue_metrics(session)
        conflicts = cls.get_conflicts_summary(session)

        # ✅ تقييم الحالة
        if queue.failed > 100 or conflicts['open'] > 50:
            status = 'critical'
        elif queue.failed > 10 or conflicts['open'] > 10:
            status = 'warning'
        elif queue.oldest_pending_seconds > 3600:
            status = 'warning'
        else:
            status = 'healthy'

        return {
            'status': status,
            'queue': asdict(queue),
            'conflicts': conflicts,
            'checked_at': datetime.now().isoformat(),
        }

    @classmethod
    def log_snapshot(cls, session: Session):
        """تسجيل snapshot في الـ logs (للمراقبة الدورية)."""
        try:
            metrics = cls.get_queue_metrics(session)
            logger.info(
                f"📊 Sync Metrics: "
                f"pending={metrics.pending} "
                f"processing={metrics.processing} "
                f"failed={metrics.failed} "
                f"conflict={metrics.conflict} "
                f"oldest={metrics.oldest_pending_seconds:.0f}s"
            )
        except Exception as e:
            logger.warning(f"فشل تسجيل المقاييس: {e}")