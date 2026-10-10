"""مصنع خدمة المتابعة اليومية."""

from app.services.auth_factory import AuthFactory


class OperationsFactory:
    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        if cls.is_remote():
            from app.api_client.services.operations_api import (
                OperationsApiService,
            )
            client = AuthFactory.get_api_client()
            return OperationsApiService(client)
        return None