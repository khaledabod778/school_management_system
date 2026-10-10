# scripts/clear_queue_errors.py
"""
تنظيف الطابور: إزالة الأخطاء القديمة وإعادة جدولة العمليات.

يُستخدم بعد إصلاح مشكلة جماعية (مثل Migration).
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


def clear():
    _init_db()

    from app.database.session import session_scope
    from app.database.models.sync import SyncQueue

    reset_count = 0
    cleared_errors = 0

    with session_scope() as session:
        # ✅ 1. أعد ضبط كل عمليات pending المعلّقة
        stuck = session.query(SyncQueue).filter(
            SyncQueue.status == 'pending'
        ).all()

        now = datetime.now()
        for item in stuck:
            # أعد ضبط المحاولات
            if item.attempts > 0:
                item.attempts = 0
                cleared_errors += 1

            # أعد الجدولة إلى الآن
            item.next_retry_at = now

            # امسح الأخطاء القديمة
            item.last_error = None
            item.error_code = None

            reset_count += 1

        session.flush()

    print("=" * 60)
    print(f"✅ تم:")
    print(f"   • إعادة جدولة: {reset_count} عملية")
    print(f"   • مسح الأخطاء: {cleared_errors} عملية")
    print("=" * 60)


if __name__ == "__main__":
    clear()