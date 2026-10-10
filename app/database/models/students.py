"""
نماذج الطلاب وأولياء الأمور والوثائق.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, Numeric,
    String, Text, UniqueConstraint, CheckConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .sync_mixin import SyncableMixin

class Parent(Base, SyncableMixin, TimestampMixin):
    """إدارة أولياء الأمور."""
    
    __tablename__ = "parents"
    __table_args__ = (
        CheckConstraint(
            "category IN ('عادي', 'VIP', 'كفالة')",
            name="ck_parents_category"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    primary_phone: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False
    )
    secondary_phone: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)
    job: Mapped[Optional[str]] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(20), default='عادي', nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # العلاقات
    students: Mapped[List["Student"]] = relationship(back_populates="parent")
    devices: Mapped[List["ParentDevice"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan"
    )
    notification_logs: Mapped[List["NotificationLog"]] = relationship(
        back_populates="parent"
    )
    
    @property
    def display_name(self) -> str:
        """اسم ولي الأمر مع رقم الهاتف."""
        return f"{self.full_name} ({self.primary_phone})"


class ParentDevice(Base, SyncableMixin, TimestampMixin):
    """أجهزة تطبيق أولياء الأمور."""
    
    __tablename__ = "parent_devices"
    __table_args__ = (
        CheckConstraint(
            "device_type IN ('android', 'ios', 'web')",
            name="ck_parent_devices_type"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False
    )
    device_token: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[Optional[str]] = mapped_column(String(20))
    app_version: Mapped[Optional[str]] = mapped_column(String(30))
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # العلاقات
    parent: Mapped["Parent"] = relationship(back_populates="devices")


class Student(Base, SyncableMixin, TimestampMixin):
    """إدارة الطلاب."""
    
    __tablename__ = "students"
    __table_args__ = (
        CheckConstraint("gender IN ('ذكر', 'أنثى')", name="ck_students_gender"),
        CheckConstraint(
            "status IN ('مستمر', 'انسحاب', 'موقف', 'خريج')",
            name="ck_students_status"
        ),
        CheckConstraint(
            "enrollment_type IN ('مستجد', 'محول', 'باقي')",
            name="ck_students_enrollment_type"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_number: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    mother_name: Mapped[Optional[str]] = mapped_column(String(150))
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    nationality: Mapped[str] = mapped_column(String(50), default='يمني', nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='مستمر', nullable=False)
    enrollment_type: Mapped[str] = mapped_column(
        String(20), default='مستجد', nullable=False
    )
    student_status_reason: Mapped[Optional[str]] = mapped_column(String(100))
    
    # بيانات الميلاد
    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    birth_village: Mapped[Optional[str]] = mapped_column(String(50))
    birth_district: Mapped[Optional[str]] = mapped_column(String(50))
    birth_governorate: Mapped[Optional[str]] = mapped_column(String(50))
    
    # بيانات المدرسة المحول منها
    transferred_from_school: Mapped[Optional[str]] = mapped_column(String(100))
    transferred_district: Mapped[Optional[str]] = mapped_column(String(50))
    transferred_governorate: Mapped[Optional[str]] = mapped_column(String(50))
    transfer_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # الربط الأكاديمي الحالي
    academic_year_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("academic_years.id")
    )
    grade_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("grades.id")
    )
    section_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sections.id")
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("parents.id", ondelete="SET NULL")
    )
    photo_url: Mapped[Optional[str]] = mapped_column(String(255))
    
    # العلاقات
    academic_year: Mapped[Optional["AcademicYear"]] = relationship(back_populates="students")
    grade: Mapped[Optional["Grade"]] = relationship(back_populates="students")
    section: Mapped[Optional["Section"]] = relationship(back_populates="students")
    parent: Mapped[Optional["Parent"]] = relationship(back_populates="students")
    documents: Mapped[List["StudentDocument"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    academic_history: Mapped[List["StudentAcademicHistory"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    fees: Mapped[List["StudentFee"]] = relationship(back_populates="student")
    receipts: Mapped[List["Receipt"]] = relationship(back_populates="student")
    attendance: Mapped[List["DailyAttendance"]] = relationship(back_populates="student")
    evaluations: Mapped[List["MonthlyEvaluation"]] = relationship(back_populates="student")
    exam_scores: Mapped[List["TermExamScore"]] = relationship(back_populates="student")
    behavioral_records: Mapped[List["BehavioralRecord"]] = relationship(back_populates="student")
    
    @property
    def display_name(self) -> str:
        """اسم الطالب مع الرقم."""
        return f"{self.full_name} ({self.student_number})"
    
    @property
    def current_section_name(self) -> str:
        """اسم الشعبة الحالية."""
        if self.section:
            return f"{self.grade.grade_name} - {self.section.section_name}"
        elif self.grade:
            return self.grade.grade_name
        return "غير محدد"


class StudentAcademicHistory(Base, SyncableMixin, TimestampMixin):
    """السجل الأكاديمي التاريخي للطلاب."""
    
    __tablename__ = "student_academic_history"
    __table_args__ = (
        UniqueConstraint(
            "student_id", "academic_year_id",
            name="uq_student_year_history"
        ),
        CheckConstraint(
            "final_result IN ('passed', 'failed', 'second_round')",
            name="ck_student_history_result"
        ),
        CheckConstraint(
            "promotion_status IN ('promoted', 'retained', 'withdrawn')",
            name="ck_student_history_promotion"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id"), nullable=False
    )
    grade_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("grades.id"), nullable=False
    )
    section_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sections.id"), nullable=False
    )
    final_result: Mapped[Optional[str]] = mapped_column(String(20))
    promotion_status: Mapped[Optional[str]] = mapped_column(String(20))
    
    # العلاقات
    student: Mapped["Student"] = relationship(back_populates="academic_history")


class StudentDocument(Base, SyncableMixin, TimestampMixin):
    """أرشيف وثائق الطلاب."""
    
    __tablename__ = "student_documents"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    
    # العلاقات
    student: Mapped["Student"] = relationship(back_populates="documents")