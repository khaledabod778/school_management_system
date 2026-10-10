"""
مصنع خدمة الطلاب - يختار local أو remote.
"""

import logging
from typing import Optional

from app.core.config import config_manager
from app.services.auth_factory import AuthFactory

logger = logging.getLogger(__name__)


class StudentFactory:
    """مصنع لخدمة الطلاب."""

    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        """
        إرجاع الخدمة المناسبة.

        Returns:
            StudentApiService (remote) أو None (local)
            نُعيد None للوضع local لأن الصفحة ستستخدم session_scope مباشرة
        """
        if cls.is_remote():
            from app.api_client.services.student_api import StudentApiService
            client = AuthFactory.get_api_client()
            return StudentApiService(client)
        return None