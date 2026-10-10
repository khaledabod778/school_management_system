# scripts/fix_passwords.py
"""
إصلاح كلمات المرور في config.json.

يطلب من المستخدم القيم الصحيحة ويشفّرها بالمفتاح الحالي.
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.secrets_manager import secrets_manager


# الحقول التي ستُشفَّر مع وصفها
FIELDS_TO_FIX = [
    {
        'key': 'local_password',
        'label': 'كلمة مرور PostgreSQL المحلي',
        'hint': 'الافتراضي: postgres',
        'default': 'postgres',
    },
    {
        'key': 'cloud_password',
        'label': 'كلمة مرور PostgreSQL السحابي (Railway)',
        'hint': 'من لوحة Railway → PostgreSQL → Variables → PGPASSWORD',
        'default': '',
    },
    {
        'key': 'cloud_api_key',
        'label': 'مفتاح Cloud API',
        'hint': 'من لوحة Cloud API → Settings → API Keys',
        'default': '',
    },
]


def fix_passwords():
    config_file = PROJECT_ROOT / "config.json"

    if not config_file.exists():
        print(f"❌ {config_file} غير موجود")
        return 1

    # نسخة احتياطية
    backup = config_file.with_name(
        f"config_backup_{datetime.now():%Y%m%d_%H%M%S}.json"
    )
    shutil.copy2(config_file, backup)
    print(f"✅ نسخة احتياطية: {backup.name}")

    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'database' not in data:
        print("❌ لا يوجد قسم database في config.json")
        return 1

    db = data['database']

    # ==================== عرض الحالة الحالية ====================
    print("\n" + "=" * 65)
    print("📊 الحالة الحالية")
    print("=" * 65)

    for field in FIELDS_TO_FIX:
        key = field['key']
        value = db.get(key, '')

        if not value:
            status = "⚪ فارغ"
            preview = ""
        elif value.startswith('ENC:'):
            # حاول فك التشفير
            try:
                decrypted = secrets_manager.decrypt(value, strict=True)
                status = "✅ مشفّر سليم"
                preview = f"→ {decrypted[:15]}..."
            except ValueError:
                status = "❌ مشفّر لكن لا يفك!"
                preview = f"(قيمة تالفة، طول={len(value)})"
        else:
            status = "🟡 plaintext"
            preview = f"→ {value[:15]}..."

        print(f"  {key:20s} : {status} {preview}")

    print("=" * 65)

    # ==================== طلب القيم الجديدة ====================
    print("\n📝 أدخل القيم الصحيحة (اترك الحقل فارغاً لاستخدام القيمة الحالية)")
    print()

    new_values = {}

    for field in FIELDS_TO_FIX:
        key = field['key']
        print(f"🔹 {field['label']}")
        print(f"   💡 {field['hint']}")
        if field['default']:
            print(f"   📌 Default: {field['default']}")

        try:
            value = input(f"   {key}: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n❌ أُلغيت العملية")
            return 1

        if not value:
            # استخدم default إن وُجد
            if field['default']:
                value = field['default']
                print(f"   ✅ استُخدم الافتراضي: {value}")
            else:
                print(f"   ⚠️ تُرك فارغاً")
                value = ''
        else:
            print(f"   ✅ سيُشفّر")

        new_values[key] = value
        print()

    # ==================== تأكيد ====================
    print("=" * 65)
    print("⚠️  مراجعة قبل الحفظ:")
    print()
    for field in FIELDS_TO_FIX:
        key = field['key']
        value = new_values[key]
        display = value[:10] + '...' if len(value) > 10 else (value or '(فارغ)')
        print(f"   {key:20s} = {display}")
    print()

    try:
        confirm = input("هل تريد المتابعة؟ (y/n): ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        confirm = 'n'

    if confirm not in ('y', 'yes', 'نعم', ''):
        print("❌ أُلغيت العملية")
        return 1

    # ==================== التشفير والحفظ ====================
    print("\n🔐 جاري التشفير...")

    for field in FIELDS_TO_FIX:
        key = field['key']
        value = new_values[key]

        if value:
            encrypted = secrets_manager.encrypt(value)
            db[key] = encrypted
            # تحقق أن التشفير يعمل
            check = secrets_manager.decrypt(encrypted, strict=True)
            assert check == value, f"فشل التحقق من {key}"
            print(f"   ✅ {key}: مشفّر (طول={len(encrypted)})")
        else:
            db[key] = ''
            print(f"   ⚪ {key}: فارغ")

    # حفظ
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print()
    print("=" * 65)
    print("✅ تم الإصلاح بنجاح!")
    print("=" * 65)
    print(f"📁 Config: {config_file}")
    print(f"🔑 Key:    {secrets_manager.key_path}")
    print()
    print("⚠️  احتفظ بنسخة من master.key في مكان آمن!")
    print("   فقدانه يعني فقدان كل القيم المشفّرة.")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(fix_passwords())