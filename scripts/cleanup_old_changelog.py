# scripts/diagnose_failed_queue.py
"""
فحص العمليات الفاشلة في الطابور - لمعرفة سبب الرفض.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def _init_db():
    from app.core.config import config_manager
    from app.database.session import init_database

    mode = config_manager.app_config.database_mode
    print(f"🔌 وضع DB: {mode}\n")
    init_database(use_local=(mode != 'cloud'))


def diagnose():
    _init_db()

    from app.database.session import session_scope
    from app.database.models.sync import SyncQueue

    with session_scope() as session:
        # ✅ 1. العمليات الفاشلة - اطبع السبب
        failed = session.query(SyncQueue).filter(
            SyncQueue.status == 'failed'
        ).all()

        print(f"{'='*70}")
        print(f"❌ عمليات فاشلة نهائياً: {len(failed)}")
        print(f"{'='*70}")

        # جمّع الأسباب
        error_counts = {}
        for item in failed:
            err = (item.last_error or 'لا يوجد خطأ مسجّل')[:100]
            error_counts[err] = error_counts.get(err, 0) + 1

        for err, count in sorted(error_counts.items(), key=lambda x: -x[1]):
            print(f"  [{count}x] {err}")

        # ✅ 2. العمليات الـ pending - اطبع عيّنة
        pending = session.query(SyncQueue).filter(
            SyncQueue.status == 'pending',
            SyncQueue.attempts > 0,
        ).order_by(SyncQueue.attempts.desc()).limit(20).all()

        print(f"\n{'='*70}")
        print(f"⏳ عمليات pending بأخطاء سابقة: {len(pending)} (عيّنة)")
        print(f"{'='*70}")

        for item in pending:
            err = (item.last_error or 'لا يوجد')[:80]
            print(
                f"  {item.entity_type}/{item.entity_uuid[:8]} "
                f"attempts={item.attempts} "
                f"err={err}"
            )

        # ✅ 3. عدّ حسب entity_type
        from sqlalchemy import func
        by_type = session.query(
            SyncQueue.entity_type,
            SyncQueue.status,
            func.count(SyncQueue.id),
        ).group_by(
            SyncQueue.entity_type, SyncQueue.status
        ).all()

        print(f"\n{'='*70}")
        print(f"📊 توزيع الطابور حسب الجدول:")
        print(f"{'='*70}")

        grouped = {}
        for entity, status, count in by_type:
            if entity not in grouped:
                grouped[entity] = {}
            grouped[entity][status] = count

        for entity in sorted(grouped.keys()):
            statuses = grouped[entity]
            total = sum(statuses.values())
            print(f"  {entity:30s} total={total:4d}  {statuses}")


if __name__ == "__main__":
    diagnose()