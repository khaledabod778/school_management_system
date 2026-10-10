# scripts/migrate_cloud_columns.py
"""
إضافة الأعمدة المفقودة في Cloud DB.

✅ v2: يدعم Public URL بدلاً من internal host.
يقرأ الإعدادات من:
  1. config.json (cloud_host)
  2. متغيرات البيئة (CLOUD_DB_HOST, CLOUD_DB_PORT, ...)
"""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import URL


def get_cloud_credentials():
    """
    الحصول على بيانات الاتصال بالسحابة.
    
    الأولوية:
    1. متغيرات البيئة (CLOUD_DB_HOST, ...)
    2. config.json
    """
    # ==================== 1. متغيرات البيئة ====================
    env_host = os.environ.get('CLOUD_DB_HOST')
    if env_host:
        print("📌 استخدام متغيرات البيئة")
        return {
            'host': env_host,
            'port': int(os.environ.get('CLOUD_DB_PORT', 5432)),
            'user': os.environ.get('CLOUD_DB_USER', 'postgres'),
            'password': os.environ.get('CLOUD_DB_PASSWORD', ''),
            'dbname': os.environ.get('CLOUD_DB_NAME', 'railway'),
            'sslmode': os.environ.get('CLOUD_DB_SSLMODE', 'require'),
        }

    # ==================== 2. config.json ====================
    from app.core.config import config_manager
    cfg = config_manager.database_config

    host = cfg.cloud_host
    port = cfg.cloud_port

    if not host:
        print("❌ cloud_host فارغ في config.json")
        sys.exit(1)

    # ⚠️ تحذير: railway.internal لا يعمل من خارج Railway
    if '.railway.internal' in host:
        print()
        print("=" * 70)
        print("❌ المشكلة: cloud_host يشير إلى عنوان داخلي")
        print(f"   {host}")
        print()
        print("📌 الحل: احصل على Public URL من Railway:")
        print("   1. railway.app → مشروعك → PostgreSQL")
        print("   2. Settings → Networking → Generate Domain")
        print("   3. انسخ Host و Port الجديدين")
        print()
        print("   ثم شغّل:")
        print("   $env:CLOUD_DB_HOST = 'containers-xxx.railway.app'")
        print("   $env:CLOUD_DB_PORT = '45231'")
        print("   $env:CLOUD_DB_PASSWORD = 'كلمة_المرور'")
        print("   python scripts/migrate_cloud_columns.py")
        print("=" * 70)
        sys.exit(1)

    return {
        'host': host,
        'port': port,
        'user': cfg.cloud_user,
        'password': cfg.cloud_password,
        'dbname': cfg.cloud_db_name,
        'sslmode': cfg.cloud_sslmode or 'require',
    }


def create_cloud_engine(creds):
    """إنشاء engine بـ credentials مباشرة."""
    url = URL.create(
        drivername='postgresql+psycopg2',
        username=creds['user'],
        password=creds['password'],
        host=creds['host'],
        port=creds['port'],
        database=creds['dbname'],
        query={'sslmode': creds['sslmode']},
    )
    return create_engine(url, echo=False)


def check_columns(conn):
    """فحص الأعمدة الحالية."""
    inspector = inspect(conn)
    results = {}

    for table, col in [
        ('cloud_instances', 'last_pulled_cursor'),
        ('cloud_changelog', 'entity_sync_version'),
    ]:
        try:
            cols = [c['name'] for c in inspector.get_columns(table)]
            results[f'{table}.{col}'] = col in cols
        except Exception as e:
            results[f'{table}.{col}'] = f"خطأ: {e}"

    print("\n📊 الفحص الحالي:")
    for key, val in results.items():
        if isinstance(val, bool):
            icon = "✅" if val else "❌"
            print(f"   {icon} {key}")
        else:
            print(f"   ⚠️ {key}: {val}")

    return results


def migrate():
    """تطبيق Migration."""
    print("=" * 70)
    print("🔧 Migration: Cloud DB Columns")
    print("=" * 70)

    creds = get_cloud_credentials()
    print(f"\n🔌 الاتصال بـ: {creds['host']}:{creds['port']}/{creds['dbname']}")

    try:
        engine = create_cloud_engine(creds)

        # اختبار الاتصال
        with engine.connect() as test_conn:
            test_conn.execute(text("SELECT 1"))
        print("✅ الاتصال نجح\n")

    except Exception as e:
        print(f"\n❌ فشل الاتصال: {e}")
        print("\n💡 تحقق من:")
        print("   • Public Host/Port صحيحان")
        print("   • كلمة المرور صحيحة")
        print("   • SSL مطلوب (sslmode=require)")
        sys.exit(1)

    # ==================== Migration ====================
    engine = create_cloud_engine(creds)

    with engine.connect().execution_options(
        isolation_level="AUTOCOMMIT"
    ) as conn:
        check_columns(conn)

        print("\n🔧 بدء Migration...\n")

        migrations = [
            (
                "cloud_instances.last_pulled_cursor",
                "ALTER TABLE cloud_instances "
                "ADD COLUMN IF NOT EXISTS last_pulled_cursor BIGINT "
                "DEFAULT 0 NOT NULL",
            ),
            (
                "cloud_changelog.entity_sync_version",
                "ALTER TABLE cloud_changelog "
                "ADD COLUMN IF NOT EXISTS entity_sync_version INTEGER NULL",
            ),
            (
                "index for cursor query",
                "CREATE INDEX IF NOT EXISTS idx_changelog_cursor "
                "ON cloud_changelog (id, device_id)",
            ),
            (
                "populate last_pulled_cursor defaults",
                "UPDATE cloud_instances "
                "SET last_pulled_cursor = 0 "
                "WHERE last_pulled_cursor IS NULL",
            ),
        ]

        success = 0
        failed = 0

        for name, sql in migrations:
            try:
                conn.execute(text(sql))
                logger.info(f"  ✅ {name}")
                success += 1
            except Exception as e:
                logger.error(f"  ❌ {name}: {e}")
                failed += 1

        print("\n📊 بعد Migration:")
        final = check_columns(conn)

        print(f"\n{'='*70}")
        print(f"  ✅ نجح: {success}")
        print(f"  ❌ فشل: {failed}")
        print(f"{'='*70}")

        all_ok = all(v is True for v in final.values())
        if all_ok:
            print("\n🎉 Migration اكتمل بنجاح!")
        return all_ok


if __name__ == "__main__":
    try:
        success = migrate()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ أُلغيت")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)