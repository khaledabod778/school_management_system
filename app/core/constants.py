"""
الثوابت العامة للنظام.
"""

# معلومات التطبيق
APP_NAME = "نظام إدارة المدرسة"
APP_VERSION = "1.0.0"
APP_ORGANIZATION = "School Management System"
APP_DESCRIPTION = "نظام متكامل لإدارة المدارس الأهلية"

# أسماء أيام الأسبوع
DAYS_OF_WEEK = [
    ("saturday", "السبت"),
    ("sunday", "الأحد"),
    ("monday", "الاثنين"),
    ("tuesday", "الثلاثاء"),
    ("wednesday", "الأربعاء"),
    ("thursday", "الخميس"),
    ("friday", "الجمعة"),
]

# أشهر السنة
MONTHS_ARABIC = [
    (1, "يناير"),
    (2, "فبراير"),
    (3, "مارس"),
    (4, "أبريل"),
    (5, "مايو"),
    (6, "يونيو"),
    (7, "يوليو"),
    (8, "أغسطس"),
    (9, "سبتمبر"),
    (10, "أكتوبر"),
    (11, "نوفمبر"),
    (12, "ديسمبر"),
]

# الأشهر الدراسية (شهري/فصلي)
STUDY_MONTHS = [
    (1, "الشهر الأول"),
    (2, "الشهر الثاني"),
    (3, "الشهر الثالث"),
]

# الفصول الدراسية
TERMS = [
    (1, "الفصل الأول"),
    (2, "الفصل الثاني"),
]

# المراحل الدراسية
STAGES = [
    "رياض الأطفال",
    "الابتدائي",
    "الإعدادي",
    "الثانوي",
]

# أسماء الشعب الافتراضية
DEFAULT_SECTION_NAMES = ["أ", "ب", "ج", "د", "هـ", "و"]

# أنواع الرسوم الافتراضية
DEFAULT_FEE_TYPES = [
    "رسوم دراسية",
    "رسوم تسجيل",
    "زي مدرسي",
    "كتب",
    "مواصلات",
    "أنشطة",
    "أخرى",
]

# تقييمات الدرجات
GRADE_RANGES = [
    (90, 100, "ممتاز"),
    (80, 89, "جيد جداً"),
    (70, 79, "جيد"),
    (60, 69, "مقبول"),
    (50, 59, "ضعيف"),
    (0, 49, "راسب"),
]

# حدود الدرجات
MONTHLY_SCORE_LIMITS = {
    'written': 40.00,
    'oral': 20.00,
    'homework': 20.00,
    'attendance': 20.00,
}

TERM_EXAM_SCORE_LIMIT = 30.00
TOTAL_MONTHLY_SCORE = 100.00
TOTAL_TERM_SCORE = 100.00

# إعدادات قاعدة البيانات
DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT = 5432
DEFAULT_DB_NAME = "school_management"
DEFAULT_DB_USER = "postgres"
DEFAULT_DB_PASSWORD = "postgres"

# إعدادات المزامنة
SYNC_INTERVAL_SECONDS = 60  # فحص المزامنة كل دقيقة
MAX_SYNC_RETRIES = 3
SYNC_TIMEOUT_SECONDS = 30

# إعدادات النسخ الاحتياطي
BACKUP_RETENTION_DAYS = 30
MAX_BACKUP_FILES = 50

# إعدادات التقارير
PAGE_SIZE_A4 = (210, 297)  # مم
PAGE_MARGIN = 20  # مم
DEFAULT_FONT_SIZE = 10
HEADER_FONT_SIZE = 12
TITLE_FONT_SIZE = 16

# إعدادات واجهة المستخدم
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 768
DEFAULT_FONT_FAMILY = "Segoe UI"
ARABIC_FONT_FAMILY = "Cairo"

# مسارات الملفات
RESOURCES_DIR = "resources"
ICONS_DIR = "resources/icons"
STYLES_DIR = "resources/styles"
FONTS_DIR = "resources/fonts"
BACKUP_DIR = "backups"
EXPORT_DIR = "exports"
UPLOAD_DIR = "uploads"

# أنواع المستندات المدعومة
ALLOWED_DOCUMENT_TYPES = [
    "شهادة ميلاد",
    "بطاقة شخصية",
    "شهادة انتقالية",
    "صورة شخصية",
    "أخرى",
]

# صيغ الملفات المدعومة
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
ALLOWED_DOCUMENT_EXTENSIONS = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".png"]

# أقصى حجم للملفات (بالميجابايت)
MAX_UPLOAD_SIZE_MB = 10