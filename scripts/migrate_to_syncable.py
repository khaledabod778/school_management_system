"""
ترحيل الجداول الحالية لإضافة حقول المزامنة (SyncableMixin).

يضيف الحقول التالية لكل جدول:
- sync_uuid: UUID فريد لكل صف
- sync_version: رقم النسخة
- sync_updated_at: آخر تعديل
- sync_source: مصدر التعديل
- is_synced: هل تمت مزامنته
"""

import sys
import uuid
from pathlib import Path

# إضافة مسار المشروع
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import logging
from sqlalchemy import text, inspect

from app.database.session import init_database, session_scope
from app.database.connection import db_manager
from app.database.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ✅ الجداول التي تحتاج مزامنة
SYNCABLE_TABLES = [
    # الطلاب والكادر
    'students', 'parents', 'employees', 'users',
    # الأكاديمي
    'academic_years', 'grades', 'sections', 'subjects',
    'teacher_subject_sections',
    # المالية
    'grade_fee_structures', 'fee_types', 'student_fees',
    'fee_installments', 'receipts', 'expense_vouchers',
    'payroll_records', 'employee_loans',
    'employee_allowances_deductions',
    # المتابعة
    'daily_attendance', 'monthly_evaluations', 'term_exam_scores',
    'homeworks', 'behavioral_records', 'notifications',
    # الجداول
    'weekly_schedules', 'monthly_exam_schedules',
    'final_exam_schedules',
    # أخرى
    'school_info', 'student_documents',
]


def add_sync_columns(table_name: str):
    """إضافة أعمدة المزامنة لجدول."""
    with session_scope() as session:
        try:
            # ✅ فحص الأعمدة الحالية
            inspector = inspect(session.bind)
            existing_columns = {
                col['name'] 
                for col in inspector.get_columns(table_name)
            }
            
            # ✅ إضافة الأعمدة الناقصة
            columns_to_add = {
                'sync_uuid': 'VARCHAR(36)',
                'sync_version': 'INTEGER DEFAULT 1',
                'sync_updated_at': 'TIMESTAMP DEFAULT NOW()',
                'sync_source': "VARCHAR(20) DEFAULT 'local'",
                'is_synced': 'BOOLEAN DEFAULT FALSE',
            }
            
            added = []
            for col_name, col_type in columns_to_add.items():
                if col_name not in existing_columns:
                    session.execute(text(
                        f'ALTER TABLE "{table_name}" '
                        f'ADD COLUMN {col_name} {col_type}'
                    ))
                    added.append(col_name)
            
            if added:
                session.commit()
                logger.info(f"✅ {table_name}: أُضيفت {len(added)} أعمدة")
            
            # ✅ ملء sync_uuid للصفوف الموجودة
            session.execute(text(f'''
                UPDATE "{table_name}"
                SET sync_uuid = gen_random_uuid()::text
                WHERE sync_uuid IS NULL
            '''))
            
            # ✅ إنشاء فهرس فريد على sync_uuid
            try:
                session.execute(text(f'''
                    CREATE UNIQUE INDEX IF NOT EXISTS 
                    idx_{table_name}_sync_uuid 
                    ON "{table_name}" (sync_uuid)
                '''))
            except Exception:
                pass
            
            # ✅ إنشاء فهرس على is_synced
            try:
                session.execute(text(f'''
                    CREATE INDEX IF NOT EXISTS 
                    idx_{table_name}_is_synced 
                    ON "{table_name}" (is_synced)
                '''))
            except Exception:
                pass
            
            session.commit()
            
        except Exception as e:
            logger.error(f"❌ {table_name}: {str(e)}")
            raise


def create_sync_tables():
    """إنشاء جداول المزامنة."""
    try:
        # استيراد النماذج لإنشاء الجداول
        from app.database.models.sync import (
            SyncQueue, SyncConflict, SyncMetadata, SyncInstance
        )
        
        Base.metadata.create_all(
            db_manager.engine,
            tables=[
                SyncQueue.__table__,
                SyncConflict.__table__,
                SyncMetadata.__table__,
                SyncInstance.__table__,
            ]
        )
        logger.info("✅ تم إنشاء جداول المزامنة")
    except Exception as e:
        logger.error(f"❌ فشل إنشاء جداول المزامنة: {str(e)}")
        raise


def main():
    """الدالة الرئيسية."""
    print("=" * 70)
    print("🚀 ترحيل الجداول إلى نظام المزامنة")
    print("=" * 70)
    
    # 1. تهيئة قاعدة البيانات
    print("\n📌 تهيئة قاعدة البيانات...")
    init_database(use_local=True)
    
    # 2. إنشاء جداول المزامنة
    print("\n📌 إنشاء جداول المزامنة...")
    create_sync_tables()
    
    # 3. ترحيل الجداول
    print(f"\n📌 ترحيل {len(SYNCABLE_TABLES)} جدول...")
    
    success = 0
    failed = 0
    
    for table_name in SYNCABLE_TABLES:
        try:
            add_sync_columns(table_name)
            success += 1
        except Exception as e:
            failed += 1
            print(f"   ❌ فشل {table_name}: {e}")
    
    print("\n" + "=" * 70)
    print(f"✅ نجح: {success} جدول")
    print(f"❌ فشل: {failed} جدول")
    print("=" * 70)


if __name__ == "__main__":
    main()