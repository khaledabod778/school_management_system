"""مصنع خدمة الموظفين/المستخدمين/الملف الشخصي."""

from app.services.auth_factory import AuthFactory


class HrUsersFactory:
    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        if cls.is_remote():
            from app.api_client.services.hr_users_api import HrUsersApiService
            client = AuthFactory.get_api_client()
            return HrUsersApiService(client)
        return None