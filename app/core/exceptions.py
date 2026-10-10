"""
الاستثناءات المخصصة للنظام.
"""


class AppException(Exception):
    """الاستثناء الأساسي للتطبيق."""
    
    def __init__(self, message: str = "حدث خطأ في التطبيق", code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """تحويل الاستثناء إلى قاموس."""
        return {
            'code': self.code,
            'message': self.message,
        }


class DatabaseConnectionError(AppException):
    """خطأ في الاتصال بقاعدة البيانات."""
    
    def __init__(self, message: str = "فشل الاتصال بقاعدة البيانات"):
        super().__init__(message, "DB_CONNECTION_ERROR")


class DatabaseQueryError(AppException):
    """خطأ في استعلام قاعدة البيانات."""
    
    def __init__(self, message: str = "فشل تنفيذ الاستعلام"):
        super().__init__(message, "DB_QUERY_ERROR")


class ValidationError(AppException):
    """خطأ في التحقق من البيانات."""
    
    def __init__(self, message: str = "بيانات غير صالحة"):
        super().__init__(message, "VALIDATION_ERROR")


class NotFoundError(AppException):
    """العنصر غير موجود."""
    
    def __init__(self, message: str = "العنصر غير موجود"):
        super().__init__(message, "NOT_FOUND_ERROR")


class AuthenticationError(AppException):
    """خطأ في المصادقة."""
    
    def __init__(self, message: str = "فشل المصادقة"):
        super().__init__(message, "AUTH_ERROR")


class AuthorizationError(AppException):
    """خطأ في الصلاحيات."""
    
    def __init__(self, message: str = "صلاحيات غير كافية"):
        super().__init__(message, "AUTHORIZATION_ERROR")


class DuplicateError(AppException):
    """خطأ في التكرار."""
    
    def __init__(self, message: str = "العنصر موجود مسبقاً"):
        super().__init__(message, "DUPLICATE_ERROR")


class BusinessLogicError(AppException):
    """خطأ في منطق العمل."""
    
    def __init__(self, message: str = "خطأ في منطق العمل"):
        super().__init__(message, "BUSINESS_LOGIC_ERROR")


class SyncError(AppException):
    """خطأ في المزامنة."""
    
    def __init__(self, message: str = "فشل المزامنة"):
        super().__init__(message, "SYNC_ERROR")


class BackupError(AppException):
    """خطأ في النسخ الاحتياطي."""
    
    def __init__(self, message: str = "فشل النسخ الاحتياطي"):
        super().__init__(message, "BACKUP_ERROR")


class PrintError(AppException):
    """خطأ في الطباعة."""
    
    def __init__(self, message: str = "فشل الطباعة"):
        super().__init__(message, "PRINT_ERROR")


class ImportExportError(AppException):
    """خطأ في الاستيراد أو التصدير."""
    
    def __init__(self, message: str = "فشل الاستيراد/التصدير"):
        super().__init__(message, "IMPORT_EXPORT_ERROR")