"""
سكربت مزامنة البيانات من القاعدة المحلية إلى السحابية.
معالج Foreign Keys و Sequential IDs.
"""

import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine, text, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

from app.core.config import config_manager
from app.database.models import (
    Base, Role, User, Employee, AcademicYear, Grade, Section,
    Subject, Student, Parent, StudentFee, FeeInstallment, Receipt,
    ExpenseVoucher, PayrollRecord, EmployeeLoan, EmployeeAllowanceDeduction,
    DailyAttendance, MonthlyEvaluation, TermExamScore, Homework,
    BehavioralRecord, Notification, NotificationLog, GradeFeeStructure,
    FeeType, TeacherSubjectSection, WeeklySchedule, MonthlyExamSchedule,
    FinalExamSchedule, SchoolInfo, StudentDocument, StudentAcademicHistory,
    RolePermission, Permission, SystemAuditLog, PrintArchive,
    ImportExportLog, AnnualClosingLog, BackupLog, ParentDevice
)


def build_connection_string(use_cloud: bool = True) -> str:
    """بناء سلسلة الاتصال."""
    config = config_manager.database_config
    
    if use_cloud:
        host = config.cloud_host
        port = config.cloud_port
        db_name = config.cloud_db_name
        user = config.cloud_user
        password = config.cloud_password
        sslmode = config.cloud_sslmode
    else:
        host = config.local_host
        port = config.local_port
        db_name = config.local_db_name
        user = config.local_user
        password = config.local_password
        sslmode = "prefer"
    
    encoded_password = quote_plus(password)
    
    return (
        f"postgresql+psycopg2://{user}:{encoded_password}"
        f"@{host}:{port}/{db_name}?sslmode={sslmode}"
    )


def get_models_in_insertion_order():
    """
    قائمة النماذج بالترتيب الصحيح للإدراج (الآباء أولاً).
    
    الترتيب مهم جداً:
    1. الجداول المستقلة (بدون Foreign Keys)
    2. الجداول التي تعتمد على المستوى الأول
    3. الجداول التي تعتمد على المستوى الثاني
    ... وهكذا
    """
    return [
        # ===== المستوى 0: جداول مستقلة =====
        SchoolInfo,
        Role,
        Permission,
        FeeType,
        AcademicYear,
        Grade,
        Subject,
        
        # ===== المستوى 1: تعتمد على المستوى 0 =====
        Employee,              # لا يعتمد على Employee آخر
        Parent,                # لا يعتمد على أحد
        Section,               # يعتمد على Grade
        RolePermission,        # يعتمد على Role + Permission
        GradeFeeStructure,     # يعتمد على AcademicYear + Grade + FeeType
        
        # ===== المستوى 2: تعتمد على المستوى 1 =====
        User,                  # يعتمد على Employee + Role
        ParentDevice,          # يعتمد على Parent
        
        # ===== المستوى 3: الطلاب =====
        Student,               # يعتمد على AcademicYear + Grade + Section + Parent
        TeacherSubjectSection, # يعتمد على AcademicYear + Grade + Section + Subject + Employee
        
        # ===== المستوى 4: تعتمد على Student =====
        StudentAcademicHistory,
        StudentDocument,
        StudentFee,            # يعتمد على Student + AcademicYear
        DailyAttendance,
        MonthlyEvaluation,
        TermExamScore,
        Homework,
        BehavioralRecord,
        
        # ===== المستوى 5: تعتمد على StudentFee =====
        FeeInstallment,        # يعتمد على StudentFee
        
        # ===== المستوى 6: تعتمد على FeeInstallment + User =====
        Receipt,               # يعتمد على Student + FeeInstallment + User
        ExpenseVoucher,        # يعتمد على User
        EmployeeAllowanceDeduction,
        EmployeeLoan,
        PayrollRecord,
        
        # ===== الجداول =====
        WeeklySchedule,
        MonthlyExamSchedule,
        FinalExamSchedule,
        
        # ===== الإشعارات =====
        Notification,          # يعتمد على User + Grade + Section
        NotificationLog,       # يعتمد على Notification + Parent
        
        # ===== النظام =====
        SystemAuditLog,        # يعتمد على User
        PrintArchive,          # يعتمد على User
        ImportExportLog,       # يعتمد على User
        AnnualClosingLog,      # يعتمد على AcademicYear + User
        BackupLog,             # يعتمد على User
    ]


