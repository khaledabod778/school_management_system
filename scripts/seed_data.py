"""
سكربت تعبئة قاعدة البيانات ببيانات تجريبية شاملة.
"""

import sys
import random
from pathlib import Path
from datetime import date, datetime, timedelta
from decimal import Decimal

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import select, func

from app.database.connection import db_manager
from app.database.session import init_database, session_scope
from app.database.models import (
    Role, User, Employee, AcademicYear, Grade, Section,
    Subject, FeeType, GradeFeeStructure, Permission, RolePermission,
    SchoolInfo, Parent, Student, StudentFee, FeeInstallment,
    Receipt, ExpenseVoucher, DailyAttendance, MonthlyEvaluation,
    TermExamScore, Homework, BehavioralRecord, WeeklySchedule,
    EmployeeAllowanceDeduction, EmployeeLoan, PayrollRecord,
    Notification, NotificationLog, TeacherSubjectSection
)
from app.services.auth_service import AuthService
from app.core.enums import (
    AcademicYearStatus, EmployeeStatus, PaymentMethod,
    StudentStatus, EnrollmentType, ParentCategory
)

# قوائم الأسماء العربية
MALE_NAMES = [
    "محمد أحمد", "علي حسن", "عمر خالد", "يوسف إبراهيم", "خالد عبدالله",
    "أحمد محمد", "سعيد علي", "عبدالله عمر", "حسن يوسف", "إبراهيم خليل",
    "محمود سامي", "طلال ناصر", "فهد سعود", "سلطان محمد", "راشد علي",
    "ناصر عبدالعزيز", "بدر حمد", "ماجد فهد", "وليد طلال", "زياد هشام",
    "أنس محمد", "بلال أحمد", "تميم خالد", "حمزة علي", "داود سليمان",
    "زكريا يحيى", "صالح إبراهيم", "طارق زياد", "عاصم عمر", "فارس خالد",
    "قيس مالك", "كرم نبيل", "لؤي سامر", "مازن هاني", "نضال فؤاد",
    "هاشم رائد", "وائل سامي", "يحيى عادل", "آدم نوح", "أكرم وجيه",
]

FEMALE_NAMES = [
    "فاطمة علي", "عائشة محمد", "مريم أحمد", "زينب حسن", "خديجة عمر",
    "سارة خالد", "نورة عبدالله", "رنا يوسف", "لينا إبراهيم", "هدى سامي",
    "أمل ناصر", "بسمة فهد", "تقى سعود", "جنات محمد", "حنان علي",
    "دينا حمد", "رحمة فهد", "سلمى طلال", "شهد زياد", "صفاء هشام",
    "ضحى محمد", "غادة أحمد", "فرح خالد", "قمر علي", "لمى حسن",
    "مودة عمر", "نجلاء خالد", "هبة عبدالله", "وسن يوسف", "ياسمين إبراهيم",
]

MOTHER_NAMES = [
    "فاطمة", "عائشة", "مريم", "زينب", "خديجة", "سارة", "نورة", "رنا",
    "لينا", "هدى", "أمل", "بسمة", "تقى", "جنات", "حنان", "دينا",
    "رحمة", "سلمى", "شهد", "صفاء", "ضحى", "غادة", "فرح", "قمر",
]

FATHER_NAMES = [
    "أحمد", "محمد", "علي", "حسن", "عمر", "خالد", "يوسف", "إبراهيم",
    "عبدالله", "سعيد", "محمود", "طلال", "فهد", "سلطان", "راشد",
    "ناصر", "بدر", "ماجد", "وليد", "زياد", "أنس", "بلال", "تميم",
]

EMPLOYEE_NAMES = [
    "أحمد محمد العمراني", "خالد عبدالله الحكيمي", "سعيد علي المخلافي",
    "عبدالله عمر الشرعبي", "حسن يوسف الحمادي", "إبراهيم خليل النهاري",
    "محمود سامي الريمي", "طلال ناصر الحضرمي", "فهد سعود العدني",
    "سلطان محمد الإبي", "راشد علي الذماري", "ناصر عبدالعزيز الضالعي",
    "بدر حمد الجوفي", "ماجد فهد المأربي", "وليد طلال الشميري",
    "زياد هشام العنسي", "أنس محمد الحدي", "بلال أحمد الرازحي",
    "فاطمة علي الشرعبي", "عائشة محمد الحكيمي", "مريم أحمد المخلافي",
    "زينب حسن العمراني", "خديجة عمر الحمادي", "سارة خالد النهاري",
    "نورة عبدالله الريمي", "رنا يوسف الحضرمي", "لينا إبراهيم العدني",
    "هدى سامي الإبي", "أمل ناصر الذماري", "بسمة فهد الضالعي",
]

