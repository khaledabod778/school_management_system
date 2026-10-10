"""
سكربت تهيئة قاعدة البيانات - إنشاء الجداول والبيانات الأولية.
نسخة محدثة مع معالجة التكرارات.
"""

import sys
import os
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal

# إضافة مسار المشروع
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import select, func

from app.database.connection import db_manager
from app.database.session import init_database, create_tables, session_scope
from app.database.models import (
    Base, Role, User, Employee, AcademicYear, Grade, Section,
    Subject, FeeType, GradeFeeStructure, Permission, RolePermission,
    SchoolInfo, Parent, Student
)
from app.services.auth_service import AuthService
from app.core.enums import (
    AcademicYearStatus, EmployeeStatus, PaymentMethod,
    StudentStatus, EnrollmentType, ParentCategory
)


def create_default_roles(session):
    """إنشاء الأدوار الافتراضية."""
    print("إنشاء الأدوار الافتراضية...")
    
    roles_data = [
        ("مدير النظام", "صلاحيات كاملة للنظام"),
        ("مدير عام", "إدارة شاملة للمدرسة"),
        ("محاسب", "إدارة الشؤون المالية"),
        ("مدخل بيانات", "إدخال البيانات"),
        ("أخصائي اجتماعي", "متابعة الطلاب"),
        ("معلم", "رصد الدرجات والحضور"),
    ]
    
    created_roles = {}
    for role_name, description in roles_data:
        existing = session.execute(
            select(Role).where(Role.role_name == role_name)
        ).scalar_one_or_none()
        
        if not existing:
            role = Role(role_name=role_name, description=description)
            session.add(role)
            session.flush()
            created_roles[role_name] = role
            print(f"  - تم إنشاء الدور: {role_name}")
        else:
            created_roles[role_name] = existing
            print(f"  - الدور موجود: {role_name}")
    
    session.commit()
    return created_roles


def create_default_permissions(session, roles):
    """إنشاء الصلاحيات الافتراضية."""
    print("\nإنشاء الصلاحيات الافتراضية...")
    
    modules = [
        "لوحة التحكم", "لوحة المحاسب", "التهيئة الأكاديمية", "إدارة الطلاب", 
        "أولياء الأمور", "وثائق الطلاب", "توزيع الطلاب", "رسوم الطلاب", "سندات القبض",
        "كشف حساب طالب", "الموظفين والمعلمين", "سندات الصرف", "البدلات والخصومات",
        "السلف المالية", "كشف الرواتب", "كشف حساب موظف", "رصد الدرجات",
        "الشهادات والأوائل", "الحضور والغياب", "الواجبات المنزلية",
        "المتابعة السلوكية", "الجداول الدراسية", "المستخدمين", "الصلاحيات",
        "الإشعارات", "التقارير", "الإعدادات",
    ]
    
    permission_ids = []
    session.query(Permission).delete()

    for i, module in enumerate(modules):
        existing = session.execute(
            select(Permission).where(Permission.module_name == module)
        ).scalar_one_or_none()
        
        if not existing:
            permission = Permission(
                module_name=module,
                permission_key=f"module_{i}"
            )
            session.add(permission)
            session.flush()
            permission_ids.append(permission)
            print(f"  - تم إنشاء صلاحية: {module}")
        else:
            permission_ids.append(existing)
            print(f"  - الصلاحية موجودة: {module}")
    
    # منح صلاحيات كاملة لمدير النظام
    admin_role = roles.get("مدير النظام")
    if admin_role:
        for permission in permission_ids:
            existing_rp = session.execute(
                select(RolePermission).where(
                    RolePermission.role_id == admin_role.id,
                    RolePermission.permission_id == permission.id
                )
            ).scalar_one_or_none()
            
            if not existing_rp:
                rp = RolePermission(
                    role_id=admin_role.id,
                    permission_id=permission.id,
                    can_view=True, can_add=True, can_edit=True,
                    can_delete=True, can_print=True, can_cancel=True
                )
                session.add(rp)
            else:
                # تحديث الصلاحيات الموجودة
                existing_rp.can_view = True
                existing_rp.can_add = True
                existing_rp.can_edit = True
                existing_rp.can_delete = True
                existing_rp.can_print = True
                existing_rp.can_cancel = True
        
        print("  - تم منح صلاحيات كاملة لمدير النظام")
    
    # منح صلاحيات محدودة للمعلم
    teacher_role = roles.get("معلم")
    if teacher_role:
        teacher_modules = ["الحضور والغياب", "رصد الدرجات", "الواجبات المنزلية"]
        for permission in permission_ids:
            if permission.module_name in teacher_modules:
                existing_rp = session.execute(
                    select(RolePermission).where(
                        RolePermission.role_id == teacher_role.id,
                        RolePermission.permission_id == permission.id
                    )
                ).scalar_one_or_none()
                
                if not existing_rp:
                    rp = RolePermission(
                        role_id=teacher_role.id,
                        permission_id=permission.id,
                        can_view=True, can_add=True, can_edit=True,
                        can_delete=False, can_print=True, can_cancel=False
                    )
                    session.add(rp)
                else:
                    # تحديث الصلاحيات الموجودة
                    existing_rp.can_view = True
                    existing_rp.can_add = True
                    existing_rp.can_edit = True
                    existing_rp.can_delete = False
                    existing_rp.can_print = True
                    existing_rp.can_cancel = False
        
        print("  - تم منح صلاحيات للمعلم")
    
    session.commit()
    print("  - تم حفظ الصلاحيات بنجاح")

