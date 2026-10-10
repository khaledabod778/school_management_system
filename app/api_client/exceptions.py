"""
استثناءات API - مستقلة عن استثناءات التطبيق المحلية.

تجعل الكود قادراً على التعامل مع أخطاء الشبكة بشكل موحد.
"""


class ApiError(Exception):
    """الخطأ الأساسي لكل أخطاء API."""

    def __init__(self, message: str, status_code: int = 0):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NetworkError(ApiError):
    """فشل الاتصال بالشبكة."""

    def __init__(self, message: str = "تعذّر الاتصال بالسيرفر"):
        super().__init__(message, 0)


class TimeoutError(ApiError):
    """انتهت مهلة الاتصال."""

    def __init__(self, message: str = "انتهت مهلة الاتصال"):
        super().__init__(message, 0)


class AuthenticationError(ApiError):
    """401 - فشل المصادقة."""

    def __init__(self, message: str = "فشل المصادقة"):
        super().__init__(message, 401)


class PermissionError(ApiError):
    """403 - صلاحيات غير كافية."""

    def __init__(self, message: str = "صلاحيات غير كافية"):
        super().__init__(message, 403)


class NotFoundError(ApiError):
    """404 - العنصر غير موجود."""

    def __init__(self, message: str = "العنصر غير موجود"):
        super().__init__(message, 404)


class ValidationError(ApiError):
    """422 - بيانات غير صالحة."""

    def __init__(self, message: str = "بيانات غير صالحة"):
        super().__init__(message, 422)


class ServerError(ApiError):
    """500+ - خطأ في السيرفر."""

    def __init__(self, message: str = "خطأ في السيرفر"):
        super().__init__(message, 500)