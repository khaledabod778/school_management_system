# scripts/encrypt_existing_config.py
"""ترقية config.json القديم إلى الصيغة المشفّرة."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.secrets_manager import secrets_manager


def migrate(config_file: str = "config.json"):
    path = Path(config_file)
    if not path.exists():
        print(f"❌ {config_file} غير موجود")
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'database' not in data:
        print("❌ لا يوجد قسم database")
        return

    db = data['database']
    for key in secrets_manager.ENCRYPTED_FIELDS:
        if key in db and db[key] and not db[key].startswith('ENC:'):
            encrypted = secrets_manager.encrypt(db[key])
            db[key] = encrypted
            print(f"🔐 شُفّر: {key}")

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ تم ترقية {config_file}")
    print(f"🔑 المفتاح محفوظ في: {secrets_manager.key_path}")
    print("⚠️ احتفظ بنسخة احتياطية من master.key - فقدانه يفقد كل الأسرار!")


if __name__ == "__main__":
    migrate()