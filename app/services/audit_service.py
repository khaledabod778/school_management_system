"""
خدمة التدقيق وتسجيل العمليات.
"""

import json
import logging
import socket
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import event
from sqlalchemy.orm import Session

from app.database.models import SystemAuditLog, User

logger = logging.getLogger(__name__)


class AuditService:
    """خدمة تسجيل وتتبع العمليات."""
    
    _current_user_id: Optional[int] = None
    
    @classmethod
    def set_current_user(cls, user_id: Optional[int]):
        """تعيين المستخدم الحالي."""
        cls._current_user_id = user_id
    
    @classmethod
    def get_current_user_id(cls) -> Optional[int]:
        """الحصول على المستخدم الحالي."""
        return cls._current_user_id
    
    @staticmethod
    def log_operation(
        session: Session,
        user_id: Optional[int],
        module_name: str,
        operation_type: str,
        record_id: Optional[int] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        device_name: Optional[str] = None
    ) -> Optional[SystemAuditLog]:
        """
        تسجيل عملية في سجل التدقيق.
        لا تستخدم flush هنا - فقط add.
        """
        try:
            ip_address = AuditService._get_ip_address()
            
            old_values_json = json.dumps(old_values, ensure_ascii=False, default=str) if old_values else None
            new_values_json = json.dumps(new_values, ensure_ascii=False, default=str) if new_values else None
            
            audit_log = SystemAuditLog(
                user_id=user_id,
                module_name=module_name,
                operation_type=operation_type,
                record_id=record_id,
                old_values=old_values_json,
                new_values=new_values_json,
                ip_address=ip_address,
                device_name=device_name or socket.gethostname()
            )
            
            session.add(audit_log)
            # لا تستخدم flush هنا - سيتم الحفظ مع commit
            
            return audit_log
            
        except Exception as e:
            logger.error(f"فشل تسجيل العملية: {str(e)}")
            return None
    
    @staticmethod
    def log_create(session: Session, user_id: int, module_name: str, 
                   record_id: int, new_values: dict):
        """تسجيل عملية إضافة."""
        return AuditService.log_operation(
            session, user_id, module_name, "create",
            record_id=record_id, new_values=new_values
        )
    
    @staticmethod
    def log_update(session: Session, user_id: int, module_name: str, 
                   record_id: int, old_values: dict, new_values: dict):
        """تسجيل عملية تعديل."""
        return AuditService.log_operation(
            session, user_id, module_name, "update",
            record_id=record_id, old_values=old_values, new_values=new_values
        )
    
    @staticmethod
    def log_delete(session: Session, user_id: int, module_name: str, 
                   record_id: int, old_values: dict):
        """تسجيل عملية حذف."""
        return AuditService.log_operation(
            session, user_id, "حذف", "delete",
            record_id=record_id, old_values=old_values
        )
    
    @staticmethod
    def log_login(session: Session, user_id: int, device_name: str = None):
        """تسجيل عملية تسجيل دخول."""
        return AuditService.log_operation(
            session, user_id, "تسجيل الدخول", "login", device_name=device_name
        )
    
    @staticmethod
    def log_logout(session: Session, user_id: int, device_name: str = None):
        """تسجيل عملية تسجيل خروج."""
        return AuditService.log_operation(
            session, user_id, "تسجيل الخروج", "logout", device_name=device_name
        )
    
    @staticmethod
    def log_cancel(session: Session, user_id: int, module_name: str, 
                   record_id: int, reason: str):
        """تسجيل عملية إلغاء."""
        return AuditService.log_operation(
            session, user_id, module_name, "cancel",
            record_id=record_id, new_values={"reason": reason}
        )
    
    @staticmethod
    def _get_ip_address() -> str:
        """الحصول على عنوان IP."""
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception:
            return "127.0.0.1"


# إعداد مستمعين للأحداث - بدون flush
def setup_audit_listeners():
    """إعداد مستمعين لأحداث SQLAlchemy للتسجيل التلقائي."""
    
    @event.listens_for(Session, "after_flush")
    def receive_after_flush(session, flush_context):
        """بعد حفظ التغييرات."""
        user_id = AuditService.get_current_user_id()
        if not user_id:
            return
        
        # استخدام after_flush_postexec بدلاً من after_flush لتجنب التكرار
        for obj in session.new:
            if hasattr(obj, '__tablename__') and obj.__tablename__ != 'system_audit_logs':
                try:
                    new_values = {}
                    for c in obj.__table__.columns:
                        try:
                            new_values[c.name] = str(getattr(obj, c.name))
                        except:
                            new_values[c.name] = None
                    
                    audit_log = SystemAuditLog(
                        user_id=user_id,
                        module_name=obj.__tablename__,
                        operation_type="create",
                        record_id=getattr(obj, 'id', None),
                        new_values=json.dumps(new_values, ensure_ascii=False, default=str),
                        ip_address=AuditService._get_ip_address(),
                        device_name=socket.gethostname()
                    )
                    session.add(audit_log)
                except Exception as e:
                    logger.debug(f"تخطي تسجيل: {str(e)}")
        
        for obj in session.deleted:
            if hasattr(obj, '__tablename__') and obj.__tablename__ != 'system_audit_logs':
                try:
                    old_values = {}
                    for c in obj.__table__.columns:
                        try:
                            old_values[c.name] = str(getattr(obj, c.name))
                        except:
                            old_values[c.name] = None
                    
                    audit_log = SystemAuditLog(
                        user_id=user_id,
                        module_name=obj.__tablename__,
                        operation_type="delete",
                        record_id=getattr(obj, 'id', None),
                        old_values=json.dumps(old_values, ensure_ascii=False, default=str),
                        ip_address=AuditService._get_ip_address(),
                        device_name=socket.gethostname()
                    )
                    session.add(audit_log)
                except Exception as e:
                    logger.debug(f"تخطي تسجيل: {str(e)}")