JOB_TITLES = [
    "معلم رياضيات", "معلم لغة عربية", "معلم لغة إنجليزية", "معلم علوم",
    "معلم دراسات اجتماعية", "معلم حاسوب", "معلم تربية إسلامية",
    "معلم قرآن كريم", "معلم تربية فنية", "معلم تربية بدنية",
    "مدير عام", "وكيل المدرسة", "محاسب", "أمين مكتبة",
    "مشرف تربوي", "أخصائي اجتماعي", "سكرتير", "ممرض",
]

GOVERNORATES = ["صنعاء", "عدن", "تعز", "الحديدة", "إب", "ذمار", "حضرموت", "المكلا"]

DISTRICTS = ["المدينة", "المركز", "الشمالية", "الجنوبية", "الشرقية", "الغربية"]

VILLAGES = ["القرية", "الحارة", "الحي", "المنطقة", "الشارع"]

# ============ الدوال المساعدة ============

def generate_phone() -> str:
    """توليد رقم هاتف يمني."""
    return f"7{random.randint(70, 79)}{random.randint(100, 999)}{random.randint(100, 999)}"

def random_date(start_year: int = 1980, end_year: int = 2015) -> date:
    """توليد تاريخ عشوائي."""
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return date(year, month, day)

def random_birth_date() -> date:
    """توليد تاريخ ميلاد طالب."""
    return random_date(2005, 2018)


# ============ دالة التعبئة الرئيسية ============

