"""
حفظ JWT token بأمان.

يستخدم نفس نمط secrets_manager (ملف في مجلد المستخدم).
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class TokenStore:
    """حفظ/قراءة token + user info."""

    def __init__(self, name: str = "api_token.json"):
        # المسار: ~/.school_erp/api_token.json
        import sys
        import os

        if sys.platform == 'win32':
            base = Path(os.environ.get('APPDATA', Path.home()))
        else:
            base = Path.home()

        config_dir = base / '.school_erp'
        config_dir.mkdir(parents=True, exist_ok=True)
        self._path = config_dir / name

    def save(self, token: str, user_info: dict, api_url: str):
        """حفظ token."""
        try:
            data = {
                'token': token,
                'user_info': user_info,
                'api_url': api_url,
            }
            self._path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding='utf-8',
            )
            logger.debug(f"✅ token محفوظ: {self._path}")
        except Exception as e:
            logger.warning(f"فشل حفظ token: {e}")

    def load(self) -> Optional[dict]:
        """قراءة token محفوظ."""
        try:
            if not self._path.exists():
                return None
            return json.loads(self._path.read_text(encoding='utf-8'))
        except Exception as e:
            logger.warning(f"فشل قراءة token: {e}")
            return None

    def clear(self):
        """مسح token (عند logout)."""
        try:
            if self._path.exists():
                self._path.unlink()
                logger.debug("🗑️ token مُسح")
        except Exception as e:
            logger.warning(f"فشل مسح token: {e}")