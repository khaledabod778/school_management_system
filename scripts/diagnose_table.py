"""
اختبار سريع لمتتبع التغييرات.
"""

import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.session import init_database, session_scope
from app.database.models import Grade, Section, Subject
from app.database.models.sync import SyncQueue
from app.services.sync.change_tracker import ChangeTracker


def main():
    print("=" * 70)
    print("🧪 اختبار Change Tracker")
    print("=" * 70)
    
    # تهيئة
    init_database(use_local=True)
    
    # ✅ تفعيل المتتبع
    ChangeTracker.setup_listeners()
    ChangeTracker.set_instance("test-instance", "local")
    
    # ✅ عدد العمليات قبل
    with session_scope() as session:
        before = session.query(SyncQueue).count()
        print(f"\n📊 عدد العمليات قبل: {before}")
    
    # ✅ إنشاء صف جديد
    print("\n📝 إنشاء مادة دراسية جديدة...")
    try:
        with session_scope() as session:
            subject = Subject(
                subject_name="مادة اختبار المزامنة",
                min_pass_score=50,
                max_score=100,
            )
            session.add(subject)
            session.flush()
            
            print(f"   ✅ تم إنشاء المادة (ID: {subject.id})")
            print(f"   sync_uuid: {subject.sync_uuid}")
            print(f"   sync_version: {subject.sync_version}")
    except Exception as e:
        print(f"   ❌ فشل: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ✅ فحص الطابور
    with session_scope() as session:
        after = session.query(SyncQueue).count()
        print(f"\n📊 عدد العمليات بعد: {after}")
        print(f"📈 العمليات المُضافة: {after - before}")
        
        # عرض آخر 3 عمليات
        recent = session.query(SyncQueue).order_by(
            SyncQueue.id.desc()
        ).limit(3).all()
        
        print(f"\n📋 آخر العمليات:")
        for op in recent:
            print(f"   • ID={op.id} | {op.operation} | "
                  f"{op.entity_type} | status={op.status}")
            print(f"     UUID: {op.entity_uuid}")
            print(f"     Payload keys: {list((op.payload or {}).keys())[:5]}")
    
    print("\n" + "=" * 70)
    if after > before:
        print("✅ ChangeTracker يعمل!")
    else:
        print("❌ ChangeTracker لا يسجل العمليات!")
    print("=" * 70)


if __name__ == "__main__":
    main()