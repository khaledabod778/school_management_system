"""
النماذج التشغيلية: الحضور، الواجبات، السلوك، الجداول، الامتحانات.
"""

from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import (
    Date, DateTime, ForeignKey, Integer, Numeric,
    String, Text, Time, UniqueConstraint, CheckConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .sync_mixin import SyncableMixin

class DailyAttendance(Base, SyncableMixin, TimestampMixin):
    """تسجيل الحضور والغياب اليومي."""
    
    __tablename__ = "daily_attendance"
    __table_args__ = (
        UniqueConstraint(
            "student_id", "attendance_date",
            name="uq_student_daily_attendance"
        ),
        CheckConstraint(
            "status IN ('حاضر', 'غائب', 'متأخر', 'غائب بمبرر')",
            name="ck_daily_attendance_status"
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
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='حاضر', nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # العلاقات
    student: Mapped["Student"] = relationship(back_populates="attendance")
    
    @property
    def is_present(self) -> bool:
        """التحقق من الحضور."""
        return self.status == 'حاضر'
    
    @property
    def is_absent(self) -> bool:
        """التحقق من الغياب."""
        return self.status in ('غائب', 'غائب بمبرر')
    
    @property
    def status_display(self) -> str:
        """عرض الحالة مع اللون."""
        status_colors = {
            'حاضر': 'green',
            'غائب': 'red',
            'متأخر': 'orange',
            'غائب بمبرر': 'blue'
        }
        return f"{self.status} ({status_colors.get(self.status, 'gray')})"


class MonthlyEvaluation(Base, SyncableMixin, TimestampMixin):
    """رصد التقييمات والأعمال الشهرية."""
    
    __tablename__ = "monthly_evaluations"
    __table_args__ = (
        UniqueConstraint(
            "student_id", "academic_year_id", "subject_id", "term", "month",
            name="uq_student_monthly_eval"
        ),
        CheckConstraint("term IN (1, 2)", name="ck_monthly_eval_term"),
        CheckConstraint("month IN (1, 2, 3)", name="ck_monthly_eval_month"),
        CheckConstraint("written_score <= 40.00", name="ck_written_score_max"),
        CheckConstraint("oral_score <= 20.00", name="ck_oral_score_max"),
        CheckConstraint("homework_score <= 20.00", name="ck_homework_score_max"),
        CheckConstraint("attendance_score <= 20.00", name="ck_attendance_score_max"),
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
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id"), nullable=False
    )
    term: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    written_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0.00"), nullable=False
    )
    oral_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0.00"), nullable=False
    )
    homework_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0.00"), nullable=False
    )
    attendance_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0.00"), nullable=False
    )
    # total_month_score هو عمود محسوب (GENERATED ALWAYS AS STORED)
    # سنحسبه كـ property بدلاً من العمود المحسوب في PostgreSQL
    
    # العلاقات
    student: Mapped["Student"] = relationship(back_populates="evaluations")
    
    @property
    def total_month_score(self) -> Decimal:
        """المجموع الكلي للشهر (محسوب)."""
        return (
            self.written_score +
            self.oral_score +
            self.homework_score +
            self.attendance_score
        )
    
    @property
    def percentage(self) -> float:
        """النسبة المئوية."""
        return float(self.total_month_score) * 100 / 100.0
    
    @property
    def grade_letter(self) -> str:
        """التقدير."""
        total = float(self.total_month_score)
        if total >= 90:
            return "ممتاز"
        elif total >= 80:
            return "جيد جداً"
        elif total >= 70:
            return "جيد"
        elif total >= 60:
            return "مقبول"
        elif total >= 50:
            return "ضعيف"
        else:
            return "راسب"


class TermExamScore(Base, SyncableMixin, TimestampMixin):
    """رصد درجات نهاية الفصل."""
    
    __tablename__ = "term_exam_scores"
    __table_args__ = (
        UniqueConstraint(
            "student_id", "academic_year_id", "subject_id", "term",
            name="uq_student_term_exam"
        ),
        CheckConstraint("term IN (1, 2)", name="ck_term_exam_term"),
        CheckConstraint("exam_score <= 30.00", name="ck_exam_score_max"),
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
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id"), nullable=False
    )
    term: Mapped[int] = mapped_column(Integer, nullable=False)
    exam_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0.00"), nullable=False
    )
    
    # العلاقات
    student: Mapped["Student"] = relationship(back_populates="exam_scores")


