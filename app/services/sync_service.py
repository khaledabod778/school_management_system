"""
خدمة المزامنة الخلفية - Offline-First Sync Engine.
"""

import logging
import threading
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum

import requests
from sqlalchemy import select, func, text
from sqlalchemy.orm import Session

from app.core.config import config_manager
from app.core.exceptions import SyncError
from app.database.session import session_scope
from app.database.models import (
    Base, User, Student, Receipt, ExpenseVoucher,
    DailyAttendance, MonthlyEvaluation, Notification,
    NotificationLog, SystemAuditLog
)

logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """حالات المزامنة."""
    IDLE = "idle"
    SYNCING = "syncing"
    SUCCESS = "success"
    FAILED = "failed"
    OFFLINE = "offline"


class SyncOperation(Enum):
    """أنواع عمليات المزامنة."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class SyncService:
    """
    خدمة المزامنة التلقائية.
    تعمل في الخلفية وتزامن البيانات مع الخادم السحابي.
    """
    
    def __init__(self, user: User):
        self.user = user
        self.status = SyncStatus.IDLE
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_sync: Optional[datetime] = None
        self._pending_operations: List[Dict] = []
        self._conflicts: List[Dict] = []
        
        # إعدادات المزامنة
        self.sync_interval = config_manager.app_config.sync_interval
        self.max_retries = 3
        self.timeout = 30
        
    def start(self):
        """بدء خدمة المزامنة."""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("تم بدء خدمة المزامنة")
    
    def stop(self):
        """إيقاف خدمة المزامنة."""
        self._running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("تم إيقاف خدمة المزامنة")
    
    def _run(self):
        """الدالة الرئيسية للمزامنة."""
        while not self._stop_event.is_set():
            try:
                # فحص الاتصال بالخادم
                if self._check_cloud_connection():
                    self.status = SyncStatus.SYNCING
                    self._sync_all()
                    self.status = SyncStatus.SUCCESS
                    self._last_sync = datetime.now()
                else:
                    self.status = SyncStatus.OFFLINE
                    logger.info("لا يوجد اتصال بالخادم السحابي - سيتم المحاولة لاحقاً")
            except Exception as e:
                self.status = SyncStatus.FAILED
                logger.error(f"خطأ في المزامنة: {str(e)}")
            
            # انتظار الفترة المحددة
            self._stop_event.wait(self.sync_interval)
    
    def _check_cloud_connection(self) -> bool:
        """فحص الاتصال بالخادم السحابي."""
        try:
            # محاولة الاتصال بالخادم
            response = requests.get(
                f"{self._get_cloud_url()}/health",
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def _get_cloud_url(self) -> str:
        """الحصول على عنوان الخادم السحابي."""
        # يمكن تعديل هذا حسب إعدادات الخادم
        return "https://api.school-erp.com"
    
    def _sync_all(self):
        """مزامنة جميع البيانات."""
        logger.info("بدء مزامنة جميع البيانات...")
        
        # 1. مزامنة العمليات المعلقة
        self._sync_pending_operations()
        
        # 2. مزامنة البيانات الجديدة
        self._sync_new_data()
        
        # 3. مزامنة الإشعارات
        self._sync_notifications()
        
        # 4. معالجة التعارضات
        self._resolve_conflicts()
        
        logger.info("اكتملت المزامنة بنجاح")
    
    def _sync_pending_operations(self):
        """مزامنة العمليات المعلقة."""
        with session_scope() as session:
            # الحصول على العمليات المعلقة
            pending = session.execute(
                text("""
                    SELECT * FROM sync_operations 
                    WHERE status = 'pending' 
                    ORDER BY created_at ASC
                    LIMIT 100
                """)
            ).fetchall()
            
            for operation in pending:
                try:
                    # إرسال العملية إلى الخادم
                    self._send_operation_to_cloud(operation)
                    
                    # تحديث حالة العملية
                    session.execute(
                        text("""
                            UPDATE sync_operations 
                            SET status = 'synced', synced_at = NOW() 
                            WHERE id = :id
                        """),
                        {"id": operation.id}
                    )
                    
                except Exception as e:
                    logger.error(f"فشل مزامنة العملية {operation.id}: {str(e)}")
                    # تحديث عدد المحاولات
                    session.execute(
                        text("""
                            UPDATE sync_operations 
                            SET retry_count = retry_count + 1,
                                status = CASE WHEN retry_count >= :max_retries 
                                    THEN 'failed' ELSE 'pending' END
                            WHERE id = :id
                        """),
                        {"id": operation.id, "max_retries": self.max_retries}
                    )
            
            session.commit()
    
    def _send_operation_to_cloud(self, operation):
        """إرسال عملية إلى الخادم."""
        payload = {
            'operation_id': operation.id,
            'entity_type': operation.entity_type,
            'entity_id': operation.entity_id,
            'operation_type': operation.operation_type,
            'data': json.loads(operation.data_json),
            'created_at': operation.created_at.isoformat(),
            'user_id': self.user.id
        }
        
        response = requests.post(
            f"{self._get_cloud_url()}/api/sync/operations",
            json=payload,
            timeout=self.timeout,
            headers=self._get_auth_headers()
        )
        
        if response.status_code != 200:
            raise SyncError(f"فشل إرسال العملية: {response.status_code}")
    
    def _sync_new_data(self):
        """مزامنة البيانات الجديدة من الخادم."""
        try:
            # الحصول على آخر مزامنة
            last_sync_time = self._last_sync or datetime.now() - timedelta(days=1)
            
            response = requests.get(
                f"{self._get_cloud_url()}/api/sync/data",
                params={'since': last_sync_time.isoformat()},
                timeout=self.timeout,
                headers=self._get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self._apply_cloud_data(data)
        except Exception as e:
            logger.error(f"فشل مزامنة البيانات الجديدة: {str(e)}")
    
    def _apply_cloud_data(self, data: Dict):
        """تطبيق البيانات من الخادم."""
        with session_scope() as session:
            # تطبيق كل نوع من البيانات
            if 'students' in data:
                self._apply_students(session, data['students'])
            
            if 'receipts' in data:
                self._apply_receipts(session, data['receipts'])
            
            if 'attendance' in data:
                self._apply_attendance(session, data['attendance'])
            
            if 'notifications' in data:
                self._apply_notifications(session, data['notifications'])
    
    def _apply_students(self, session: Session, students: List[Dict]):
        """تطبيق بيانات الطلاب."""
        for student_data in students:
            student = session.get(Student, student_data['id'])
            
            if student:
                # تحديث الطالب الموجود
                for key, value in student_data.items():
                    if hasattr(student, key) and key not in ['id', 'created_at']:
                        setattr(student, key, value)
            else:
                # إنشاء طالب جديد
                student = Student(**student_data)
                session.add(student)
    
    def _apply_receipts(self, session: Session, receipts: List[Dict]):
        """تطبيق بيانات السندات."""
        for receipt_data in receipts:
            receipt = session.get(Receipt, receipt_data['id'])
            
            if receipt:
                # تحديث السند الموجود
                for key, value in receipt_data.items():
                    if hasattr(receipt, key) and key not in ['id', 'created_at']:
                        setattr(receipt, key, value)
            else:
                # إنشاء سند جديد
                receipt = Receipt(**receipt_data)
                session.add(receipt)
    
    def _apply_attendance(self, session: Session, attendance_data: List[Dict]):
        """تطبيق بيانات الحضور."""
        for att_data in attendance_data:
            attendance = session.get(DailyAttendance, att_data['id'])
            
            if attendance:
                for key, value in att_data.items():
                    if hasattr(attendance, key) and key not in ['id', 'created_at']:
                        setattr(attendance, key, value)
            else:
                attendance = DailyAttendance(**att_data)
                session.add(attendance)
    
    def _apply_notifications(self, session: Session, notifications: List[Dict]):
        """تطبيق بيانات الإشعارات."""
        for notif_data in notifications:
            notification = session.get(Notification, notif_data['id'])
            
            if notification:
                for key, value in notif_data.items():
                    if hasattr(notification, key) and key not in ['id', 'created_at']:
                        setattr(notification, key, value)
            else:
                notification = Notification(**notif_data)
                session.add(notification)
    
    def _sync_notifications(self):
        """مزامنة الإشعارات."""
        with session_scope() as session:
            # الحصول على الإشعارات غير المرسلة
            pending_notifications = session.execute(
                select(Notification).where(
                    Notification.sent_at.is_(None),
                    Notification.is_active == True
                )
            ).scalars().all()
            
            for notification in pending_notifications:
                try:
                    # إرسال الإشعار إلى الخادم
                    self._send_notification_to_cloud(notification)
                    
                    # تحديث حالة الإشعار
                    notification.sent_at = datetime.now()
                    
                except Exception as e:
                    logger.error(f"فشل إرسال الإشعار {notification.id}: {str(e)}")
            
            session.commit()
    
    def _send_notification_to_cloud(self, notification: Notification):
        """إرسال إشعار إلى الخادم."""
        payload = {
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'notification_type': notification.notification_type,
            'target_type': notification.target_type,
            'created_at': notification.created_at.isoformat()
        }
        
        response = requests.post(
            f"{self._get_cloud_url()}/api/notifications",
            json=payload,
            timeout=self.timeout,
            headers=self._get_auth_headers()
        )
        
        if response.status_code != 200:
            raise SyncError(f"فشل إرسال الإشعار: {response.status_code}")
    
    def _resolve_conflicts(self):
        """معالجة تعارضات البيانات."""
        # استراتيجية: Last-Write-Wins
        # يمكن تعديلها حسب الحاجة
        pass
    
    def _get_auth_headers(self) -> Dict:
        """الحصول على رؤوس المصادقة."""
        return {
            'Authorization': f'Bearer {self._get_token()}',
            'Content-Type': 'application/json'
        }
    
    def _get_token(self) -> str:
        """الحصول على رمز المصادقة."""
        # يمكن تخزين الرمز في مكان آمن
        return "dummy_token"
    
    def add_pending_operation(self, entity_type: str, entity_id: int, 
                               operation_type: str, data: Dict):
        """إضافة عملية معلقة للمزامنة."""
        with session_scope() as session:
            session.execute(
                text("""
                    INSERT INTO sync_operations 
                    (entity_type, entity_id, operation_type, data_json, status, user_id)
                    VALUES (:entity_type, :entity_id, :operation_type, :data_json, 'pending', :user_id)
                """),
                {
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'operation_type': operation_type,
                    'data_json': json.dumps(data, ensure_ascii=False),
                    'user_id': self.user.id
                }
            )
            session.commit()
        
        logger.info(f"تمت إضافة عملية معلقة: {entity_type} - {operation_type}")
    
    def get_status(self) -> SyncStatus:
        """الحصول على حالة المزامنة."""
        return self.status
    
    def get_last_sync_time(self) -> Optional[datetime]:
        """الحصول على وقت آخر مزامنة."""
        return self._last_sync
    
    def force_sync(self):
        """فرض المزامنة فوراً."""
        if self._running:
            self._sync_all()