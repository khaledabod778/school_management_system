"""
تطبيق FastAPI الرئيسي - واجهة API للتكامل المستقبلي مع تطبيق ولي الأمر.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr
import uvicorn

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.config import config_manager
from app.database.models.finance import StudentFee
from app.database.session import session_scope, get_session
from app.database.models import (
    Parent, ParentDevice, Student, Notification, NotificationLog,
    DailyAttendance, Homework, BehavioralRecord, Grade, Section,
    TermExamScore, MonthlyEvaluation, Subject, Receipt, FeeInstallment
)
from app.services.auth_service import AuthService
from app.core.exceptions import AuthenticationError, NotFoundError

logger = logging.getLogger(__name__)

# ============ نماذج Pydantic ============

class LoginRequest(BaseModel):
    """طلب تسجيل الدخول."""
    phone: str = Field(..., description="رقم الهاتف")
    password: str = Field(..., description="كلمة المرور")
    device_token: Optional[str] = None
    device_type: Optional[str] = None
    app_version: Optional[str] = None


class LoginResponse(BaseModel):
    """استجابة تسجيل الدخول."""
    success: bool
    token: Optional[str] = None
    parent_id: Optional[int] = None
    full_name: Optional[str] = None
    message: str = ""


class StudentInfo(BaseModel):
    """معلومات الطالب."""
    id: int
    student_number: str
    full_name: str
    grade_name: Optional[str] = None
    section_name: Optional[str] = None
    gender: Optional[str] = None
    status: Optional[str] = None


class AttendanceInfo(BaseModel):
    """معلومات الحضور."""
    date: str
    status: str
    notes: Optional[str] = None


class HomeworkInfo(BaseModel):
    """معلومات الواجب."""
    id: int
    title: str
    description: Optional[str] = None
    subject_name: Optional[str] = None
    homework_date: str
    due_date: str


class BehaviorInfo(BaseModel):
    """معلومات السلوك."""
    id: int
    behavior_type: str
    title: str
    details: Optional[str] = None
    action_taken: Optional[str] = None
    record_date: str


class GradeInfo(BaseModel):
    """معلومات الدرجات."""
    subject_name: str
    monthly_score: float
    exam_score: float
    total_score: float
    grade: str


class NotificationInfo(BaseModel):
    """معلومات الإشعار."""
    id: int
    title: str
    message: str
    notification_type: str
    created_at: str
    is_read: bool = False


class FeeInfo(BaseModel):
    """معلومات الرسوم."""
    installment_name: str
    amount: float
    due_date: str
    paid_amount: float
    is_paid: bool


# ============ إعداد التطبيق ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """دورة حياة التطبيق."""
    logger.info("بدء تشغيل API...")
    yield
    logger.info("إيقاف تشغيل API...")


app = FastAPI(
    title="School Management API",
    description="واجهة API لنظام إدارة المدرسة - للتكامل مع تطبيق ولي الأمر",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# ============ إعداد CORS ============

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يمكن تقييدها لاحقاً
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ الأمان ============

security = HTTPBearer(auto_error=False)

# تخزين الرموز (في الإنتاج يجب استخدام Redis أو قاعدة بيانات)
active_tokens = {}


def generate_token(parent_id: int) -> str:
    """توليد رمز مصادقة."""
    import secrets
    token = secrets.token_urlsafe(32)
    active_tokens[token] = {
        'parent_id': parent_id,
        'created_at': datetime.now(),
        'expires_at': datetime.now() + timedelta(days=30)
    }
    return token


def verify_token(token: str) -> Optional[int]:
    """التحقق من الرمز."""
    token_data = active_tokens.get(token)
    if not token_data:
        return None
    
    if token_data['expires_at'] < datetime.now():
        del active_tokens[token]
        return None
    
    return token_data['parent_id']


def get_current_parent(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """الحصول على ولي الأمر الحالي."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="رمز المصادقة مطلوب"
        )
    
    parent_id = verify_token(credentials.credentials)
    if not parent_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="رمز المصادقة غير صالح أو منتهي"
        )
    
    return parent_id


