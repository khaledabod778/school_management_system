# scripts/reset_stuck_queue.py
"""
إعادة جدولة العمليات العالقة في الطابور.

يُستخدم بعد إصلاح BUG mark_failed.
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
    """تهيئة DB."""
    from app.core.config import config_manager
    from app.database.session import init_database

    mode = config_manager.app_config.database_mode
    print(f"🔌 وضع DB: {mode}")

    if mode == 'cloud':
        init_database(use_local=False)
    else:
        init_database(use_local=True)
    print("✅ جاهز")


def reset_stuck():
    """إعادة جدولة كل العمليات المجدولة بعيداً."""
    _init_db()

    from app.database.session import session_scope
    from app.database.models.sync import SyncQueue
    from sqlalchemy import select

    now = datetime.now()
    reset_count = 0
    failed_reset_count = 0

    with session_scope() as session:
        # ✅ 1. إعادة جدولة العمليات المجدولة لأكثر من 5 دقائق
        result = session.execute(
            select(SyncQueue).where(
                SyncQueue.status == 'pending',
                SyncQueue.next_retry_at > now,
            )
        ).scalars().all()

        for item in result:
            wait_seconds = (item.next_retry_at - now).total_seconds()
            if wait_seconds > 300:  # > 5 دقائق
                item.next_retry_at = now
                reset_count += 1

        # ✅ 2. إعادة العمليات "failed" نهائياً إلى pending
        failed = session.execute(
            select(SyncQueue).where(
                SyncQueue.status == 'failed',
            )
        ).scalars().all()

        for item in failed:
            if item.attempts >= item.max_attempts:
                # أعد العداد
                item.attempts = 0
                item.status = 'pending'
                item.next_retry_at = now
                item.last_error = None
                failed_reset_count += 1

        session.flush()

    print(f"\n{'='*60}")
    print(f"✅ النتائج:")
    print(f"   • عمليات أُعيد جدولتها: {reset_count}")
    print(f"   • عمليات failed أُعيدت: {failed_reset_count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    reset_stuck()