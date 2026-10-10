"""مصنع خدمة توزيع الطلاب."""

from app.services.auth_factory import AuthFactory


class StudentDistributionFactory:
    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        if cls.is_remote():
            from app.api_client.services.student_distribution_api import (
                StudentDistributionApiService,
            )
            client = AuthFactory.get_api_client()
            return StudentDistributionApiService(client)
        return None