"""مصنع خدمة الصلاحيات."""

from app.services.auth_factory import AuthFactory


class PermissionsFactory:
    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        if cls.is_remote():
            from app.api_client.services.permissions_api import (
                PermissionsApiService,
            )
            client = AuthFactory.get_api_client()
            return PermissionsApiService(client)
        return None