class Homework(Base, SyncableMixin, TimestampMixin):
    """إدارة الواجبات المنزلية."""
    
    __tablename__ = "homeworks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id"), nullable=False
    )
    grade_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("grades.id"), nullable=False
    )
    section_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sections.id"), nullable=False
    )
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id"), nullable=False
    )
    homework_date: Mapped[date] = mapped_column(Date, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    @property
    def is_overdue(self) -> bool:
        """التحقق من تجاوز تاريخ الاستحقاق."""
        return self.due_date < date.today()
    
    @property
    def display_title(self) -> str:
        """عنوان الواجب مع المادة."""
        return f"{self.title} - {self.subject_id}"


class BehavioralRecord(Base, SyncableMixin, TimestampMixin):
    """المتابعة السلوكية والتوجيه التربوي."""
    
    __tablename__ = "behavioral_records"
    __table_args__ = (
        CheckConstraint(
            "behavior_type IN ('تميز', 'مخالفة', 'تنبيه أخصائي')",
            name="ck_behavioral_records_type"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id"), nullable=False
    )
    behavior_type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text)
    action_taken: Mapped[Optional[str]] = mapped_column(Text)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # العلاقات
    student: Mapped["Student"] = relationship(back_populates="behavioral_records")
    
    @property
    def type_color(self) -> str:
        """لون نوع السلوك."""
        colors = {
            'تميز': 'green',
            'مخالفة': 'red',
            'تنبيه أخصائي': 'orange'
        }
        return colors.get(self.behavior_type, 'gray')


class WeeklySchedule(Base, SyncableMixin, TimestampMixin):
    """الجدول المدرسي الأسبوعي."""
    
    __tablename__ = "weekly_schedules"
    __table_args__ = (
        UniqueConstraint(
            "academic_year_id", "term", "section_id", "day_of_week", "period_number",
            name="uq_schedule_slot"
        ),
        CheckConstraint("term IN (1, 2)", name="ck_schedule_term"),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id"), nullable=False
    )
    term: Mapped[int] = mapped_column(Integer, nullable=False)
    grade_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("grades.id"), nullable=False
    )
    section_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sections.id"), nullable=False
    )
    day_of_week: Mapped[str] = mapped_column(String(20), nullable=False)
    period_number: Mapped[int] = mapped_column(Integer, nullable=False)
    subject_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("subjects.id")
    )
    teacher_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("employees.id")
    )
    
    @property
    def day_display(self) -> str:
        """عرض اسم اليوم."""
        days = {
            'saturday': 'السبت',
            'sunday': 'الأحد',
            'monday': 'الاثنين',
            'tuesday': 'الثلاثاء',
            'wednesday': 'الأربعاء',
            'thursday': 'الخميس',
            'friday': 'الجمعة'
        }
        return days.get(self.day_of_week, self.day_of_week)


class MonthlyExamSchedule(Base, SyncableMixin, TimestampMixin):
    """جداول الامتحانات الشهرية."""
    
    __tablename__ = "monthly_exam_schedules"
    __table_args__ = (
        CheckConstraint("term IN (1, 2)", name="ck_monthly_exam_term"),
        CheckConstraint("month IN (1, 2, 3)", name="ck_monthly_exam_month"),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id"), nullable=False
    )
    term: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    grade_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("grades.id"), nullable=False
    )
    section_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sections.id")
    )
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id"), nullable=False
    )
    exam_date: Mapped[date] = mapped_column(Date, nullable=False)
    day_name: Mapped[str] = mapped_column(String(20), nullable=False)
    period_number: Mapped[int] = mapped_column(Integer, nullable=False)


class FinalExamSchedule(Base, SyncableMixin, TimestampMixin):
    """جداول الامتحانات النهائية."""
    
    __tablename__ = "final_exam_schedules"
    __table_args__ = (
        CheckConstraint("term IN (1, 2)", name="ck_final_exam_term"),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic_years.id"), nullable=False
    )
    term: Mapped[int] = mapped_column(Integer, nullable=False)
    grade_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("grades.id"), nullable=False
    )
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id"), nullable=False
    )
    exam_date: Mapped[date] = mapped_column(Date, nullable=False)
    day_name: Mapped[str] = mapped_column(String(20), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    
    @property
    def duration(self) -> str:
        """مدة الامتحان."""
        if self.start_time and self.end_time:
            duration = (
                datetime.combine(date.today(), self.end_time) -
                datetime.combine(date.today(), self.start_time)
            )
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            return f"{hours} ساعة و {minutes} دقيقة"
        return "غير محدد"