def create_default_admin(session, roles):
    """إنشاء المستخدم الافتراضي."""
    print("\nإنشاء المستخدم الافتراضي...")
    
    # إنشاء موظف للمدير
    admin_employee = session.execute(
        select(Employee).where(Employee.full_name == "مدير النظام")
    ).scalar_one_or_none()
    
    if not admin_employee:
        admin_employee = Employee(
            full_name="مدير النظام",
            job_title="مدير نظام",
            primary_phone="0000000000",
            basic_salary=Decimal("0.00"),
            status=EmployeeStatus.ACTIVE.value,
            payment_method="نقداً"  # تغيير من 'نقداً' إلى 'نقدي'
        )
        session.add(admin_employee)
        session.flush()
        print("  - تم إنشاء موظف مدير النظام")
    
    # إنشاء المستخدم
    admin_user = session.execute(
        select(User).where(User.username == "admin")
    ).scalar_one_or_none()
    
    if not admin_user:
        admin_role = roles.get("مدير النظام")
        password_hash, _ = AuthService.hash_password("admin123")
        
        admin_user = User(
            employee_id=admin_employee.id,
            username="admin",
            password_hash=password_hash,
            role_id=admin_role.id,
            status='نشط'
        )
        session.add(admin_user)
        session.flush()
        print("  - تم إنشاء المستخدم الافتراضي")
        print("    اسم المستخدم: admin")
        print("    كلمة المرور: admin123")
    else:
        print("  - المستخدم الافتراضي موجود")
    
    session.commit()

def create_academic_year(session):
    """إنشاء السنة الدراسية الافتراضية."""
    print("\nإنشاء السنة الدراسية الافتراضية...")
    
    current_year = date.today().year
    year_name = f"{current_year}-{current_year + 1}"
    hijri_year = f"{current_year - 578}هـ"
    
    existing = session.execute(
        select(AcademicYear).where(AcademicYear.year_name_gregorian == year_name)
    ).scalar_one_or_none()
    
    if not existing:
        academic_year = AcademicYear(
            year_name_gregorian=year_name,
            year_name_hijri=hijri_year,
            start_date=date(current_year, 9, 1),
            end_date=date(current_year + 1, 6, 30),
            is_current=True,
            status=AcademicYearStatus.CURRENT.value,
            is_closed=False
        )
        session.add(academic_year)
        session.flush()
        print(f"  - تم إنشاء السنة الدراسية: {year_name}")
        session.commit()
        return academic_year
    else:
        print(f"  - السنة الدراسية موجودة: {year_name}")
        return existing


def create_grades_and_sections(session):
    """إنشاء الصفوف والشعب الافتراضية."""
    print("\nإنشاء الصفوف والشعب...")
    
    grades_data = [
        ("الأول الأساسي", "الابتدائي", 30),
        ("الثاني الأساسي", "الابتدائي", 30),
        ("الثالث الأساسي", "الابتدائي", 30),
        ("الرابع الأساسي", "الابتدائي", 30),
        ("الخامس الأساسي", "الابتدائي", 30),
        ("السادس الأساسي", "الابتدائي", 30),
        ("السابع الأساسي", "الإعدادي", 35),
        ("الثامن الأساسي", "الإعدادي", 35),
        ("التاسع الأساسي", "الإعدادي", 35),
        ("الأول الثانوي", "الثانوي", 40),
        ("الثاني الثانوي", "الثانوي", 40),
        ("الثالث الثانوي", "الثانوي", 40),
    ]
    
    section_names = ["أ", "ب", "ج"]
    created_grades = []
    
    for grade_name, stage, capacity in grades_data:
        grade = session.execute(
            select(Grade).where(Grade.grade_name == grade_name)
        ).scalar_one_or_none()
        
        if not grade:
            grade = Grade(
                grade_name=grade_name,
                stage_name=stage,
                max_capacity=capacity
            )
            session.add(grade)
            session.flush()
            print(f"  - تم إنشاء الصف: {grade_name}")
        
        # إنشاء الشعب
        for section_name in section_names:
            section = session.execute(
                select(Section).where(
                    Section.grade_id == grade.id,
                    Section.section_name == section_name
                )
            ).scalar_one_or_none()
            
            if not section:
                section = Section(
                    grade_id=grade.id,
                    section_name=section_name,
                    capacity=capacity
                )
                session.add(section)
        
        created_grades.append(grade)
    
    session.commit()
    print(f"  - تم إنشاء {len(created_grades)} صفوف مع الشعب")
    return created_grades


