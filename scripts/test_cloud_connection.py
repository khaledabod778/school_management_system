"""
اختبار الاتصال بالسحابة.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

from app.core.config import config_manager


def main():
    config = config_manager.database_config
    
    if not config.cloud_host:
        print("✗ لم يتم تكوين الخادم السحابي")
        return False
    
    print("=" * 60)
    print("اختبار الاتصال بالخادم السحابي")
    print("=" * 60)
    print(f"\nالمضيف: {config.cloud_host}")
    print(f"المنفذ: {config.cloud_port}")
    print(f"القاعدة: {config.cloud_db_name}")
    print(f"المستخدم: {config.cloud_user}")
    
    encoded_password = quote_plus(config.cloud_password)
    url = (
        f"postgresql+psycopg2://{config.cloud_user}:{encoded_password}"
        f"@{config.cloud_host}:{config.cloud_port}/{config.cloud_db_name}"
    )
    
    try:
        print("\nجاري الاتصال...")
        engine = create_engine(
            url,
            connect_args={
                'connect_timeout': 10,
                'sslmode': config.cloud_sslmode,
            }
        )
        
        with engine.connect() as conn:
            # اختبار بسيط
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"\n✓ تم الاتصال بنجاح")
            print(f"  PostgreSQL: {version.split(',')[0]}")
            
            # عرض الجداول
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables_count = result.fetchone()[0]
            print(f"  عدد الجداول: {tables_count}")
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"\n✗ فشل الاتصال: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)