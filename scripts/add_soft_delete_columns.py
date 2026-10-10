# scripts/add_soft_delete_columns.py
"""
إضافة أعمدة Soft Delete لجميع الجداول القابلة للمزامنة.

يُشغّل مرة واحدة بعد تحديث SyncableMixin.

v2 - إصلاح autobegin في SQLAlchemy 2.x:
يستخدم AUTOCOMMIT mode لعمليات DDL (ALTER TABLE).
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

from sqlalchemy import text, inspect


def _init_db():
    """تهيئة قاعدة البيانات قبل الاستخدام."""
    from app.core.config import config_manager
    from app.database.session import init_database, check_cloud_connection

    mode = config_manager.app_config.database_mode
    print(f"🔌 وضع قاعدة البيانات: {mode}")

    if mode == 'cloud':
        init_database(use_local=False)
    elif mode == 'hybrid':
        try:
            if check_cloud_connection():
                print("☁️ متصل بالسحابة")
                init_database(use_local=False)
            else:
                print("💻 العودة للمحلية")
                init_database(use_local=True)
        except Exception as e:
            print(f"⚠️ {e} - العودة للمحلية")
            init_database(use_local=True)
    else:
        init_database(use_local=True)

    print("✅ قاعدة البيانات جاهزة")


def get_syncable_tables() -> list:
    """قائمة الجداول التي ترث SyncableMixin."""
    from app.database.models import Base
    from app.database.models.sync_mixin import SyncableMixin

    tables = []
    for mapper in Base.registry.mappers:
        cls = mapper.class_
        try:
            if issubclass(cls, SyncableMixin):
                tables.append(cls.__tablename__)
        except TypeError:
            continue
    return sorted(set(tables))


def migrate():
    """إضافة الأعمدة المفقودة لكل الجداول."""
    # 1. هيّئ DB
    _init_db()

    from app.database.connection import db_manager

    # 2. الجداول
    tables = get_syncable_tables()

    logger.info("=" * 70)
    logger.info(f"🔧 Migration: soft delete columns لـ {len(tables)} جدول")
    logger.info("=" * 70)

    added_count = 0
    skipped_count = 0
    failed_count = 0

    # ✅ الحل: استخدام AUTOCOMMIT mode
    # هذا يسمح بتشغيل DDL مباشرة بدون إدارة transactions
    engine = db_manager.engine

    with engine.connect().execution_options(
        isolation_level="AUTOCOMMIT"
    ) as conn:
        inspector = inspect(conn)

        for table in tables:
            try:
                # فحص الأعمدة الموجودة
                try:
                    columns = {
                        c['name'] for c in inspector.get_columns(table)
                    }
                except Exception as e:
                    logger.warning(
                        f"  ⚠️ {table}: تعذّر فحص الأعمدة ({e})"
                    )
                    failed_count += 1
                    continue

                needs_deleted_at = 'deleted_at' not in columns
                needs_deleted_by = 'deleted_by_user_id' not in columns

                if not needs_deleted_at and not needs_deleted_by:
                    skipped_count += 1
                    continue

                # ✅ DDL مباشرة (AUTOCOMMIT)
                if needs_deleted_at:
                    conn.execute(text(
                        f'ALTER TABLE "{table}" '
                        f'ADD COLUMN deleted_at TIMESTAMP NULL'
                    ))
                    logger.info(f"  ✅ {table}: أُضيف deleted_at")

                if needs_deleted_by:
                    conn.execute(text(
                        f'ALTER TABLE "{table}" '
                        f'ADD COLUMN deleted_by_user_id INTEGER NULL'
                    ))
                    logger.info(f"  ✅ {table}: أُضيف deleted_by_user_id")

                # فهرس على deleted_at
                try:
                    conn.execute(text(
                        f'CREATE INDEX IF NOT EXISTS '
                        f'"ix_{table}_deleted_at" '
                        f'ON "{table}" (deleted_at)'
                    ))
                except Exception as idx_err:
                    logger.debug(f"  ℹ️ فهرس {table}: {idx_err}")

                added_count += 1

            except Exception as e:
                logger.error(f"  ❌ {table}: {e}")
                failed_count += 1

    logger.info("=" * 70)
    logger.info(f"📊 النتائج:")
    logger.info(f"   ✅ تم التعديل: {added_count}")
    logger.info(f"   ⏭️  متخطى (كامل): {skipped_count}")
    logger.info(f"   ❌ فشل: {failed_count}")
    logger.info("=" * 70)

    return failed_count == 0


if __name__ == "__main__":
    try:
        success = migrate()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ أُلغيت العملية")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ فشل: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)