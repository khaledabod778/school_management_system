# scripts/cleanup_phantom_conflicts.py
"""
حذف التعارضات الوهمية - التي نشأت من تغييرات العميل نفسه.

الشرط: التعارض الذي local_version == cloud_version ومحتواهما متطابق.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

from datetime import datetime


def _init_db():
    from app.core.config import config_manager
    from app.database.session import init_database

    mode = config_manager.app_config.database_mode
    print(f"🔌 وضع DB: {mode}")
    init_database(use_local=(mode != 'cloud'))
    print("✅ جاهز\n")


def cleanup():
    """حذف التعارضات الوهمية."""
    _init_db()

    from app.database.session import session_scope
    from app.database.models.sync import SyncConflict, SyncQueue

    IGNORE_FIELDS = {
        'id', 'created_at', 'updated_at',
        'sync_updated_at', 'sync_version',
        'sync_source', 'is_synced',
    }

    def same_content(local: dict, cloud: dict) -> bool:
        if not local or not cloud:
            return False
        for key in set(local.keys()) | set(cloud.keys()):
            if key in IGNORE_FIELDS:
                continue
            if str(local.get(key)) != str(cloud.get(key)):
                return False
        return True

    resolved_count = 0

    with session_scope() as session:
        # جلب كل التعارضات المفتوحة
        conflicts = session.query(SyncConflict).filter(
            SyncConflict.status == 'open'
        ).all()

        logger.info(f"📊 إجمالي التعارضات المفتوحة: {len(conflicts)}")

        for conflict in conflicts:
            local = conflict.local_version or {}
            cloud = conflict.cloud_version or {}

            # تجاهل الميتاداتا
            local_clean = {
                k: v for k, v in local.items()
                if k not in IGNORE_FIELDS
            }
            cloud_clean = {
                k: v for k, v in cloud.items()
                if k not in IGNORE_FIELDS
            }

            if same_content(local_clean, cloud_clean):
                # ✅ تعارض وهمي - اغلقه
                conflict.status = 'ignored'
                conflict.resolution_strategy = 'ignored'
                conflict.resolved_at = datetime.now()
                conflict.conflict_reason = (
                    (conflict.conflict_reason or '') +
                    " [أُغلق تلقائياً: محتوى متطابق]"
                )
                resolved_count += 1
                logger.info(
                    f"  ✔️ أُغلق: {conflict.entity_type}/"
                    f"{conflict.entity_uuid[:8]}"
                )

        session.flush()

    print(f"\n{'='*60}")
    print(f"✅ أُغلقت {resolved_count} تعارضات وهمية")
    print(f"{'='*60}")

    # ✅ إعادة جدولة العمليات المرتبطة
    print("\n🔄 إعادة جدولة العمليات المعلّقة...")

    from app.database.session import session_scope as ss

    reset_count = 0
    with ss() as session:
        # أعد العمليات "conflict" إلى pending
        stuck = session.query(SyncQueue).filter(
            SyncQueue.status == 'conflict'
        ).all()

        for item in stuck:
            item.status = 'pending'
            item.attempts = 0
            item.next_retry_at = datetime.now()
            item.last_error = None
            reset_count += 1

        session.flush()

    print(f"✅ أُعيد جدولة {reset_count} عملية")


if __name__ == "__main__":
    cleanup()