"""
التعريفات الثابتة والقيم المسموحة للنظام.
"""

from enum import Enum


class AcademicYearStatus(str, Enum):
    """حالات السنة الدراسية."""
    CURRENT = "current"
    CLOSED = "closed"
    UPCOMING = "upcoming"


class EmployeeStatus(str, Enum):
    """حالات الموظف."""
    ACTIVE = "نشط"
    ON_LEAVE = "إجازة"
    RESIGNED = "مستقيل"


class EmployeeGender(str, Enum):
    """جنس الموظف."""
    MALE = "ذكر"
    FEMALE = "أنثى"


class PaymentMethod(str, Enum):
    """طرق الدفع."""
    CASH = "نقداً"
    BANK_TRANSFER = "تحويل بنكي"
    CARD = "كريمي/حاسب"
    CHECK = "شيك"


class StudentStatus(str, Enum):
    """حالات الطالب."""
    ACTIVE = "مستمر"
    WITHDRAWN = "انسحاب"
    SUSPENDED = "موقف"
    GRADUATED = "خريج"


class EnrollmentType(str, Enum):
    """أنواع قيد الطالب."""
    NEW = "مستجد"
    TRANSFERRED = "محول"
    RETAINED = "باقي"


class StudentGender(str, Enum):
    """جنس الطالب."""
    MALE = "ذكر"
    FEMALE = "أنثى"


class ParentCategory(str, Enum):
    """فئات أولياء الأمور."""
    NORMAL = "عادي"
    VIP = "VIP"
    SPONSORSHIP = "كفالة"


class AttendanceStatus(str, Enum):
    """حالات الحضور."""
    PRESENT = "حاضر"
    ABSENT = "غائب"
    LATE = "متأخر"
    EXCUSED = "غائب بمبرر"


class BehaviorType(str, Enum):
    """أنواع السلوك."""
    EXCELLENCE = "تميز"
    VIOLATION = "مخالفة"
    SPECIALIST_ALERT = "تنبيه أخصائي"


class InstallmentType(str, Enum):
    """أنواع الأقساط."""
    PREVIOUS_DEBT = "previous_debt"
    REGULAR = "regular"


class ReceiptStatus(str, Enum):
    """حالات سند القبض."""
    ACTIVE = "نشط"
    CANCELLED = "ملغى"


class PaymentTarget(str, Enum):
    """أهداف الدفع."""
    PREVIOUS_DEBT = "previous_debt"
    CURRENT_FEE = "current_fee"


class ExpenseCategory(str, Enum):
    """فئات المصروفات."""
    MATERIALS = "مشتريات مواد"
    MAINTENANCE = "صيانة وتشغيل"
    EVENTS = "فعاليات واحتفالات"
    ACTIVITIES = "أنشطة مدرسية"
    OTHER = "أخرى"


class AllowanceDeductionType(str, Enum):
    """أنواع البدلات والخصومات."""
    ALLOWANCE = "بدل"
    INCENTIVE = "حافز"
    BONUS = "مكافأة"
    DEDUCTION = "خصم"
    ABSENCE = "غياب"


class LoanStatus(str, Enum):
    """حالات السلفة."""
    ACTIVE = "مستمرة"
    COMPLETED = "منتهية"


class PayrollStatus(str, Enum):
    """حالات الراتب."""
    PAID = "مسلم"
    PENDING = "معلق"


class UserStatus(str, Enum):
    """حالات المستخدم."""
    ACTIVE = "نشط"
    SUSPENDED = "موقف"


class NotificationType(str, Enum):
    """أنواع الإشعارات."""
    ATTENDANCE = "حضور"
    ABSENCE = "غياب"
    HOMEWORK = "واجبات"
    BEHAVIOR = "سلوك"
    RESULTS = "نتائج"
    FEES = "رسوم"
    GENERAL = "عام"


class NotificationTargetType(str, Enum):
    """أنواع مستهدفي الإشعارات."""
    ALL = "all"
    GRADE = "grade"
    SECTION = "section"
    PARENT = "parent"


class DeliveryStatus(str, Enum):
    """حالات تسليم الإشعارات."""
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class OperationType(str, Enum):
    """أنواع العمليات للتدقيق."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    CLOSE = "close"
    CANCEL = "cancel"
    PRINT = "print"
    EXPORT = "export"
    IMPORT = "import"


class ImportExportStatus(str, Enum):
    """حالات عمليات الاستيراد والتصدير."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class FinalResult(str, Enum):
    """نتائج الطالب النهائية."""
    PASSED = "passed"
    FAILED = "failed"
    SECOND_ROUND = "second_round"


class PromotionStatus(str, Enum):
    """حالات الترفيع."""
    PROMOTED = "promoted"
    RETAINED = "retained"
    WITHDRAWN = "withdrawn"