def create_subjects(session):
    """إنشاء المواد الدراسية."""
    print("\nإنشاء المواد الدراسية...")
    
    subjects = [
        ("القرآن الكريم", 50, 100),
        ("التربية الإسلامية", 50, 100),
        ("اللغة العربية", 50, 100),
        ("اللغة الإنجليزية", 50, 100),
        ("الرياضيات", 50, 100),
        ("العلوم", 50, 100),
        ("الدراسات الاجتماعية", 50, 100),
        ("الحاسوب", 50, 100),
        ("التربية الفنية", 50, 100),
        ("التربية البدنية", 50, 100),
    ]
    
    for subject_name, min_score, max_score in subjects:
        subject = session.execute(
            select(Subject).where(Subject.subject_name == subject_name)
        ).scalar_one_or_none()
        
        if not subject:
            subject = Subject(
                subject_name=subject_name,
                min_pass_score=Decimal(str(min_score)),
                max_score=Decimal(str(max_score))
            )
            session.add(subject)
            print(f"  - تم إنشاء المادة: {subject_name}")
    
    session.commit()


def create_fee_types(session):
    """إنشاء أنواع الرسوم."""
    print("\nإنشاء أنواع الرسوم...")
    
    fee_types = [
        "رسوم دراسية",
        "رسوم تسجيل",
        "زي مدرسي",
        "كتب",
        "مواصلات",
        "أنشطة",
    ]
    
    for fee_name in fee_types:
        fee_type = session.execute(
            select(FeeType).where(FeeType.fee_name == fee_name)
        ).scalar_one_or_none()
        
        if not fee_type:
            fee_type = FeeType(fee_name=fee_name)
            session.add(fee_type)
            print(f"  - تم إنشاء نوع الرسوم: {fee_name}")
    
    session.commit()


def create_school_info(session):
    """إنشاء بيانات المدرسة."""
    print("\nإنشاء بيانات المدرسة...")
    
    school = session.execute(
        select(SchoolInfo).limit(1)
    ).scalar_one_or_none()
    
    if not school:
        school = SchoolInfo(
            school_name_ar="مدرسة النور الأهلية",
            school_name_en="Al-Noor Private School",
            principal_name="",
            license_number="",
            phone_primary="",
            phone_secondary="",
            email="",
            address_detail="",
            terms_and_conditions="شروط وأحكام المدرسة"
        )
        session.add(school)
        session.flush()
        print("  - تم إنشاء بيانات المدرسة الافتراضية")
    
    session.commit()


def main():
    """الدالة الرئيسية."""
    print("=" * 60)
    print("تهيئة قاعدة بيانات نظام إدارة المدرسة")
    print("=" * 60)
    
    # تهيئة قاعدة البيانات
    print("\n1. الاتصال بقاعدة البيانات...")
    init_database(use_local=True)
    
    if not db_manager.check_connection():
        print("✗ فشل الاتصال بقاعدة البيانات")
        print("يرجى التأكد من تشغيل PostgreSQL والإعدادات صحيحة")
        sys.exit(1)
    
    print("✓ تم الاتصال بقاعدة البيانات")
    
    # إنشاء الجداول
    print("\n2. إنشاء الجداول...")
    create_tables()
    print("✓ تم إنشاء الجداول")
    
    # إنشاء البيانات الافتراضية
    print("\n3. إنشاء البيانات الافتراضية...")
    
    with session_scope() as session:
        # الأدوار
        roles = create_default_roles(session)
        
        # الصلاحيات
        create_default_permissions(session, roles)
        
        # المستخدم الافتراضي
        create_default_admin(session, roles)
        
        # السنة الدراسية
        create_academic_year(session)
        
        # الصفوف والشعب
        create_grades_and_sections(session)
        
        # المواد
        create_subjects(session)
        
        # أنواع الرسوم
        create_fee_types(session)
        
        # بيانات المدرسة
        create_school_info(session)
    
    print("\n" + "=" * 60)
    print("✓ تمت تهيئة قاعدة البيانات بنجاح")
    print("=" * 60)
    print("\nمعلومات الدخول الافتراضية:")
    print("  اسم المستخدم: admin")
    print("  كلمة المرور: admin123")
    print("\nيمكنك الآن تشغيل النظام باستخدام: python run.py")


if __name__ == "__main__":
    main()