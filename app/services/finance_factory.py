"""مصنع خدمة المالية."""

from app.services.auth_factory import AuthFactory


class FinanceFactory:
    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        if cls.is_remote():
            from app.api_client.services.finance_api import FinanceApiService
            client = AuthFactory.get_api_client()
            return FinanceApiService(client)
        return None