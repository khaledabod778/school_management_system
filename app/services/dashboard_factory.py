"""
مصنع خدمة لوحات التحكم - local أو remote.
"""

import logging
from app.services.auth_factory import AuthFactory

logger = logging.getLogger(__name__)


class DashboardFactory:
    """مصنع لخدمة لوحات التحكم."""

    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        """إرجاع الخدمة المناسبة."""
        if cls.is_remote():
            from app.api_client.services.dashboard_api import DashboardApiService
            client = AuthFactory.get_api_client()
            return DashboardApiService(client)
        return None