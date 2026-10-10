"""
مصنع خدمة أولياء الأمور - يختار local أو remote.
"""

import logging
from app.services.auth_factory import AuthFactory

logger = logging.getLogger(__name__)


class ParentFactory:
    """مصنع لخدمة أولياء الأمور."""

    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        """إرجاع الخدمة المناسبة."""
        if cls.is_remote():
            from app.api_client.services.parent_api import ParentApiService
            client = AuthFactory.get_api_client()
            return ParentApiService(client)
        return None