def truncate_all_tables(engine):
    """
    حذف جميع بيانات الجداول باستخدام TRUNCATE CASCADE.
    هذا يتجاوز مشكلة Foreign Keys.
    """
    print("\nحذف جميع البيانات من السحابة (TRUNCATE CASCADE)...")
    
    with engine.connect() as conn:
        # الحصول على جميع الجداول في قاعدة البيانات
        result = conn.execute(text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """))
        
        tables = [row[0] for row in result]
        
        if not tables:
            print("  لا توجد جداول للحذف")
            return
        
        # استخدام TRUNCATE مع CASCADE
        # نجرب معاملة واحدة لجميع الجداول
        try:
            tables_str = ', '.join([f'"{t}"' for t in tables])
            conn.execute(text(f'TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE'))
            conn.commit()
            print(f"  ✓ تم حذف بيانات {len(tables)} جدول")
        except Exception as e:
            conn.rollback()
            print(f"  ⚠ فشل TRUNCATE الجماعي: {str(e)}")
            print("  محاولة حذف كل جدول على حدة...")
            
            for table in tables:
                try:
                    conn.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))
                    conn.commit()
                    print(f"    ✓ {table}")
                except Exception as e2:
                    conn.rollback()
                    print(f"    ⚠ {table}: {str(e2)}")


def disable_foreign_keys(engine):
    """تعطيل Foreign Keys مؤقتاً."""
    with engine.connect() as conn:
        conn.execute(text("SET session_replication_role = 'replica'"))
        conn.commit()


def enable_foreign_keys(engine):
    """إعادة تفعيل Foreign Keys."""
    with engine.connect() as conn:
        conn.execute(text("SET session_replication_role = 'origin'"))
        conn.commit()


def sync_table(source_engine, target_engine, model, batch_size=500):
    """مزامنة جدول واحد بدون حذف (الحذف تم مسبقاً بـ TRUNCATE)."""
    table_name = model.__tablename__
    
    print(f"  → مزامنة: {table_name}...", end=" ", flush=True)
    
    try:
        SourceSession = sessionmaker(bind=source_engine)
        TargetSession = sessionmaker(bind=target_engine)
        
        source_session = SourceSession()
        target_session = TargetSession()
        
        try:
            # قراءة البيانات من المصدر
            records = source_session.query(model).all()
            
            if not records:
                print("لا توجد بيانات")
                return 0
            
            # تحويل السجلات إلى dicts
            records_dicts = []
            for record in records:
                record_dict = {}
                for column in model.__table__.columns:
                    record_dict[column.name] = getattr(record, column.name)
                records_dicts.append(record_dict)
            
            # إدراج على دفعات
            count = 0
            for i in range(0, len(records_dicts), batch_size):
                batch = records_dicts[i:i + batch_size]
                try:
                    target_session.execute(model.__table__.insert(), batch)
                    target_session.commit()
                    count += len(batch)
                except Exception as e:
                    target_session.rollback()
                    # محاولة إدراج سجل بسجل لتحديد المشكلة
                    for single_record in batch:
                        try:
                            target_session.execute(model.__table__.insert(), single_record)
                            target_session.commit()
                            count += 1
                        except Exception as inner_e:
                            target_session.rollback()
                            print(f"\n    ⚠ تخطي سجل: {str(inner_e)[:100]}")
            
            print(f"✓ {count} سجل")
            return count
            
        finally:
            source_session.close()
            target_session.close()
    
    except Exception as e:
        print(f"✗ خطأ: {str(e)}")
        raise


def reset_sequences(target_engine):
    """إعادة تعيين sequences للسيريال."""
    print("\nإعادة تعيين sequences...")
    
    try:
        with target_engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    t.table_name,
                    c.column_name,
                    pg_get_serial_sequence(quote_ident(t.table_name), c.column_name) as seq_name
                FROM information_schema.tables t
                JOIN information_schema.columns c 
                    ON t.table_name = c.table_name 
                    AND t.table_schema = c.table_schema
                WHERE t.table_schema = 'public'
                    AND t.table_type = 'BASE TABLE'
                    AND c.column_default LIKE 'nextval%'
                    AND pg_get_serial_sequence(quote_ident(t.table_name), c.column_name) IS NOT NULL
            """))
            
            sequences = list(result)
            
            for table_name, column_name, seq_name in sequences:
                try:
                    # الحصول على MAX
                    max_result = conn.execute(text(
                        f'SELECT COALESCE(MAX("{column_name}"), 0) FROM "{table_name}"'
                    ))
                    max_val = max_result.scalar() or 0
                    
                    # تعيين القيمة التالية
                    conn.execute(text(
                        f"SELECT setval('{seq_name}', {max_val}, true)"
                    ))
                    conn.commit()
                    print(f"  ✓ {table_name}.{column_name} = {max_val}")
                except Exception as e:
                    conn.rollback()
                    print(f"  ⚠ {table_name}.{column_name}: {str(e)[:80]}")
    
    except Exception as e:
        print(f"  ⚠ فشل إعادة تعيين sequences: {str(e)}")


