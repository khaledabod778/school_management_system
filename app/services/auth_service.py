"""
خدمة المصادقة وإدارة المستخدمين.
"""

import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import User, Employee, Role
from app.core.exceptions import AuthenticationError, ValidationError, NotFoundError
from app.core.enums import UserStatus

logger = logging.getLogger(__name__)


class AuthService:
    """خدمة المصادقة وإدارة الجلسات."""
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple:
        """
        تشفير كلمة المرور باستخدام PBKDF2.
        
        Args:
            password: كلمة المرور
            salt: الملح (اختياري)
        
        Returns:
            (كلمة المرور المشفرة, الملح)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # استخدام PBKDF2 مع SHA256
        hash_value = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # عدد التكرارات
        ).hex()
        
        # تخزين الملح مع الهاش
        return f"{salt}${hash_value}", salt
    
    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """
        التحقق من كلمة المرور.
        
        Args:
            password: كلمة المرور المدخلة
            stored_hash: الهاش المخزن
        
        Returns:
            True إذا كانت كلمة المرور صحيحة
        """
        try:
            salt, original_hash = stored_hash.split('$')
            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            ).hex()
            return new_hash == original_hash
        except Exception:
            return False
    
    @staticmethod
    def authenticate(session: Session, username: str, password: str) -> Optional[User]:
        """
        المصادقة على المستخدم.
        
        Args:
            session: جلسة قاعدة البيانات
            username: اسم المستخدم
            password: كلمة المرور
        
        Returns:
            المستخدم إذا نجحت المصادقة
        
        Raises:
            AuthenticationError: عند فشل المصادقة
        """
        try:
            # البحث عن المستخدم
            user = session.execute(
                select(User).where(User.username == username)
            ).scalar_one_or_none()
            
            if not user:
                raise AuthenticationError("اسم المستخدم غير موجود")
            
            if user.status != UserStatus.ACTIVE.value:
                raise AuthenticationError("الحساب موقوف. يرجى التواصل مع المسؤول")
            
            if not AuthService.verify_password(password, user.password_hash):
                raise AuthenticationError("كلمة المرور غير صحيحة")
            
            # تحديث آخر تسجيل دخول
            user.last_login = datetime.now()
            session.commit()
            
            logger.info(f"تم تسجيل دخول المستخدم: {username}")
            return user
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"خطأ في المصادقة: {str(e)}")
            raise AuthenticationError("فشل المصادقة")
    
    @staticmethod
    def change_password(
        session: Session,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        تغيير كلمة المرور.
        
        Args:
            session: جلسة قاعدة البيانات
            user_id: معرف المستخدم
            old_password: كلمة المرور القديمة
            new_password: كلمة المرور الجديدة
        
        Returns:
            True إذا تم التغيير بنجاح
        """
        user = session.get(User, user_id)
        if not user:
            raise NotFoundError("المستخدم غير موجود")
        
        # التحقق من كلمة المرور القديمة
        if not AuthService.verify_password(old_password, user.password_hash):
            raise AuthenticationError("كلمة المرور القديمة غير صحيحة")
        
        # التحقق من قوة كلمة المرور الجديدة
        if len(new_password) < 8:
            raise ValidationError("كلمة المرور يجب أن تكون 8 أحرف على الأقل")
        
        # تحديث كلمة المرور
        user.password_hash, _ = AuthService.hash_password(new_password)
        user.last_password_change = datetime.now()
        session.commit()
        
        logger.info(f"تم تغيير كلمة المرور للمستخدم: {user_id}")
        return True
    
    @staticmethod
    def reset_password(session: Session, user_id: int, new_password: str = None) -> str:
        """
        إعادة ضبط كلمة المرور.
        
        Args:
            session: جلسة قاعدة البيانات
            user_id: معرف المستخدم
            new_password: كلمة المرور الجديدة (اختياري)
        
        Returns:
            كلمة المرور الجديدة
        """
        user = session.get(User, user_id)
        if not user:
            raise NotFoundError("المستخدم غير موجود")
        
        if new_password is None:
            new_password = secrets.token_urlsafe(8)
        
        user.password_hash, _ = AuthService.hash_password(new_password)
        user.last_password_change = datetime.now()
        session.commit()
        
        logger.info(f"تم إعادة ضبط كلمة المرور للمستخدم: {user_id}")
        return new_password
    
    @staticmethod
    def create_user(
        session: Session,
        username: str,
        password: str,
        role_id: int,
        employee_id: Optional[int] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> User:
        """
        إنشاء مستخدم جديد.
        
        Args:
            session: جلسة قاعدة البيانات
            username: اسم المستخدم
            password: كلمة المرور
            role_id: معرف الدور
            employee_id: معرف الموظف المرتبط
            phone: رقم الهاتف
            email: البريد الإلكتروني
        
        Returns:
            المستخدم الجديد
        """
        # التحقق من عدم وجود المستخدم
        existing = session.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()
        
        if existing:
            raise ValidationError("اسم المستخدم موجود مسبقاً")
        
        # تشفير كلمة المرور
        password_hash, _ = AuthService.hash_password(password)
        
        user = User(
            username=username,
            password_hash=password_hash,
            role_id=role_id,
            employee_id=employee_id,
            phone=phone,
            email=email,
            status=UserStatus.ACTIVE.value
        )
        
        session.add(user)
        session.commit()
        
        logger.info(f"تم إنشاء مستخدم جديد: {username}")
        return user
    
    @staticmethod
    def deactivate_user(session: Session, user_id: int) -> bool:
        """
        تعطيل مستخدم.
        
        Args:
            session: جلسة قاعدة البيانات
            user_id: معرف المستخدم
        
        Returns:
            True إذا تم التعطيل
        """
        user = session.get(User, user_id)
        if not user:
            raise NotFoundError("المستخدم غير موجود")
        
        user.status = UserStatus.SUSPENDED.value
        session.commit()
        
        logger.info(f"تم تعطيل المستخدم: {user_id}")
        return True
    
    @staticmethod
    def activate_user(session: Session, user_id: int) -> bool:
        """
        تفعيل مستخدم.
        
        Args:
            session: جلسة قاعدة البيانات
            user_id: معرف المستخدم
        
        Returns:
            True إذا تم التفعيل
        """
        user = session.get(User, user_id)
        if not user:
            raise NotFoundError("المستخدم غير موجود")
        
        user.status = UserStatus.ACTIVE.value
        session.commit()
        
        logger.info(f"تم تفعيل المستخدم: {user_id}")
        return True
    
    @staticmethod
    def get_user_permissions(session: Session, user_id: int) -> dict:
        """
        الحصول على صلاحيات المستخدم.
        
        Args:
            session: جلسة قاعدة البيانات
            user_id: معرف المستخدم
        
        Returns:
            قاموس بالصلاحيات
        """
        user = session.get(User, user_id)
        if not user or not user.role:
            return {}
        
        permissions = {}
        for role_permission in user.role.permissions:
            module = role_permission.permission.module_name
            permissions[module] = {
                'can_view': role_permission.can_view,
                'can_add': role_permission.can_add,
                'can_edit': role_permission.can_edit,
                'can_delete': role_permission.can_delete,
                'can_print': role_permission.can_print,
                'can_cancel': role_permission.can_cancel,
            }
        
        return permissions