# scripts/diagnose_crypto.py
import sys
import json
from pathlib import Path

# ✅ أضف جذر المشروع إلى sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.secrets_manager import secrets_manager


def diagnose():
    print("=" * 60)
    print("🔍 تشخيص حالة التشفير")
    print("=" * 60)

    # 1. مفتاح التشفير
    key_path = secrets_manager.key_path
    print(f"\n📁 مسار المفتاح: {key_path}")

    if key_path.exists():
        import datetime
        stat = key_path.stat()
        modified = datetime.datetime.fromtimestamp(stat.st_mtime)
        print(f"   ✅ موجود | الحجم: {stat.st_size} bytes | آخر تعديل: {modified}")
    else:
        print(f"   ❌ غير موجود!")
        return

    # 2. اختبار المفتاح الحالي
    print("\n🧪 اختبار المفتاح الحالي:")
    test_value = "test-value-12345"
    try:
        encrypted = secrets_manager.encrypt(test_value)
        decrypted = secrets_manager.decrypt(encrypted)
        if decrypted == test_value:
            print(f"   ✅ المفتاح يعمل")
        else:
            print(f"   ❌ فك التشفير أعاد قيمة خاطئة")
    except Exception as e:
        print(f"   ❌ فشل: {e}")

    # 3. فحص config.json
    print("\n📄 فحص config.json:")
    config_file = PROJECT_ROOT / "config.json"
    if not config_file.exists():
        print(f"   ❌ الملف غير موجود في {config_file}")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    db = data.get('database', {})
    for key in secrets_manager.ENCRYPTED_FIELDS:
        value = db.get(key, '')
        if not value:
            print(f"   ⚪ {key}: فارغ")
        elif not value.startswith('ENC:'):
            print(f"   🟡 {key}: غير مشفّر (plaintext) - طول {len(value)}")
        else:
            # حاول فك التشفير
            decrypted = secrets_manager.decrypt(value)
            if decrypted:
                preview = decrypted[:15] + '...' if len(decrypted) > 15 else decrypted
                print(f"   ✅ {key}: مشفّر ويفك بنجاح ({preview})")
            else:
                print(f"   ❌ {key}: مشفّر لكن لا يمكن فكه! (طول: {len(value)})")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    diagnose()