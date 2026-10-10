"""
اختبار شامل للمزامنة: إنشاء صف → مراقبة → التحقق.
"""

import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import logging
import time
from datetime import date

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    # 1. تهيئة
    from app.database.session import init_database, session_scope
    init_database(use_local=True)
    
    # 2. تفعيل ChangeTracker
    from app.services.sync.change_tracker import ChangeTracker
    ChangeTracker.setup_listeners()
    ChangeTracker.set_instance('test-script', 'local')
    
    # 3. فحص الطابور قبل
    from app.database.models.sync import SyncQueue
    from sqlalchemy import select, func
    
    with session_scope() as session:
        before = session.execute(select(func.count(SyncQueue.id))).scalar()
        print(f"📊 الطابور قبل: {before}")
    
    # 4. أنشئ صف اختبار
    print("\n📝 إنشاء صف اختبار...")
    from app.database.models.academic import Grade
    
    with session_scope() as session:
        # استخدم اسم فريد لتجنب التعارض
        test_name = f"صف اختبار {int(time.time())}"
        
        grade = Grade(
            grade_name=test_name,
            stage_name="الابتدائي",
            max_capacity=30,
        )
        session.add(grade)
        session.flush()
        
        print(f"   ✅ تم إنشاء: {grade.grade_name}")
        print(f"   ID: {grade.id}")
        print(f"   sync_uuid: {grade.sync_uuid}")
        print(f"   sync_version: {grade.sync_version}")
    
    # 5. فحص الطابور بعد
    with session_scope() as session:
        after = session.execute(select(func.count(SyncQueue.id))).scalar()
        print(f"\n📊 الطابور بعد: {after}")
        
        if after > before:
            print("✅ ChangeTracker سجّل العملية!")
            
            last_op = session.execute(
                select(SyncQueue).order_by(SyncQueue.id.desc()).limit(1)
            ).scalar_one()
            
            print(f"\n📋 آخر عملية:")
            print(f"   ID: {last_op.id}")
            print(f"   Type: {last_op.operation} {last_op.entity_type}")
            print(f"   Status: {last_op.status}")
            print(f"   UUID: {last_op.entity_uuid}")
        else:
            print("❌ ChangeTracker لم يُسجّل!")
            return
    
    # 6. مزامنة
    print("\n🔄 بدء المزامنة...")
    from app.services.sync.sync_engine import SyncEngine
    
    engine = SyncEngine()
    result = engine.push_to_cloud(batch_size=10)
    
    print(f"\n📊 نتيجة المزامنة:")
    print(f"   ✅ pushed: {result['pushed']}")
    print(f"   ❌ failed: {result['failed']}")
    print(f"   ⚠️  conflicts: {result['conflicts']}")
    
    if result['pushed'] > 0:
        print("\n🎉 نجحت المزامنة!")
        print("👉 افتح Railway PostgreSQL وتحقق من:")
        print(f"   SELECT * FROM grades WHERE sync_uuid = '{grade.sync_uuid}';")
    elif result['failed'] > 0:
        print("\n🔴 فشلت المزامنة - راجع logs")
        with session_scope() as session:
            failed = session.execute(
                select(SyncQueue).where(
                    SyncQueue.status == 'failed'
                ).order_by(SyncQueue.id.desc()).limit(1)
            ).scalar_one_or_none()
            
            if failed:
                print(f"   آخر خطأ: {failed.last_error}")


if __name__ == "__main__":
    main()