def seed_database():
    """تعبئة قاعدة البيانات بالبيانات."""
    print("=" * 70)
    print("تعبئة قاعدة البيانات بالبيانات التجريبية")
    print("=" * 70)
    
    init_database(use_local=True)
    
    if not db_manager.check_connection():
        print("✗ فشل الاتصال بقاعدة البيانات")
        return
    
    with session_scope() as session:
        # 1. السنة الدراسية
        print("\n1. السنوات الدراسية...")
        current_year = date.today().year
        year = session.execute(
            select(AcademicYear).where(AcademicYear.is_current == True)
        ).scalar_one_or_none()
        
        if not year:
            year = session.execute(
                select(AcademicYear).limit(1)
            ).scalar_one()
        
        print(f"   ✓ السنة الحالية: {year.year_name_gregorian}")
        
        # 2. الصفوف والشعب
        print("\n2. الصفوف والشعب...")
        grades = session.execute(select(Grade)).scalars().all()
        sections = session.execute(select(Section)).scalars().all()
        print(f"   ✓ الصفوف: {len(grades)}، الشعب: {len(sections)}")
        
        # 3. المواد
        print("\n3. المواد...")
        subjects = session.execute(select(Subject)).scalars().all()
        print(f"   ✓ المواد: {len(subjects)}")
        
        # 4. أنواع الرسوم
        print("\n4. أنواع الرسوم...")
        fee_types = session.execute(select(FeeType)).scalars().all()
        print(f"   ✓ أنواع الرسوم: {len(fee_types)}")
        
        # 5. الموظفين والمعلمين
        print("\n5. إنشاء الموظفين...")
        employees = []
        used_names = set()
        
        for i in range(30):
            name = random.choice(EMPLOYEE_NAMES)
            while name in used_names:
                name = random.choice(EMPLOYEE_NAMES)
            used_names.add(name)
            
            job_title = random.choice(JOB_TITLES)
            gender = "ذكر" if "فاطمة" not in name and "عائشة" not in name and "مريم" not in name and "زينب" not in name and "خديجة" not in name and "سارة" not in name and "نورة" not in name and "رنا" not in name and "لينا" not in name and "هدى" not in name and "أمل" not in name and "بسمة" not in name else "أنثى"
            
            employee = Employee(
                full_name=name,
                job_title=job_title,
                qualification=random.choice(["بكالوريوس", "ماجستير", "دبلوم", "دكتوراه"]),
                primary_phone=generate_phone(),
                secondary_phone=generate_phone() if random.random() > 0.5 else None,
                gender=gender,
                marital_status=random.choice(["أعزب", "متزوج"]),
                address=random.choice(DISTRICTS),
                status=random.choice(["نشط", "نشط", "نشط", "إجازة"]),
                national_id=str(random.randint(10000000, 99999999)),
                id_issue_place=random.choice(GOVERNORATES),
                id_issue_date=random_date(2010, 2023),
                birth_date=random_date(1975, 2000),
                birth_village=random.choice(VILLAGES),
                birth_district=random.choice(DISTRICTS),
                birth_governorate=random.choice(GOVERNORATES),
                contract_start_date=date(2020, 9, 1),
                contract_end_date=date(2027, 8, 31),
                basic_salary=Decimal(str(random.randint(80000, 250000))),
                payment_method=random.choice(["نقداً", "حساب بنكي", "محفظة إلكترونية"]),
                bank_account_number=str(random.randint(100000, 999999)) if random.random() > 0.5 else None
            )
            session.add(employee)
            session.flush()
            employees.append(employee)
        
        print(f"   ✓ تم إنشاء {len(employees)} موظفاً")
        
        # 6. أولياء الأمور
        print("\n6. إنشاء أولياء الأمور...")
        parents = []
        used_phones = set()
        
        for i in range(100):
            phone = generate_phone()
            while phone in used_phones:
                phone = generate_phone()
            used_phones.add(phone)
            
            father_name = random.choice(FATHER_NAMES)
            parent = Parent(
                full_name=f"{father_name} {random.choice(['محمد', 'علي', 'حسن', 'عمر', 'خالد', 'يوسف'])}",
                primary_phone=phone,
                secondary_phone=generate_phone() if random.random() > 0.6 else None,
                address=f"{random.choice(VILLAGES)} - {random.choice(DISTRICTS)} - {random.choice(GOVERNORATES)}",
                job=random.choice(["مهندس", "طبيب", "معلم", "تاجر", "موظف حكومي", "مقاول", "سائق", "مزارع"]),
                category=random.choice(["عادي", "عادي", "عادي", "VIP", "كفالة"]),
                password_hash=""
            )
            parent.password_hash, _ = AuthService.hash_password("123456")
            session.add(parent)
            session.flush()
            parents.append(parent)
        
        print(f"   ✓ تم إنشاء {len(parents)} ولي أمر")
        
        # 7. الطلاب
        print("\n7. إنشاء الطلاب...")
        students = []
        student_number = 1
        
        for grade in grades:
            grade_sections = [s for s in sections if s.grade_id == grade.id]
            
            for section in grade_sections:
                # عدد الطلاب في كل شعبة (15-25 طالب)
                num_students = random.randint(15, 25)
                
                for _ in range(num_students):
                    gender = random.choice(["ذكر", "أنثى"])
                    
                    if gender == "ذكر":
                        full_name = random.choice(MALE_NAMES)
                    else:
                        full_name = random.choice(FEMALE_NAMES)
                    
                    mother_name = random.choice(MOTHER_NAMES)
                    parent = random.choice(parents)
                    
                    student = Student(
                        student_number=f"ST-{year.id:02d}-{student_number:04d}",
                        full_name=full_name,
                        mother_name=mother_name,
                        gender=gender,
                        nationality="يمني",
                        status=random.choice(["مستمر", "مستمر", "مستمر", "مستمر", "انسحاب"]),
                        enrollment_type=random.choice(["مستجد", "محول", "باقي", "باقي"]),
                        birth_date=random_birth_date(),
                        birth_village=random.choice(VILLAGES),
                        birth_district=random.choice(DISTRICTS),
                        birth_governorate=random.choice(GOVERNORATES),
                        academic_year_id=year.id,
                        grade_id=grade.id,
                        section_id=section.id,
                        parent_id=parent.id,
                        photo_url=None
                    )
                    session.add(student)
                    session.flush()
                    students.append(student)
                    student_number += 1
        
        print(f"   ✓ تم إنشاء {len(students)} طالباً")
        
        # 8. رسوم الصفوف
        print("\n8. إنشاء لائحة الرسوم...")
        
        for grade in grades:
            for fee_type in fee_types:
                existing = session.execute(
                    select(GradeFeeStructure).where(
                        GradeFeeStructure.academic_year_id == year.id,
                        GradeFeeStructure.grade_id == grade.id,
                        GradeFeeStructure.fee_type_id == fee_type.id
                    )
                ).scalar_one_or_none()
                
                if not existing:
                    # تحديد المبلغ حسب نوع الرسوم
                    if fee_type.fee_name == "رسوم دراسية":
                        amount = random.randint(100000, 300000)
                    elif fee_type.fee_name == "رسوم تسجيل":
                        amount = random.randint(10000, 30000)
                    elif fee_type.fee_name == "زي مدرسي":
                        amount = random.randint(15000, 25000)
                    elif fee_type.fee_name == "كتب":
                        amount = random.randint(20000, 40000)
                    elif fee_type.fee_name == "مواصلات":
                        amount = random.randint(30000, 60000)
                    else:
                        amount = random.randint(5000, 15000)
                    
                    fee_structure = GradeFeeStructure(
                        academic_year_id=year.id,
                        grade_id=grade.id,
                        fee_type_id=fee_type.id,
                        amount=Decimal(str(amount))
                    )
                    session.add(fee_structure)
        
        print("   ✓ تم إنشاء لائحة الرسوم")
        
        # 9. رسوم الطلاب والأقساط
        print("\n9. إنشاء رسوم الطلاب والأقساط...")
        
        for student in students[:80]:  # 80 طالب فقط لتسريع العملية
            # حساب مجموع الرسوم
            grade_fees = session.execute(
                select(GradeFeeStructure).where(
                    GradeFeeStructure.grade_id == student.grade_id,
                    GradeFeeStructure.academic_year_id == year.id
                )
            ).scalars().all()
            
            total_fees = sum(f.amount for f in grade_fees)
            
            # خصم عشوائي
            discount = Decimal(str(random.randint(0, 20000)))
            net_total = total_fees - discount
            
            # رصيد سابق
            previous_debt = Decimal(str(random.randint(0, 50000))) if random.random() > 0.7 else Decimal("0")
            
            student_fee = StudentFee(
                student_id=student.id,
                academic_year_id=year.id,
                previous_debt=previous_debt,
                current_year_fees=total_fees,
                discount_amount=discount,
                net_total_required=net_total + previous_debt
            )
            session.add(student_fee)
            session.flush()
            
            # إنشاء الأقساط
            num_installments = random.choice([2, 3, 4])
            installment_amount = net_total / num_installments
            
            # قسط الرصيد السابق
            if previous_debt > 0:
                installment = FeeInstallment(
                    student_fee_id=student_fee.id,
                    installment_type='previous_debt',
                    installment_number=0,
                    installment_name="قسط رصيد سابقة مرحّل",
                    amount=previous_debt,
                    due_date=date(year.start_date.year, 9, 15),
                    is_paid=random.random() > 0.5,
                    paid_amount=previous_debt if random.random() > 0.5 else Decimal("0")
                )
                session.add(installment)
            
            # أقساط السنة
            for i in range(num_installments):
                due_month = 9 + i * 2  # سبتمبر، نوفمبر، يناير، مارس
                if due_month > 12:
                    due_month -= 12
                
                is_paid = random.random() > 0.4
                paid_amount = Decimal(str(installment_amount)) if is_paid else Decimal("0")
                
                installment = FeeInstallment(
                    student_fee_id=student_fee.id,
                    installment_type='regular',
                    installment_number=i + 1,
                    installment_name=f"قسط {i + 1}",
                    amount=Decimal(str(round(float(installment_amount), 2))),
                    due_date=date(year.start_date.year + (1 if due_month <= 6 else 0), due_month, 15),
                    is_paid=is_paid,
                    paid_amount=paid_amount
                )
                session.add(installment)
        
        print("   ✓ تم إنشاء رسوم وأقساط الطلاب")
        
        # 10. سندات القبض
        print("\n10. إنشاء سندات القبض...")
        receipt_number = 1
        
        for student in students[:60]:
            num_receipts = random.randint(1, 3)
            
            for _ in range(num_receipts):
                amount = Decimal(str(random.randint(20000, 100000)))
                receipt = Receipt(
                    receipt_number=f"RCV-{year.id:02d}-{receipt_number:05d}",
                    student_id=student.id,
                    installment_id=None,
                    payment_target=random.choice(['previous_debt', 'current_fee']),
                    amount_paid=amount,
                    payment_date=datetime.now() - timedelta(days=random.randint(0, 120)),
                    payment_method=random.choice(["نقداً", "تحويل بنكي", "كريمي/حاسب"]),
                    reference_number=f"REF-{random.randint(10000, 99999)}" if random.random() > 0.5 else None,
                    notes=random.choice(["", "دفعة مقدمة", "سداد قسط", "تسوية"]),
                    created_by_user_id=1,
                    status=random.choice(["نشط", "نشط", "نشط", "ملغى"]),
                    cancellation_reason="خطأ في المبلغ" if random.random() < 0.1 else None
                )
                session.add(receipt)
                receipt_number += 1
        
        print("   ✓ تم إنشاء سندات القبض")
        
        # 11. سندات الصرف
        print("\n11. إنشاء سندات الصرف...")
        voucher_number = 1
        
        expense_categories = ["مشتريات مواد", "صيانة وتشغيل", "فعاليات واحتفالات", "أنشطة مدرسية", "أخرى"]
        beneficiaries = ["مكتبة النور", "شركة التقنية", "مؤسسة النظافة", "مطعم المدرسة", "شركة النقل"]
        
        for i in range(40):
            voucher = ExpenseVoucher(
                voucher_number=f"EXP-{year.id:02d}-{voucher_number:05d}",
                expense_category=random.choice(expense_categories),
                beneficiary_name=random.choice(beneficiaries),
                amount=Decimal(str(random.randint(10000, 150000))),
                payment_date=datetime.now() - timedelta(days=random.randint(0, 90)),
                payment_method=random.choice(["نقداً", "تحويل بنكي"]),
                invoice_number=f"INV-{random.randint(1000, 9999)}" if random.random() > 0.5 else None,
                notes=random.choice(["", "صيانة دورية", "شراء مستلزمات", "فعالية مدرسية"]),
                created_by_user_id=1,
                status=random.choice(["نشط", "نشط", "ملغى"]),
                cancellation_reason="إلغاء" if random.random() < 0.15 else None
            )
            session.add(voucher)
            voucher_number += 1
        
        print("   ✓ تم إنشاء سندات الصرف")
        
        # 12. الحضور والغياب
        print("\n12. إنشاء سجلات الحضور...")
        attendance_count = 0
        
        for student in students[:50]:
            # آخر 30 يوم
            for day_offset in range(30):
                if random.random() > 0.15:  # 85% حضور
                    status = random.choice(["حاضر", "حاضر", "حاضر", "حاضر", "متأخر", "غائب"])
                else:
                    status = "حاضر"
                
                attendance = DailyAttendance(
                    student_id=student.id,
                    academic_year_id=year.id,
                    grade_id=student.grade_id,
                    section_id=student.section_id,
                    attendance_date=date.today() - timedelta(days=day_offset),
                    status=status,
                    notes="متأخر عن الطابور" if status == "متأخر" and random.random() > 0.5 else None
                )
                session.add(attendance)
                attendance_count += 1
        
        print(f"   ✓ تم إنشاء {attendance_count} سجل حضور")
        
        # 13. التقييمات الشهرية
        print("\n13. إنشاء التقييمات الشهرية...")
        eval_count = 0
        
        for student in students[:40]:
            for subject in subjects[:5]:
                for month in range(1, 4):
                    written = Decimal(str(round(random.uniform(10, 40), 2)))
                    oral = Decimal(str(round(random.uniform(5, 20), 2)))
                    homework = Decimal(str(round(random.uniform(5, 20), 2)))
                    attendance_score = Decimal(str(round(random.uniform(5, 20), 2)))
                    
                    evaluation = MonthlyEvaluation(
                        student_id=student.id,
                        academic_year_id=year.id,
                        grade_id=student.grade_id,
                        section_id=student.section_id,
                        subject_id=subject.id,
                        term=1,
                        month=month,
                        written_score=written,
                        oral_score=oral,
                        homework_score=homework,
                        attendance_score=attendance_score
                    )
                    session.add(evaluation)
                    eval_count += 1
        
        print(f"   ✓ تم إنشاء {eval_count} تقييم شهري")
        
        # 14. درجات نهاية الفصل
        print("\n14. إنشاء درجات نهاية الفصل...")
        exam_count = 0
        
        for student in students[:40]:
            for subject in subjects[:5]:
                exam_score = Decimal(str(round(random.uniform(5, 30), 2)))
                
                exam = TermExamScore(
                    student_id=student.id,
                    academic_year_id=year.id,
                    grade_id=student.grade_id,
                    section_id=student.section_id,
                    subject_id=subject.id,
                    term=1,
                    exam_score=exam_score
                )
                session.add(exam)
                exam_count += 1
        
        print(f"   ✓ تم إنشاء {exam_count} درجة اختبار")
        
        # 15. الواجبات المنزلية
        print("\n15. إنشاء الواجبات...")
        
        homework_titles = [
            "حل تمارين الرياضيات", "قراءة درس اللغة العربية", "حفظ سورة",
            "كتابة مقال", "حل مسائل العلوم", "مراجعة القواعد",
        ]
        
        for grade in grades[:6]:
            grade_sections = [s for s in sections if s.grade_id == grade.id][:2]
            
            for section in grade_sections:
                for subject in subjects[:3]:
                    homework = Homework(
                        academic_year_id=year.id,
                        grade_id=grade.id,
                        section_id=section.id,
                        subject_id=subject.id,
                        homework_date=date.today() - timedelta(days=random.randint(0, 14)),
                        title=random.choice(homework_titles),
                        description="يرجى حل جميع التمارين وتسليمها في الموعد المحدد",
                        due_date=date.today() + timedelta(days=random.randint(1, 7))
                    )
                    session.add(homework)
        
        print("   ✓ تم إنشاء الواجبات")
        
        # 16. السجل السلوكي
        print("\n16. إنشاء السجل السلوكي...")
        
        behavior_types = ["تميز", "مخالفة", "تنبيه أخصائي"]
        behavior_titles = {
            "تميز": ["مشاركة فعالة", "مساعدة زملاء", "تفوق دراسي"],
            "مخالفة": ["تأخر متكرر", "عدم الالتزام بالزي", "إزعاج في الفصل"],
            "تنبيه أخصائي": ["متابعة سلوكية", "جلسة إرشادية"],
        }
        
        for student in students[:30]:
            num_records = random.randint(1, 3)
            
            for _ in range(num_records):
                behavior_type = random.choice(behavior_types)
                
                record = BehavioralRecord(
                    student_id=student.id,
                    academic_year_id=year.id,
                    behavior_type=behavior_type,
                    title=random.choice(behavior_titles[behavior_type]),
                    details="تم تسجيل الملاحظة من قبل المعلم",
                    action_taken="تم إبلاغ ولي الأمر" if random.random() > 0.5 else None,
                    record_date=date.today() - timedelta(days=random.randint(0, 60))
                )
                session.add(record)
        
        print("   ✓ تم إنشاء السجل السلوكي")
        
        # 17. البدلات والخصومات
        print("\n17. إنشاء البدلات والخصومات...")
        
        allowance_types = ["بدل", "حافز", "مكافأة", "خصم", "غياب"]
        
        for employee in employees[:15]:
            num_records = random.randint(1, 3)
            
            for _ in range(num_records):
                type_ = random.choice(allowance_types)
                amount = Decimal(str(random.randint(5000, 30000)))
                
                record = EmployeeAllowanceDeduction(
                    employee_id=employee.id,
                    type=type_,
                    amount=amount,
                    reason="بدل مواصلات" if type_ == "بدل" else "خصم غياب" if type_ == "غياب" else "",
                    date=date.today() - timedelta(days=random.randint(0, 45))
                )
                session.add(record)
        
        print("   ✓ تم إنشاء البدلات والخصومات")
        
        # 18. السلف المالية
        print("\n18. إنشاء السلف...")
        
        for employee in employees[:10]:
            if random.random() > 0.5:
                total = Decimal(str(random.randint(50000, 200000)))
                monthly = Decimal(str(round(float(total) / random.randint(3, 12), 2)))
                
                loan = EmployeeLoan(
                    employee_id=employee.id,
                    total_loan_amount=total,
                    monthly_deduction=monthly,
                    status=random.choice(["مستمرة", "مستمرة", "منتهية"]),
                    loan_date=date.today() - timedelta(days=random.randint(30, 180)),
                    reason="ظروف شخصية"
                )
                session.add(loan)
        
        print("   ✓ تم إنشاء السلف")
        
        # 19. الرواتب
        print("\n19. إنشاء الرواتب...")
        
        for employee in employees[:15]:
            month = date.today().month - 1 if date.today().month > 1 else 12
            year_value = date.today().year if month > 1 else date.today().year - 1
            
            allowances = Decimal(str(random.randint(0, 30000)))
            deductions = Decimal(str(random.randint(0, 10000)))
            loan_deduction = Decimal(str(random.randint(0, 20000)))
            
            net = employee.basic_salary + allowances - deductions - loan_deduction
            
            payroll = PayrollRecord(
                employee_id=employee.id,
                month=month,
                year=year_value,
                basic_salary=employee.basic_salary,
                total_allowances=allowances,
                total_deductions=deductions,
                loan_deduction=loan_deduction,
                net_salary=net,
                payment_status=random.choice(["مسلم", "مسلم", "معلق"]),
                payment_date=datetime.now() - timedelta(days=random.randint(1, 15)) if random.random() > 0.3 else None
            )
            session.add(payroll)
        
        print("   ✓ تم إنشاء الرواتب")
        
        # 20. توزيع المواد على المعلمين
        print("\n20. توزيع المواد...")
        
        teacher_employees = [e for e in employees if "معلم" in e.job_title][:15]
        
        for grade in grades[:6]:
            grade_sections = [s for s in sections if s.grade_id == grade.id]
            
            for section in grade_sections:
                for subject in subjects[:5]:
                    if teacher_employees:
                        teacher = random.choice(teacher_employees)
                        
                        existing = session.execute(
                            select(TeacherSubjectSection).where(
                                TeacherSubjectSection.academic_year_id == year.id,
                                TeacherSubjectSection.section_id == section.id,
                                TeacherSubjectSection.subject_id == subject.id
                            )
                        ).scalar_one_or_none()
                        
                        if not existing:
                            assignment = TeacherSubjectSection(
                                academic_year_id=year.id,
                                grade_id=grade.id,
                                section_id=section.id,
                                subject_id=subject.id,
                                teacher_id=teacher.id
                            )
                            session.add(assignment)
        
        print("   ✓ تم توزيع المواد")
        
        # 21. الإشعارات
        print("\n21. إنشاء الإشعارات...")
        
        notification_data = [
            ("بداية العام الدراسي", "نرحب بجميع الطلاب وأولياء الأمور في العام الدراسي الجديد", "عام"),
            ("اجتماع أولياء الأمور", "سيتم عقد اجتماع لأولياء الأمور يوم الخميس القادم", "عام"),
            ("تأجيل اختبار", "تم تأجيل اختبار الرياضيات إلى الأسبوع القادم", "نتائج"),
            ("تذكير بالرسوم", "نذكركم بموعد استحقاق القسط الثاني من الرسوم", "رسوم"),
            ("فعالية مدرسية", "ستقام فعالية اليوم المفتوح يوم السبت القادم", "عام"),
        ]
        
        for title, message, type_ in notification_data:
            notification = Notification(
                title=title,
                message=message,
                notification_type=type_,
                sender_user_id=1,
                target_type='all',
                sent_at=datetime.now() - timedelta(days=random.randint(1, 10)),
                is_active=True
            )
            session.add(notification)
            session.flush()
            
            # سجل الإشعارات لبعض أولياء الأمور
            for parent in parents[:20]:
                log = NotificationLog(
                    notification_id=notification.id,
                    parent_id=parent.id,
                    sent_at=datetime.now() - timedelta(days=random.randint(1, 10)),
                    delivery_status=random.choice(["sent", "delivered", "read"]),
                    read_at=datetime.now() - timedelta(days=random.randint(0, 5)) if random.random() > 0.5 else None
                )
                session.add(log)
        
        print("   ✓ تم إنشاء الإشعارات")
        
        session.commit()
    
    print("\n" + "=" * 70)
    print("✓ تمت تعبئة قاعدة البيانات بنجاح!")
    print("=" * 70)
    
    # ملخص
    print("\nملخص البيانات:")
    print(f"  - الموظفين: 30")
    print(f"  - أولياء الأمور: 100")
    print(f"  - الطلاب: {len(students)}")
    print(f"  - سجلات الحضور: {attendance_count}")
    print(f"  - التقييمات الشهرية: {eval_count}")
    print(f"  - درجات الاختبارات: {exam_count}")
    print(f"  - سندات القبض: ~60+")
    print(f"  - سندات الصرف: 40")
    print(f"  - الواجبات: ~36")
    print(f"  - السجل السلوكي: ~60")
    print(f"  - الرواتب: 15")
    print(f"  - الإشعارات: 5")


if __name__ == "__main__":
    seed_database()