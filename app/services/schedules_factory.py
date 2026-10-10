"""مصنع خدمة الجداول الدراسية."""

from app.services.auth_factory import AuthFactory


class SchedulesFactory:
    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        if cls.is_remote():
            from app.api_client.services.schedules_api import (
                SchedulesApiService,
            )
            client = AuthFactory.get_api_client()
            return SchedulesApiService(client)
        return None