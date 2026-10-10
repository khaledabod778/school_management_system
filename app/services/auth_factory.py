"""
مصنع خدمة المصادقة - يختار بين Local DB و Remote API.
"""

import logging
from typing import Optional

from app.core.config import config_manager

logger = logging.getLogger(__name__)


class AuthFactory:
    """مصنع للتبديل بين Local و Remote."""

    _api_client = None

    @classmethod
    def get_api_client(cls):
        """ApiClient singleton."""
        if cls._api_client is None:
            from app.api_client import ApiClient
            cfg = config_manager.app_config
            cls._api_client = ApiClient(
                base_url=cfg.api_url,
                timeout=cfg.api_timeout,
            )
        return cls._api_client

    @classmethod
    def is_remote_mode(cls) -> bool:
        """هل نستخدم API؟"""
        mode = config_manager.app_config.api_mode
        return mode in ('remote', 'auto')

    @classmethod
    def get_auth_service(cls):
        """الخدمة المناسبة."""
        if cls.is_remote_mode():
            from app.api_client.services.auth_api import AuthServiceRemote
            return AuthServiceRemote(cls.get_api_client())
        else:
            from app.services.auth_service import AuthService
            return AuthService