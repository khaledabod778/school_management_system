"""
AuthService للـ remote - يعكس واجهة AuthService المحلية.
"""

import logging
from typing import Optional

from app.api_client.client import ApiClient
from app.api_client.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class AuthServiceRemote:
    """
    خدمة المصادقة عن بُعد.

    الواجهة مُطابقة لـ AuthService المحلي حتى يسهل التبديل.
    """

    def __init__(self, client: ApiClient):
        self.client = client

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> dict:
        """
        مصادقة المستخدم.

        Returns:
            dict مع 'user' و 'access_token'

        Raises:
            AuthenticationError: عند فشل المصادقة
        """
        try:
            result = self.client.login(username, password)
            return result
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"فشل مصادقة remote: {e}")
            raise AuthenticationError(str(e))

    def get_current_user(self) -> Optional[dict]:
        """المستخدم الحالي."""
        if not self.client.is_authenticated:
            return None
        return self.client.current_user

    def logout(self):
        """تسجيل خروج."""
        self.client.logout()