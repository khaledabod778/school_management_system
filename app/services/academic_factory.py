"""مصنع خدمة التهيئة الأكاديمية."""

from app.services.auth_factory import AuthFactory


class AcademicFactory:
    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        if cls.is_remote():
            from app.api_client.services.academic_api import AcademicApiService
            client = AuthFactory.get_api_client()
            return AcademicApiService(client)
        return None