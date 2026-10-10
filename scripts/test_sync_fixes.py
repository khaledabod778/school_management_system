# test_sync_fixes.py
import logging
from pathlib import Path
import sys
logging.basicConfig(level=logging.INFO)

# ✅ أضف جذر المشروع إلى sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_instance_id_unified():
    """التحقق من توحيد instance_id."""
    from app.services.sync.change_tracker import ChangeTracker
    from app.services.sync.sync_engine import SyncEngine

    ChangeTracker.set_instance("local-test-001", source="local")
    engine = SyncEngine()

    assert engine.instance_id == "local-test-001", \
        f"❌ Engine: {engine.instance_id}"
    print("✅ instance_id موحّد")

def test_no_cloud_loop():
    """التحقق من عدم تسجيل تغييرات Cloud في الطابور."""
    from app.database.session import session_scope
    from app.database.models.sync import SyncQueue
    from app.database.models.academic import Grade

    with session_scope() as session:
        g = Grade(grade_name="test", stage_name="test", max_capacity=30)
        g.sync_source = 'cloud'  # simulate from cloud
        session.add(g)
        session.flush()

        # يجب ألا يوجد queue_item
        item = session.query(SyncQueue).filter_by(
            entity_type='grades',
            entity_uuid=g.sync_uuid,
        ).first()
        assert item is None, "❌ تم تسجيل تغيير Cloud في الطابور!"
        print("✅ لا حلقة Cloud→Local")

if __name__ == "__main__":
    test_instance_id_unified()
    test_no_cloud_loop()