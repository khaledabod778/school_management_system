"""
ApiClient - عميل HTTP للـ Local API.

يقوم بـ:
- إدارة الاتصال بـ Local API
- تخزين JWT token
- التعامل مع الأخطاء
- إعادة المحاولة التلقائية
"""

import logging
from pathlib import Path
import time
from typing import Optional, Dict, Any, Callable

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.api_client.exceptions import (
    ApiError, NetworkError, TimeoutError, AuthenticationError,
    PermissionError, NotFoundError, ValidationError, ServerError,
)
from app.api_client.token_store import TokenStore

logger = logging.getLogger(__name__)


class ApiClient:
    """
    عميل HTTP للـ Local API.

    الاستخدام:
        client = ApiClient("http://192.168.1.100:8000")
        result = client.login("admin", "password123")
        students = client.get("/api/students", params={"page": 1})
    """

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 2,
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._token: Optional[str] = None
        self._user_info: Optional[dict] = None
        self._token_store = TokenStore()

        # إعداد session مع retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[502, 503, 504],
            allowed_methods=["GET", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    # ==================== Properties ====================

    @property
    def is_authenticated(self) -> bool:
        return self._token is not None

    @property
    def current_user(self) -> Optional[dict]:
        return self._user_info

    @property
    def token(self) -> Optional[str]:
        return self._token

    # ==================== Auth ====================

    def login(self, username: str, password: str) -> dict:
        """
        تسجيل دخول.

        Returns:
            dict مع 'user' و 'access_token'
        """
        response = self._request(
            "POST",
            "/api/auth/login",
            json={"username": username, "password": password},
            authenticated=False,
        )

        # استخرج token
        self._token = response.get('access_token')
        self._user_info = response.get('user')

        if not self._token:
            raise ApiError("لم يُستَلم token من السيرفر")

        # احفظ token
        self._token_store.save(
            token=self._token,
            user_info=self._user_info or {},
            api_url=self.base_url,
        )

        logger.info(
            f"✅ تم تسجيل دخول: {username} "
            f"(role_id={self._user_info.get('role_id')})"
        )
        return response

    def logout(self):
        """تسجيل خروج."""
        self._token = None
        self._user_info = None
        self._token_store.clear()
        logger.info("🚪 تم تسجيل خروج")

    def try_auto_login(self) -> bool:
        """
        محاولة استرجاع session سابقة.

        Returns:
            True إذا وُجد token صالح
        """
        saved = self._token_store.load()
        if not saved:
            return False

        # تحقق من أن الـ URL نفسه
        if saved.get('api_url') != self.base_url:
            logger.debug("API URL مختلف - تجاهل token محفوظ")
            return False

        self._token = saved.get('token')
        self._user_info = saved.get('user_info', {})

        # اختبر token بطلب /me
        try:
            me = self.get("/api/auth/me")
            self._user_info = me
            logger.info(f"♻️ استرجاع جلسة: {self._user_info.get('username')}")
            return True
        except AuthenticationError:
            logger.debug("token محفوظ منتهي الصلاحية")
            self.logout()
            return False
        except Exception as e:
            logger.warning(f"فشل تحقق token: {e}")
            return False

    # ==================== HTTP Methods ====================
    
    def get(self, endpoint: str, params: Optional[dict] = None) -> Any:
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, json: Optional[dict] = None) -> Any:
        return self._request("POST", endpoint, json=json)

    def put(self, endpoint: str, json: Optional[dict] = None) -> Any:
        return self._request("PUT", endpoint, json=json)

    def patch(self, endpoint: str, json: Optional[dict] = None) -> Any:
        return self._request("PATCH", endpoint, json=json)

    def delete(self, endpoint: str) -> Any:
        return self._request("DELETE", endpoint)

    # ✅ جديد: multipart (لرفع الملفات)
    def post_multipart(
        self,
        endpoint: str,
        files: dict,
        data: Optional[dict] = None,
    ) -> Any:
        """POST multipart/form-data (لرفع الملفات)."""
        url = f"{self.base_url}{endpoint}"
        headers = {"Accept": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        try:
            response = self.session.post(
                url,
                files=files,
                data=data or {},
                headers=headers,
                timeout=self.timeout * 3,  # مهل أطول للملفات
            )
        except requests.exceptions.Timeout:
            raise TimeoutError("انتهت مهلة رفع الملف")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"فشل الاتصال: {e}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"خطأ في الشبكة: {e}")

        return self._handle_response(response, "POST", endpoint, False)

    # ✅ جديد: تنزيل ملف
    def download_file(self, endpoint: str, save_path: str) -> bool:
        """
        تنزيل ملف إلى مسار محلي.

        Returns:
            True إذا نجح التنزيل
        """
        url = f"{self.base_url}{endpoint}"
        headers = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        try:
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout * 3,
                stream=True,
            )
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"فشل التنزيل: {e}")

        if response.status_code != 200:
            raise ApiError(
                self._extract_error(response),
                response.status_code,
            )

        try:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception as e:
            raise ApiError(f"فشل حفظ الملف: {e}")

    # ==================== Core Request ====================

    def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
        authenticated: bool = True,
        _retry: bool = False,
    ) -> Any:
        """
        تنفيذ HTTP request مع معالجة شاملة للأخطاء.

        Args:
            authenticated: هل نُرسل Authorization header؟
            _retry: داخلي - لمنع الحلقات اللانهائية
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if authenticated and self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        # تسجيل
        log_msg = f"🌐 {method} {endpoint}"
        if json:
            log_msg += f" (payload keys: {list(json.keys())[:5]})"
        logger.debug(log_msg)

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(f"انتهت مهلة الاتصال بـ {url}")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"تعذّر الاتصال بـ {url}: {e}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"خطأ في الشبكة: {e}")

        # معالجة الاستجابة
        return self._handle_response(response, method, endpoint, _retry)

    def _handle_response(
        self,
        response: requests.Response,
        method: str,
        endpoint: str,
        _retry: bool,
    ) -> Any:
        """معالجة الاستجابة وأخطاء HTTP."""

        status = response.status_code

        # ✅ نجاح
        if 200 <= status < 300:
            if status == 204:  # No Content
                return None
            try:
                return response.json()
            except ValueError:
                return response.text

        # ==================== أخطاء ====================

        # استخرج رسالة الخطأ
        error_msg = self._extract_error(response)

        # 401 - فشل مصادقة
        if status == 401:
            # مسح token لأنه انتهى
            self._token = None
            self._token_store.clear()
            logger.warning(f"❌ 401 من {endpoint}: {error_msg}")
            raise AuthenticationError(error_msg)

        # 403 - صلاحيات
        if status == 403:
            logger.warning(f"❌ 403 من {endpoint}: {error_msg}")
            raise PermissionError(error_msg)

        # 404 - غير موجود
        if status == 404:
            logger.debug(f"❌ 404 من {endpoint}: {error_msg}")
            raise NotFoundError(error_msg)

        # 422 - بيانات
        if status == 422:
            logger.warning(f"❌ 422 من {endpoint}: {error_msg}")
            raise ValidationError(error_msg)

        # 5xx - خطأ سيرفر
        if status >= 500:
            logger.error(f"❌ {status} من {endpoint}: {error_msg}")
            raise ServerError(error_msg)

        # أي خطأ آخر
        logger.error(f"❌ HTTP {status} من {endpoint}: {error_msg}")
        raise ApiError(error_msg, status)

    @staticmethod
    def _extract_error(response: requests.Response) -> str:
        """استخراج رسالة خطأ من الاستجابة."""
        try:
            data = response.json()
            # FastAPI: {"detail": "..."}
            if isinstance(data, dict):
                if 'detail' in data:
                    detail = data['detail']
                    if isinstance(detail, list):
                        # أخطاء validation
                        return '; '.join(
                            str(d.get('msg', d)) for d in detail
                        )
                    return str(detail)
                if 'message' in data:
                    return str(data['message'])
                if 'error' in data:
                    return str(data['error'])
            return str(data)
        except ValueError:
            return response.text or f"HTTP {response.status_code}"

    # ==================== Health Check ====================

    def health_check(self) -> bool:
        """فحص الاتصال بالسيرفر."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/health",
                timeout=5,
            )
            return response.status_code == 200
        except Exception:
            return False


    def download_file_with_params(
        self,
        endpoint: str,
        save_path: str,
        params: Optional[dict] = None,
    ) -> bool:
        """تنزيل ملف مع query params."""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        try:
            response = self.session.get(
                url,
                headers=headers,
                params=params or {},
                timeout=self.timeout * 3,
                stream=True,
            )
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"فشل التنزيل: {e}")

        if response.status_code != 200:
            raise ApiError(
                self._extract_error(response),
                response.status_code,
            )

        try:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception as e:
            raise ApiError(f"فشل حفظ الملف: {e}")