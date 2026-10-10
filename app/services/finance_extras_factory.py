"""مصنع خدمة المالية الإضافية."""

from app.services.auth_factory import AuthFactory


class FinanceExtrasFactory:
    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        if cls.is_remote():
            from app.api_client.services.finance_extras_api import (
                FinanceExtrasApiService,
            )
            client = AuthFactory.get_api_client()
            return FinanceExtrasApiService(client)
        return None