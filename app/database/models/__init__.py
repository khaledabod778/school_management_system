"""
تجميع جميع نماذج قاعدة البيانات.
"""

from .base import Base, TimestampMixin, AuditMixin
from .academic import (
    SchoolInfo,
    AcademicYear,
    Grade,
    Section,
    Subject
)
from .users import (
    Role,
    Employee,
    User,
    TeacherSubjectSection,
    Permission,
    RolePermission
)
from .students import (
    Parent,
    ParentDevice,
    Student,
    StudentAcademicHistory,
    StudentDocument
)
from .finance import (
    FeeType,
    GradeFeeStructure,
    StudentFee,
    FeeInstallment,
    Receipt,
    ExpenseVoucher,
    EmployeeAllowanceDeduction,
    EmployeeLoan,
    PayrollRecord
)
from .operations import (
    DailyAttendance,
    MonthlyEvaluation,
    TermExamScore,
    Homework,
    BehavioralRecord,
    WeeklySchedule,
    MonthlyExamSchedule,
    FinalExamSchedule
)
from .notifications import (
    Notification,
    NotificationLog
)
from .system import (
    SystemAuditLog,
    PrintArchive,
    ImportExportLog,
    AnnualClosingLog,
    BackupLog
)

# قائمة بجميع النماذج
__all__ = [
    # Base
    'Base',
    'TimestampMixin',
    'AuditMixin',
    
    # Academic
    'SchoolInfo',
    'AcademicYear',
    'Grade',
    'Section',
    'Subject',
    
    # Users
    'Role',
    'Employee',
    'User',
    'TeacherSubjectSection',
    'Permission',
    'RolePermission',
    
    # Students
    'Parent',
    'ParentDevice',
    'Student',
    'StudentAcademicHistory',
    'StudentDocument',
    
    # Finance
    'FeeType',
    'GradeFeeStructure',
    'StudentFee',
    'FeeInstallment',
    'Receipt',
    'ExpenseVoucher',
    'EmployeeAllowanceDeduction',
    'EmployeeLoan',
    'PayrollRecord',
    
    # Operations
    'DailyAttendance',
    'MonthlyEvaluation',
    'TermExamScore',
    'Homework',
    'BehavioralRecord',
    'WeeklySchedule',
    'MonthlyExamSchedule',
    'FinalExamSchedule',
    
    # Notifications
    'Notification',
    'NotificationLog',
    
    # System
    'SystemAuditLog',
    'PrintArchive',
    'ImportExportLog',
    'AnnualClosingLog',
    'BackupLog',
]