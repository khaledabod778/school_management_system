"""
نماذج التهيئة والتنظيم الأكاديمي.
يتضمن: المدرسة، السنوات الدراسية، الصفوف، الشعب، المواد.
"""

from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, Numeric, 
    String, Text, UniqueConstraint, CheckConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .sync_mixin import SyncableMixin

from .base import Base, TimestampMixin


class SchoolInfo(Base, SyncableMixin, TimestampMixin):
    """بيانات المدرسة والهوية المطبوعة."""
    
    __tablename__ = "school_info"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    school_name_ar: Mapped[str] = mapped_column(String(150), nullable=False)
    school_name_en: Mapped[Optional[str]] = mapped_column(String(150))
    principal_name: Mapped[Optional[str]] = mapped_column(String(100))
    license_number: Mapped[Optional[str]] = mapped_column(String(50))
    phone_primary: Mapped[Optional[str]] = mapped_column(String(20))
    phone_secondary: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    address_detail: Mapped[Optional[str]] = mapped_column(Text)
    logo_url: Mapped[Optional[str]] = mapped_column(String(255))
    header_footer_url: Mapped[Optional[str]] = mapped_column(String(255))
    terms_and_conditions: Mapped[Optional[str]] = mapped_column(Text)


class AcademicYear(Base, SyncableMixin, TimestampMixin):
    """إدارة السنوات الدراسية."""
    
    __tablename__ = "academic_years"
    __table_args__ = (
        CheckConstraint(
            "status IN ('current', 'closed', 'upcoming')",
            name="ck_academic_years_status"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year_name_gregorian: Mapped[str] = mapped_column(String(20), nullable=False)
    year_name_hijri: Mapped[str] = mapped_column(String(20), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='upcoming', nullable=False)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    closed_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    
    # العلاقات
    students: Mapped[List["Student"]] = relationship(back_populates="academic_year")
    grade_fees: Mapped[List["GradeFeeStructure"]] = relationship(back_populates="academic_year")
    teacher_assignments: Mapped[List["TeacherSubjectSection"]] = relationship(back_populates="academic_year")
    
    @property
    def display_name(self) -> str:
        """الاسم الكامل للسنة الدراسية."""
        return f"{self.year_name_gregorian} / {self.year_name_hijri}"


class Grade(Base, SyncableMixin, TimestampMixin):
    """إدارة الصفوف الدراسية."""
    
    __tablename__ = "grades"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    grade_name: Mapped[str] = mapped_column(String(50), nullable=False)
    stage_name: Mapped[str] = mapped_column(String(50), nullable=False)
    max_capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # العلاقات
    sections: Mapped[List["Section"]] = relationship(
        back_populates="grade", cascade="all, delete-orphan"
    )
    students: Mapped[List["Student"]] = relationship(back_populates="grade")
    grade_fees: Mapped[List["GradeFeeStructure"]] = relationship(back_populates="grade")
    
    @property
    def display_name(self) -> str:
        """اسم الصف مع المرحلة."""
        return f"{self.grade_name} - {self.stage_name}"


class Section(Base, SyncableMixin, TimestampMixin):
    """إدارة الشعب الدراسية."""
    
    __tablename__ = "sections"
    __table_args__ = (
        UniqueConstraint("grade_id", "section_name", name="uq_grade_section"),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    grade_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("grades.id", ondelete="CASCADE"), nullable=False
    )
    section_name: Mapped[str] = mapped_column(String(10), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    
    # العلاقات
    grade: Mapped["Grade"] = relationship(back_populates="sections")
    students: Mapped[List["Student"]] = relationship(back_populates="section")
    teacher_assignments: Mapped[List["TeacherSubjectSection"]] = relationship(back_populates="section")
    
    @property
    def display_name(self) -> str:
        """اسم الشعبة مع الصف."""
        return f"{self.grade.grade_name} - {self.section_name}" if self.grade else self.section_name


class Subject(Base, SyncableMixin, TimestampMixin):
    """دليل المواد الدراسية."""
    
    __tablename__ = "subjects"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_name: Mapped[str] = mapped_column(String(100), nullable=False)
    min_pass_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("50.00"), nullable=False
    )
    max_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("100.00"), nullable=False
    )
    
    # العلاقات
    teacher_assignments: Mapped[List["TeacherSubjectSection"]] = relationship(back_populates="subject")
    
    @property
    def display_name(self) -> str:
        """اسم المادة مع الدرجات."""
        return f"{self.subject_name} (النجاح: {self.min_pass_score}, الكبرى: {self.max_score})"