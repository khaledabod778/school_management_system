"""
Factory لاختيار AuthService (local أو remote).
"""

import logging
from typing import Optional

from app.core.config import config_manager
from app.api_client.client import ApiClient
from app.api_client.services.auth_api import AuthServiceRemote

logger = logging.getLogger(__name__)


class AuthFactory:
    """مصنع خدمة المصادقة."""

    _api_client: Optional[ApiClient] = None

    @classmethod
    def get_api_client(cls) -> ApiClient:
        """ApiClient singleton."""
        if cls._api_client is None:
            cfg = config_manager.app_config
            cls._api_client = ApiClient(
                base_url=cfg.api_url,
                timeout=cfg.api_timeout,
            )
        return cls._api_client

    @classmethod
    def is_remote_mode(cls) -> bool:
        """هل نستخدم API؟"""
        return config_manager.app_config.api_mode in ('remote', 'auto')

    @classmethod
    def get_auth_service(cls):
        """
        إرجاع الخدمة المناسبة.

        Returns:
            AuthServiceRemote إذا كان api_mode = remote/auto
            AuthService (local) في حالات أخرى
        """
        if cls.is_remote_mode():
            client = cls.get_api_client()
            return AuthServiceRemote(client)
        else:
            from app.services.auth_service import AuthService
            return AuthService

    @classmethod
    def get_client(cls) -> Optional[ApiClient]:
        """ApiClient إذا كان في وضع remote."""
        if cls.is_remote_mode():
            return cls.get_api_client()
        return None