def verify_sync(source_engine, target_engine, models):
    """التحقق من نجاح المزامنة."""
    print("\nالتحقق من المزامنة:")
    print(f"{'الجدول':<30} {'المصدر':<10} {'الهدف':<10} {'الحالة'}")
    print("-" * 70)
    
    source_session = sessionmaker(bind=source_engine)()
    target_session = sessionmaker(bind=target_engine)()
    
    try:
        total_source = 0
        total_target = 0
        
        for model in models:
            table_name = model.__tablename__
            
            try:
                source_count = source_session.query(model).count()
                target_count = target_session.query(model).count()
                
                total_source += source_count
                total_target += target_count
                
                status = "✓" if source_count == target_count else "✗"
                print(f"{table_name:<30} {source_count:<10} {target_count:<10} {status}")
            except Exception as e:
                print(f"{table_name:<30} {'ERROR':<10} {'ERROR':<10} {str(e)[:20]}")
        
        print("-" * 70)
        print(f"{'الإجمالي':<30} {total_source:<10} {total_target:<10} "
              f"{'✓' if total_source == total_target else '✗'}")
    
    finally:
        source_session.close()
        target_session.close()


def main():
    """الدالة الرئيسية."""
    print("=" * 70)
    print("مزامنة قاعدة البيانات إلى السحابة")
    print("=" * 70)
    
    config = config_manager.database_config
    if not config.cloud_host:
        print("✗ لم يتم تكوين الخادم السحابي في config.json")
        sys.exit(1)
    
    local_url = build_connection_string(use_cloud=False)
    cloud_url = build_connection_string(use_cloud=True)
    
    print(f"\nالمصدر (محلي): {config.local_host}/{config.local_db_name}")
    print(f"الهدف (سحابي): {config.cloud_host}:{config.cloud_port}/{config.cloud_db_name}")
    print(f"SSL Mode: {config.cloud_sslmode}")
    
    print("\n" + "!" * 70)
    print("تحذير: سيتم حذف جميع البيانات الموجودة على السحابة!")
    print("!" * 70)
    
    confirm = input("\nهل تريد المتابعة؟ اكتب 'yes' للتأكيد: ")
    if confirm.lower() != 'yes':
        print("تم الإلغاء")
        sys.exit(0)
    
    # ===== الاتصال =====
    print("\n1. الاتصال بقواعد البيانات...")
    try:
        local_engine = create_engine(local_url, connect_args={'sslmode': 'prefer'})
        cloud_engine = create_engine(
            cloud_url, 
            connect_args={'sslmode': config.cloud_sslmode, 'connect_timeout': 30}
        )
        
        with local_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("  ✓ المصدر (محلي)")
        
        with cloud_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("  ✓ الهدف (سحابي)")
        
    except Exception as e:
        print(f"✗ فشل الاتصال: {str(e)}")
        sys.exit(1)
    
    # ===== إنشاء الجداول =====
    print("\n2. إنشاء الجداول في السحابة (إذا لم تكن موجودة)...")
    try:
        Base.metadata.create_all(cloud_engine)
        print("  ✓ تم التحقق من الجداول")
    except Exception as e:
        print(f"✗ فشل إنشاء الجداول: {str(e)}")
        sys.exit(1)
    
    # ===== حذف البيانات =====
    print("\n3. حذف البيانات القديمة من السحابة...")
    truncate_all_tables(cloud_engine)
    
    # ===== مزامنة الجداول =====
    print("\n4. مزامنة البيانات...")
    models = get_models_in_insertion_order()
    
    total_records = 0
    failed_tables = []
    
    for model in models:
        try:
            count = sync_table(local_engine, cloud_engine, model)
            total_records += count
        except Exception as e:
            failed_tables.append((model.__tablename__, str(e)))
    
    # ===== إعادة تعيين sequences =====
    print("\n5. إعادة تعيين sequences...")
    reset_sequences(cloud_engine)
    
    # ===== التحقق =====
    print("\n6. التحقق من المزامنة...")
    verify_sync(local_engine, cloud_engine, models)
    
    # ===== الملخص =====
    print("\n" + "=" * 70)
    print(f"✓ اكتملت المزامنة: {total_records} سجل")
    
    if failed_tables:
        print(f"\n⚠ فشل في {len(failed_tables)} جدول:")
        for table, error in failed_tables:
            print(f"  - {table}: {error[:80]}")
    else:
        print("✓ جميع الجداول تمت مزامنتها بنجاح")
    
    print("=" * 70)
    
    # تنظيف
    local_engine.dispose()
    cloud_engine.dispose()


if __name__ == "__main__":
    main()