"""مصنع خدمة سجل العمليات."""

from app.services.auth_factory import AuthFactory


class AuditLogFactory:
    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        if cls.is_remote():
            from app.api_client.services.audit_log_api import (
                AuditLogApiService,
            )
            client = AuthFactory.get_api_client()
            return AuditLogApiService(client)
        return None