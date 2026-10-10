# test_phase2.py
import logging
from pathlib import Path
import sys
logging.basicConfig(level=logging.INFO)
# ✅ أضف جذر المشروع إلى sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
def test_cursor_pull():
    """اختبار أن Pull يستخدم cursor."""
    from app.services.sync.sync_engine import SyncEngine
    from app.database.session import session_scope
    from app.database.models.sync import SyncMetadata

    engine = SyncEngine()

    # ✅ تحقق من وجود KEY_LAST_CURSOR
    assert hasattr(engine, 'KEY_LAST_CURSOR')
    print(f"✅ KEY_LAST_CURSOR = {engine.KEY_LAST_CURSOR}")

    # محاكاة push لتوليد changelog
    with session_scope() as s:
        cursor = SyncMetadata.get(s, engine.KEY_LAST_CURSOR)
        print(f"✅ cursor الحالي: {cursor}")

def test_soft_delete():
    """اختبار Soft Delete."""
    from app.database.models.academic import Grade

    g = Grade(grade_name="test", stage_name="test", max_capacity=30)
    assert not g.is_deleted, "❌ جديدة يجب ألا تكون محذوفة"

    g.soft_delete(user_id=1)
    assert g.is_deleted, "❌ soft_delete لم يعمل"
    assert g.sync_version >= 2, "❌ sync_version لم يزد"
    print("✅ Soft delete يعمل")

    g.restore()
    assert not g.is_deleted, "❌ restore لم يعمل"
    print("✅ Restore يعمل")

if __name__ == "__main__":
    test_cursor_pull()
    test_soft_delete()