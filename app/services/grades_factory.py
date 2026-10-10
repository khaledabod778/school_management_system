"""مصنع خدمة الدرجات/الشهادات/الأوائل."""

from app.services.auth_factory import AuthFactory


class GradesFactory:
    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        if cls.is_remote():
            from app.api_client.services.grades_api import GradesApiService
            client = AuthFactory.get_api_client()
            return GradesApiService(client)
        return None