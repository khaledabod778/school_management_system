"""
مدير الأسرار - تشفير كلمات المرور والمفاتيح الحساسة.

v2.0:
- دعم strict mode في decrypt لكشف الأخطاء بدلاً من إخفائها
- رسائل خطأ واضحة مع الحلول
"""

import os
import sys
import stat
import logging
import base64
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


class SecretsManager:
    """مدير تشفير الأسرار (Singleton)."""

    _instance: Optional['SecretsManager'] = None
    _PREFIX = "ENC:"

    # ✅ الحقول التي تُشفَّر تلقائياً
    ENCRYPTED_FIELDS = frozenset({
        'local_password',
        'cloud_password',
        'cloud_api_key',
    })

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._fernet: Optional[Fernet] = None
        self._key_path = self._get_key_path()
        self._initialized = True

    # ==================== مسار المفتاح ====================

    @staticmethod
    def _get_key_path() -> Path:
        """مسار مفتاح التشفير الرئيسي (خارج المشروع)."""
        if sys.platform == 'win32':
            base = Path(os.environ.get('APPDATA', Path.home()))
        else:
            base = Path.home()
        key_dir = base / '.school_erp'
        key_dir.mkdir(parents=True, exist_ok=True)
        return key_dir / 'master.key'

    # ==================== Fernet ====================

    def _get_fernet(self) -> Fernet:
        """الحصول على كائن Fernet (lazy)."""
        if self._fernet is not None:
            return self._fernet

        if self._key_path.exists():
            key = self._key_path.read_bytes()
            try:
                self._fernet = Fernet(key)
                return self._fernet
            except Exception as e:
                logger.error(f"مفتاح التشفير تالف: {e}")
                raise RuntimeError(
                    f"مفتاح التشفير في {self._key_path} تالف. "
                    "يجب حذفه يدوياً لإعادة الإنشاء."
                )

        # أنشئ مفتاحاً جديداً
        key = Fernet.generate_key()
        self._key_path.write_bytes(key)

        try:
            if sys.platform != 'win32':
                os.chmod(self._key_path, stat.S_IRUSR | stat.S_IWUSR)
        except Exception as e:
            logger.warning(f"فشل ضبط أذونات المفتاح: {e}")

        self._fernet = Fernet(key)
        logger.info(f"🔐 تم إنشاء مفتاح تشفير جديد: {self._key_path}")
        return self._fernet

    # ==================== التشفير ====================

    def encrypt(self, value: str) -> str:
        """تشفير قيمة نصية."""
        if not value:
            return value

        # مشفّرة مسبقاً → اتركها
        if value.startswith(self._PREFIX):
            return value

        try:
            f = self._get_fernet()
            encrypted = f.encrypt(value.encode('utf-8'))
            return self._PREFIX + base64.b64encode(encrypted).decode('ascii')
        except Exception as e:
            logger.error(f"فشل التشفير: {e}")
            return value

    def decrypt(self, value: str, strict: bool = True) -> str:
        """
        فك تشفير قيمة.

        Args:
            value: القيمة المشفّرة
            strict: إذا True، يرفع ValueError عند الفشل.
                    إذا False، يُرجع القيمة الأصلية بصمت.

        Raises:
            ValueError: عندما strict=True وفشل فك التشفير.
        """
        if not value:
            return value

        # قيمة legacy (غير مشفّرة)
        if not value.startswith(self._PREFIX):
            return value

        try:
            f = self._get_fernet()
            encoded = value[len(self._PREFIX):]
            encrypted = base64.b64decode(encoded)
            decrypted = f.decrypt(encrypted)
            return decrypted.decode('utf-8')

        except InvalidToken:
            msg = (
                f"❌ فشل فك التشفير: المفتاح في {self._key_path} "
                f"لا يطابق القيمة المشفّرة.\n"
                f"   الأسباب المحتملة:\n"
                f"   • master.key تغيّر أو فُقد\n"
                f"   • config.json من جهاز آخر\n"
                f"   • القيمة تالفة أو غير مكتملة\n"
                f"   الحل: python scripts/fix_passwords.py"
            )
            logger.error(msg)

            if strict:
                raise ValueError(msg)
            return value

        except Exception as e:
            logger.error(f"فشل فك التشفير: {e}")
            if strict:
                raise
            return value

    # ==================== معالجة dict ====================

    def encrypt_dict(self, data: dict) -> dict:
        """تشفير الحقول الحساسة في dict."""
        result = dict(data)
        for key in self.ENCRYPTED_FIELDS:
            if key in result and result[key]:
                result[key] = self.encrypt(str(result[key]))
        return result

    def decrypt_dict(self, data: dict, strict: bool = False) -> dict:
        """
        فك تشفير الحقول الحساسة في dict.

        Args:
            strict: إذا True، يرفع exception عند أول فشل.
                    إذا False (الافتراضي)، يتخطى الفاشلة بصمت.
        """
        result = dict(data)
        for key in self.ENCRYPTED_FIELDS:
            if key in result and result[key]:
                try:
                    result[key] = self.decrypt(
                        str(result[key]), strict=strict
                    )
                except ValueError:
                    if strict:
                        raise
                    # اترك القيمة كما هي (مشفّرة تالفة)
                    logger.warning(
                        f"⚠️ {key}: القيمة المشفّرة تالفة - "
                        f"تُركت كما هي"
                    )
        return result

    # ==================== الحالة ====================

    @property
    def is_available(self) -> bool:
        """هل التشفير متاح؟"""
        try:
            self._get_fernet()
            return True
        except Exception:
            return False

    @property
    def key_path(self) -> Path:
        return self._key_path


# مثيل عام
secrets_manager = SecretsManager()