# ============ نقاط النهاية ============

@app.get("/")
async def root():
    """الصفحة الرئيسية."""
    return {
        "name": "School Management API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "login": "/api/auth/login",
            "students": "/api/students",
            "attendance": "/api/attendance",
            "homeworks": "/api/homeworks",
            "notifications": "/api/notifications",
            "fees": "/api/fees",
        }
    }


@app.get("/health")
async def health_check():
    """فحص صحة الخدمة."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============ المصادقة ============

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """تسجيل دخول ولي الأمر."""
    try:
        with session_scope() as session:
            # البحث عن ولي الأمر
            parent = session.execute(
                select(Parent).where(Parent.primary_phone == request.phone)
            ).scalar_one_or_none()
            
            if not parent:
                return LoginResponse(
                    success=False,
                    message="رقم الهاتف غير مسجل"
                )
            
            # التحقق من كلمة المرور
            if not AuthService.verify_password(request.password, parent.password_hash):
                return LoginResponse(
                    success=False,
                    message="كلمة المرور غير صحيحة"
                )
            
            # تسجيل الجهاز
            if request.device_token:
                device = session.execute(
                    select(ParentDevice).where(
                        ParentDevice.parent_id == parent.id,
                        ParentDevice.device_token == request.device_token
                    )
                ).scalar_one_or_none()
                
                if not device:
                    device = ParentDevice(
                        parent_id=parent.id,
                        device_token=request.device_token,
                        device_type=request.device_type,
                        app_version=request.app_version,
                        last_login=datetime.now(),
                        is_active=True
                    )
                    session.add(device)
                else:
                    device.last_login = datetime.now()
                    device.is_active = True
            
            # توليد الرمز
            token = generate_token(parent.id)
            
            return LoginResponse(
                success=True,
                token=token,
                parent_id=parent.id,
                full_name=parent.full_name,
                message="تم تسجيل الدخول بنجاح"
            )
    
    except Exception as e:
        logger.error(f"خطأ في تسجيل الدخول: {str(e)}")
        return LoginResponse(
            success=False,
            message="حدث خطأ غير متوقع"
        )


@app.post("/api/auth/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """تسجيل الخروج."""
    if credentials and credentials.credentials in active_tokens:
        del active_tokens[credentials.credentials]
    
    return {"success": True, "message": "تم تسجيل الخروج"}


# ============ الطلاب ============

@app.get("/api/students", response_model=List[StudentInfo])
async def get_students(
    parent_id: int = Depends(get_current_parent)
):
    """الحصول على طلاب ولي الأمر."""
    with session_scope() as session:
        students = session.execute(
            select(Student).where(Student.parent_id == parent_id)
        ).scalars().all()
        
        result = []
        for student in students:
            result.append(StudentInfo(
                id=student.id,
                student_number=student.student_number,
                full_name=student.full_name,
                grade_name=student.grade.grade_name if student.grade else None,
                section_name=student.section.section_name if student.section else None,
                gender=student.gender,
                status=student.status
            ))
        
        return result


@app.get("/api/students/{student_id}", response_model=StudentInfo)
async def get_student(
    student_id: int,
    parent_id: int = Depends(get_current_parent)
):
    """الحصول على معلومات طالب محدد."""
    with session_scope() as session:
        student = session.get(Student, student_id)
        
        if not student:
            raise HTTPException(status_code=404, detail="الطالب غير موجود")
        
        if student.parent_id != parent_id:
            raise HTTPException(status_code=403, detail="غير مصرح بالوصول")
        
        return StudentInfo(
            id=student.id,
            student_number=student.student_number,
            full_name=student.full_name,
            grade_name=student.grade.grade_name if student.grade else None,
            section_name=student.section.section_name if student.section else None,
            gender=student.gender,
            status=student.status
        )


# ============ الحضور ============

@app.get("/api/attendance/{student_id}", response_model=List[AttendanceInfo])
async def get_attendance(
    student_id: int,
    days: int = 30,
    parent_id: int = Depends(get_current_parent)
):
    """الحصول على سجل الحضور."""
    with session_scope() as session:
        student = session.get(Student, student_id)
        if not student or student.parent_id != parent_id:
            raise HTTPException(status_code=403, detail="غير مصرح بالوصول")
        
        from_date = datetime.now().date() - timedelta(days=days)
        
        attendance_records = session.execute(
            select(DailyAttendance).where(
                DailyAttendance.student_id == student_id,
                DailyAttendance.attendance_date >= from_date
            ).order_by(DailyAttendance.attendance_date.desc())
        ).scalars().all()
        
        return [
            AttendanceInfo(
                date=att.attendance_date.isoformat(),
                status=att.status,
                notes=att.notes
            )
            for att in attendance_records
        ]


# ============ الواجبات ============

@app.get("/api/homeworks/{student_id}", response_model=List[HomeworkInfo])
async def get_homeworks(
    student_id: int,
    parent_id: int = Depends(get_current_parent)
):
    """الحصول على واجبات الطالب."""
    with session_scope() as session:
        student = session.get(Student, student_id)
        if not student or student.parent_id != parent_id:
            raise HTTPException(status_code=403, detail="غير مصرح بالوصول")
        
        homeworks = session.execute(
            select(Homework, Subject)
            .join(Subject, Homework.subject_id == Subject.id)
            .where(
                Homework.grade_id == student.grade_id,
                Homework.section_id == student.section_id
            )
            .order_by(Homework.homework_date.desc())
            .limit(50)
        ).all()
        
        return [
            HomeworkInfo(
                id=hw.id,
                title=hw.title,
                description=hw.description,
                subject_name=subject.subject_name,
                homework_date=hw.homework_date.isoformat(),
                due_date=hw.due_date.isoformat()
            )
            for hw, subject in homeworks
        ]


# ============ السلوك ============

@app.get("/api/behavior/{student_id}", response_model=List[BehaviorInfo])
async def get_behavior(
    student_id: int,
    parent_id: int = Depends(get_current_parent)
):
    """الحصول على السجل السلوكي."""
    with session_scope() as session:
        student = session.get(Student, student_id)
        if not student or student.parent_id != parent_id:
            raise HTTPException(status_code=403, detail="غير مصرح بالوصول")
        
        records = session.execute(
            select(BehavioralRecord).where(
                BehavioralRecord.student_id == student_id
            ).order_by(BehavioralRecord.record_date.desc()).limit(50)
        ).scalars().all()
        
        return [
            BehaviorInfo(
                id=rec.id,
                behavior_type=rec.behavior_type,
                title=rec.title,
                details=rec.details,
                action_taken=rec.action_taken,
                record_date=rec.record_date.isoformat()
            )
            for rec in records
        ]


# ============ الدرجات ============

@app.get("/api/grades/{student_id}", response_model=List[GradeInfo])
async def get_grades(
    student_id: int,
    term: int = 1,
    parent_id: int = Depends(get_current_parent)
):
    """الحصول على درجات الطالب."""
    with session_scope() as session:
        student = session.get(Student, student_id)
        if not student or student.parent_id != parent_id:
            raise HTTPException(status_code=403, detail="غير مصرح بالوصول")
        
        # الحصول على التقييمات الشهرية
        monthly = session.execute(
            select(MonthlyEvaluation, Subject)
            .join(Subject, MonthlyEvaluation.subject_id == Subject.id)
            .where(
                MonthlyEvaluation.student_id == student_id,
                MonthlyEvaluation.term == term
            )
        ).all()
        
        # الحصول على درجات الاختبارات
        exams = session.execute(
            select(TermExamScore, Subject)
            .join(Subject, TermExamScore.subject_id == Subject.id)
            .where(
                TermExamScore.student_id == student_id,
                TermExamScore.term == term
            )
        ).all()
        
        # دمج البيانات
        grades_dict = {}
        
        for eval, subject in monthly:
            if subject.id not in grades_dict:
                grades_dict[subject.id] = {'subject': subject, 'monthly': 0, 'exam': 0}
            grades_dict[subject.id]['monthly'] += float(eval.total_month_score)
        
        for exam, subject in exams:
            if subject.id not in grades_dict:
                grades_dict[subject.id] = {'subject': subject, 'monthly': 0, 'exam': 0}
            grades_dict[subject.id]['exam'] = float(exam.exam_score)
        
        result = []
        for data in grades_dict.values():
            total = data['monthly'] + data['exam']
            
            if total >= 90:
                grade_text = "ممتاز"
            elif total >= 80:
                grade_text = "جيد جداً"
            elif total >= 70:
                grade_text = "جيد"
            elif total >= 50:
                grade_text = "مقبول"
            else:
                grade_text = "راسب"
            
            result.append(GradeInfo(
                subject_name=data['subject'].subject_name,
                monthly_score=data['monthly'],
                exam_score=data['exam'],
                total_score=total,
                grade=grade_text
            ))
        
        return result


# ============ الرسوم ============

@app.get("/api/fees/{student_id}", response_model=List[FeeInfo])
async def get_fees(
    student_id: int,
    parent_id: int = Depends(get_current_parent)
):
    """الحصول على رسوم الطالب."""
    with session_scope() as session:
        student = session.get(Student, student_id)
        if not student or student.parent_id != parent_id:
            raise HTTPException(status_code=403, detail="غير مصرح بالوصول")
        
        installments = session.execute(
            select(FeeInstallment, StudentFee)
            .join(StudentFee, FeeInstallment.student_fee_id == StudentFee.id)
            .where(StudentFee.student_id == student_id)
            .order_by(FeeInstallment.installment_number)
        ).all()
        
        return [
            FeeInfo(
                installment_name=inst.installment_name,
                amount=float(inst.amount),
                due_date=inst.due_date.isoformat(),
                paid_amount=float(inst.paid_amount),
                is_paid=inst.is_paid
            )
            for inst, fee in installments
        ]


# ============ الإشعارات ============

@app.get("/api/notifications", response_model=List[NotificationInfo])
async def get_notifications(
    parent_id: int = Depends(get_current_parent)
):
    """الحصول على إشعارات ولي الأمر."""
    with session_scope() as session:
        logs = session.execute(
            select(NotificationLog, Notification)
            .join(Notification, NotificationLog.notification_id == Notification.id)
            .where(NotificationLog.parent_id == parent_id)
            .order_by(Notification.created_at.desc())
            .limit(100)
        ).all()
        
        return [
            NotificationInfo(
                id=notification.id,
                title=notification.title,
                message=notification.message,
                notification_type=notification.notification_type,
                created_at=notification.created_at.isoformat(),
                is_read=log.delivery_status == 'read'
            )
            for log, notification in logs
        ]


@app.post("/api/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    parent_id: int = Depends(get_current_parent)
):
    """تحديد إشعار كمقروء."""
    with session_scope() as session:
        log = session.execute(
            select(NotificationLog).where(
                NotificationLog.notification_id == notification_id,
                NotificationLog.parent_id == parent_id
            )
        ).scalar_one_or_none()
        
        if not log:
            raise HTTPException(status_code=404, detail="الإشعار غير موجود")
        
        log.delivery_status = 'read'
        log.read_at = datetime.now()
        session.commit()
        
        return {"success": True}


# ============ تشغيل الخادم ============

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """تشغيل خادم API."""
    uvicorn.run(
        "app.api.fastapi_app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    run_server()