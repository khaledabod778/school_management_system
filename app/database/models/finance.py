"""
النماذج المالية: الرسوم، السندات، الرواتب، المصروفات.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, Numeric,
    String, Text, UniqueConstraint, CheckConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .sync_mixin import SyncableMixin

from .base import Base, TimestampMixin


class FeeType(Base, SyncableMixin, TimestampMixin):
    """أنواع الرسوم المدرسية."""
    
    __tablename__ = "fee_types"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fee_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    # العلاقات
    grade_fees: Mapped[List["GradeFeeStructure"]] = relationship(back_populates="fee_type")


class GradeFeeStructure(Base, SyncableMixin, TimestampMixin):
    """لائحة الرسوم المدرسية المحددة للصفوف."""
    
    __tablename__ = "grade_fee_structures"
    __table_args__ = (
        UniqueConstraint(
            "academic_year_id", "grade_id", "fee_type_id",
            name="uq_grade_fee"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False
    )
    grade_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("grades.id", ondelete="CASCADE"), nullable=False
    )
    fee_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fee_types.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    
    # العلاقات
    academic_year: Mapped["AcademicYear"] = relationship(back_populates="grade_fees")
    grade: Mapped["Grade"] = relationship(back_populates="grade_fees")
    fee_type: Mapped["FeeType"] = relationship(back_populates="grade_fees")


class StudentFee(Base, SyncableMixin, TimestampMixin):
    """رسوم الطلاب المعتمدة والأرصدة."""
    
    __tablename__ = "student_fees"
    __table_args__ = (
        UniqueConstraint(
            "student_id", "academic_year_id",
            name="uq_student_year_fee"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False
    )
    previous_debt: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    current_year_fees: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    net_total_required: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    
    # العلاقات
    student: Mapped["Student"] = relationship(back_populates="fees")
    installments: Mapped[List["FeeInstallment"]] = relationship(
        back_populates="student_fee", cascade="all, delete-orphan"
    )
    
    @property
    def total_paid(self) -> Decimal:
        """إجمالي المدفوع."""
        return sum(
            (inst.paid_amount for inst in self.installments),
            Decimal("0.00")
        )
    
    @property
    def remaining_balance(self) -> Decimal:
        """المبلغ المتبقي."""
        return self.net_total_required - self.total_paid


class FeeInstallment(Base, SyncableMixin, TimestampMixin):
    """أقساط الرسوم المدرسية."""
    
    __tablename__ = "fee_installments"
    __table_args__ = (
        CheckConstraint(
            "installment_type IN ('previous_debt', 'regular')",
            name="ck_fee_installments_type"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_fee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("student_fees.id", ondelete="CASCADE"), nullable=False
    )
    installment_type: Mapped[str] = mapped_column(
        String(20), default='regular', nullable=False
    )
    installment_number: Mapped[int] = mapped_column(Integer, nullable=False)
    installment_name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    
    # العلاقات
    student_fee: Mapped["StudentFee"] = relationship(back_populates="installments")
    receipts: Mapped[List["Receipt"]] = relationship(back_populates="installment")
    
    @property
    def remaining_amount(self) -> Decimal:
        """المبلغ المتبقي للقسط."""
        return self.amount - self.paid_amount
    
    @property
    def is_overdue(self) -> bool:
        """التحقق من تأخر السداد."""
        return not self.is_paid and self.due_date < date.today()


class Receipt(Base, SyncableMixin, TimestampMixin):
    """سندات القبض والدفعات المالية."""
    
    __tablename__ = "receipts"
    __table_args__ = (
        CheckConstraint(
            "payment_target IN ('previous_debt', 'current_fee')",
            name="ck_receipts_payment_target"
        ),
        CheckConstraint(
            "payment_method IN ('نقداً', 'تحويل بنكي', 'كريمي/حاسب', 'شيك')",
            name="ck_receipts_payment_method"
        ),
        CheckConstraint(
            "status IN ('نشط', 'ملغى')",
            name="ck_receipts_status"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    receipt_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    installment_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("fee_installments.id", ondelete="SET NULL")
    )
    payment_target: Mapped[str] = mapped_column(
        String(30), default='current_fee', nullable=False
    )
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    payment_method: Mapped[str] = mapped_column(
        String(30), default='نقداً', nullable=False
    )
    reference_number: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default='نشط', nullable=False)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # العلاقات
    student: Mapped["Student"] = relationship(back_populates="receipts")
    installment: Mapped[Optional["FeeInstallment"]] = relationship(back_populates="receipts")
    created_by_user: Mapped["User"] = relationship(back_populates="created_receipts")


class ExpenseVoucher(Base, SyncableMixin, TimestampMixin):
    """سندات الصرف والمصروفات العامة."""
    
    __tablename__ = "expense_vouchers"
    __table_args__ = (
        CheckConstraint(
            "expense_category IN ('مشتريات مواد', 'صيانة وتشغيل', 'فعاليات واحتفالات', 'أنشطة مدرسية', 'أخرى')",
            name="ck_expense_vouchers_category"
        ),
        CheckConstraint(
            "payment_method IN ('نقداً', 'تحويل بنكي', 'كريمي/حاسب', 'شيك')",
            name="ck_expense_vouchers_payment_method"
        ),
        CheckConstraint(
            "status IN ('نشط', 'ملغى')",
            name="ck_expense_vouchers_status"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    voucher_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    expense_category: Mapped[str] = mapped_column(String(50), nullable=False)
    beneficiary_name: Mapped[str] = mapped_column(String(150), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    payment_method: Mapped[str] = mapped_column(
        String(30), default='نقداً', nullable=False
    )
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default='نشط', nullable=False)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # العلاقات
    created_by_user: Mapped["User"] = relationship(back_populates="created_vouchers")


class EmployeeAllowanceDeduction(Base, SyncableMixin, TimestampMixin):
    """البدلات والخصومات للموظفين."""
    
    __tablename__ = "employee_allowances_deductions"
    __table_args__ = (
        CheckConstraint(
            "type IN ('بدل', 'حافز', 'مكافأة', 'خصم', 'غياب')",
            name="ck_employee_allowances_type"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # العلاقات
    employee: Mapped["Employee"] = relationship(back_populates="allowances_deductions")
    
    @property
    def is_allowance(self) -> bool:
        """التحقق من كونها بدل."""
        return self.type in ('بدل', 'حافز', 'مكافأة')
    
    @property
    def is_deduction(self) -> bool:
        """التحقق من كونها خصم."""
        return self.type in ('خصم', 'غياب')


class EmployeeLoan(Base, SyncableMixin, TimestampMixin):
    """السُلف المالية للموظفين."""
    
    __tablename__ = "employee_loans"
    __table_args__ = (
        CheckConstraint(
            "status IN ('مستمرة', 'منتهية')",
            name="ck_employee_loans_status"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    total_loan_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    monthly_deduction: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='مستمرة', nullable=False)
    loan_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text)

        # حقل جديد لتتبع المبلغ المتبقي
    remaining_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )
    
    # العلاقات
    employee: Mapped["Employee"] = relationship(back_populates="loans")


class PayrollRecord(Base, SyncableMixin, TimestampMixin):
    """كشف الرواتب الشهري."""
    
    __tablename__ = "payroll_records"
    __table_args__ = (
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_payroll_month"),
        UniqueConstraint(
            "employee_id", "month", "year",
            name="uq_employee_monthly_payroll"
        ),
        CheckConstraint(
            "payment_status IN ('مسلم', 'معلق')",
            name="ck_payroll_status"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    basic_salary: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_allowances: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    total_deductions: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    loan_deduction: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    net_salary: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_status: Mapped[str] = mapped_column(
        String(20), default='معلق', nullable=False
    )
    payment_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # العلاقات
    employee: Mapped["Employee"] = relationship(back_populates="payroll_records")
    
    @property
    def display_period(self) -> str:
        """عرض الفترة."""
        return f"{self.month:02d}/{self.year}"