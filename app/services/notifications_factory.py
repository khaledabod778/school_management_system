"""مصنع خدمة الإشعارات."""

from app.services.auth_factory import AuthFactory


class NotificationsFactory:
    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        if cls.is_remote():
            from app.api_client.services.notifications_api import (
                NotificationsApiService,
            )
            client = AuthFactory.get_api_client()
            return NotificationsApiService(client)
        return None