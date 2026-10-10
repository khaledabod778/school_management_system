"""
نماذج المستخدمين والموظفين والأدوار والصلاحيات.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, Numeric,
    String, Text, UniqueConstraint, CheckConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .sync_mixin import SyncableMixin

class Role(Base, SyncableMixin, TimestampMixin):
    """أدوار النظام."""
    
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # العلاقات
    users: Mapped[List["User"]] = relationship(back_populates="role")
    permissions: Mapped[List["RolePermission"]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )
    
    def has_permission(self, module_name: str, permission_key: str) -> bool:
        """التحقق من صلاحية الدور."""
        for perm in self.permissions:
            if perm.permission.module_name == module_name:
                return getattr(perm, permission_key, False)
        return False


class Employee(Base, SyncableMixin, TimestampMixin):
    """إدارة الموظفين والمعلمين."""
    
    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint("gender IN ('ذكر', 'أنثى')", name="ck_employees_gender"),
        CheckConstraint(
            "status IN ('نشط', 'إجازة', 'مستقيل')",
            name="ck_employees_status"
        ),
        CheckConstraint(
            "payment_method IN ('حساب بنكي', 'محفظة إلكترونية', 'نقداً')",
            name="ck_employees_payment_method"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    job_title: Mapped[str] = mapped_column(String(100), nullable=False)
    qualification: Mapped[Optional[str]] = mapped_column(String(100))
    primary_phone: Mapped[Optional[str]] = mapped_column(String(20))
    secondary_phone: Mapped[Optional[str]] = mapped_column(String(20))
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    marital_status: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default='نشط', nullable=False)
    
    # بيانات الهوية والميلاد
    national_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True)
    id_issue_place: Mapped[Optional[str]] = mapped_column(String(50))
    id_issue_date: Mapped[Optional[datetime]] = mapped_column(Date)
    birth_date: Mapped[Optional[datetime]] = mapped_column(Date)
    birth_village: Mapped[Optional[str]] = mapped_column(String(50))
    birth_district: Mapped[Optional[str]] = mapped_column(String(50))
    birth_governorate: Mapped[Optional[str]] = mapped_column(String(50))
    
    # بيانات العقد والمالية
    contract_start_date: Mapped[Optional[datetime]] = mapped_column(Date)
    contract_end_date: Mapped[Optional[datetime]] = mapped_column(Date)
    basic_salary: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    payment_method: Mapped[str] = mapped_column(
        String(30), default='نقداً', nullable=False
    )
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(50))
    
    # العلاقات
    user_account: Mapped[Optional["User"]] = relationship(
        back_populates="employee", uselist=False
    )
    teacher_assignments: Mapped[List["TeacherSubjectSection"]] = relationship(
        back_populates="teacher"
    )
    allowances_deductions: Mapped[List["EmployeeAllowanceDeduction"]] = relationship(
        back_populates="employee"
    )
    loans: Mapped[List["EmployeeLoan"]] = relationship(back_populates="employee")
    payroll_records: Mapped[List["PayrollRecord"]] = relationship(back_populates="employee")


class User(Base, SyncableMixin, TimestampMixin):
    """مستخدمو النظام."""
    
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("status IN ('نشط', 'موقف')", name="ck_users_status"),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("employees.id", ondelete="SET NULL")
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id"), nullable=False
    )
    profile_image: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default='نشط', nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_password_change: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # العلاقات
    employee: Mapped[Optional["Employee"]] = relationship(back_populates="user_account")
    role: Mapped["Role"] = relationship(back_populates="users")
    
    # السجلات المرتبطة
    created_receipts: Mapped[List["Receipt"]] = relationship(
        back_populates="created_by_user"
    )
    created_vouchers: Mapped[List["ExpenseVoucher"]] = relationship(
        back_populates="created_by_user"
    )
    
    @property
    def display_name(self) -> str:
        """الاسم الكامل للمستخدم."""
        if self.employee:
            return self.employee.full_name
        return self.username
    
    @property
    def is_active(self) -> bool:
        """التحقق من حالة المستخدم."""
        return self.status == 'نشط'


class TeacherSubjectSection(Base, SyncableMixin, TimestampMixin):
    """ربط معلم بمادة وشعبة."""
    
    __tablename__ = "teacher_subject_sections"
    __table_args__ = (
        UniqueConstraint(
            "academic_year_id", "section_id", "subject_id",
            name="uq_teacher_assignment"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False
    )
    grade_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("grades.id", ondelete="CASCADE"), nullable=False
    )
    section_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False
    )
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    teacher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    
    # العلاقات
    academic_year: Mapped["AcademicYear"] = relationship(back_populates="teacher_assignments")
    grade: Mapped["Grade"] = relationship()
    section: Mapped["Section"] = relationship(back_populates="teacher_assignments")
    subject: Mapped["Subject"] = relationship(back_populates="teacher_assignments")
    teacher: Mapped["Employee"] = relationship(back_populates="teacher_assignments")


class Permission(Base):
    """مصفوفة الصلاحيات."""
    
    __tablename__ = "permissions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module_name: Mapped[str] = mapped_column(String(50), nullable=False)
    permission_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    # العلاقات
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        back_populates="permission", cascade="all, delete-orphan"
    )


class RolePermission(Base):
    """ربط الأدوار بالصلاحيات."""
    
    __tablename__ = "role_permissions"
    
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )
    can_view: Mapped[bool] = mapped_column(Boolean, default=False)
    can_add: Mapped[bool] = mapped_column(Boolean, default=False)
    can_edit: Mapped[bool] = mapped_column(Boolean, default=False)
    can_delete: Mapped[bool] = mapped_column(Boolean, default=False)
    can_print: Mapped[bool] = mapped_column(Boolean, default=False)
    can_cancel: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # العلاقات
    role: Mapped["Role"] = relationship(back_populates="permissions")
    permission: Mapped["Permission"] = relationship(back_populates="role_permissions")