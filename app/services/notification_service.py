"""
خدمة الإشعارات الداخلية.
"""

import logging
import threading
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy import select, func

from app.database.session import session_scope
from app.database.models import (
    Notification, NotificationLog, Parent, ParentDevice,
    Student, Grade, Section, User
)
from app.core.enums import NotificationType, NotificationTargetType

logger = logging.getLogger(__name__)


class NotificationService:
    """
    خدمة الإشعارات.
    تدير إنشاء وإرسال الإشعارات لأولياء الأمور.
    """
    
    def __init__(self, user: User):
        self.user = user
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def start(self):
        """بدء خدمة الإشعارات."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("تم بدء خدمة الإشعارات")
    
    def stop(self):
        """إيقاف خدمة الإشعارات."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("تم إيقاف خدمة الإشعارات")
    
    def _run(self):
        """الدالة الرئيسية للخدمة."""
        # معالجة الإشعارات المجدولة
        while self._running:
            self._process_scheduled_notifications()
            threading.Event().wait(30)
    
    def _process_scheduled_notifications(self):
        """معالجة الإشعارات المجدولة."""
        with session_scope() as session:
            # الحصول على الإشعارات المجدولة المستحقة
            scheduled = session.execute(
                select(Notification).where(
                    Notification.scheduled_at.isnot(None),
                    Notification.scheduled_at <= datetime.now(),
                    Notification.sent_at.is_(None),
                    Notification.is_active == True
                )
            ).scalars().all()
            
            for notification in scheduled:
                self.send_notification(notification)
    
    def create_notification(
        self,
        title: str,
        message: str,
        notification_type: str,
        target_type: str = 'all',
        target_grade_id: Optional[int] = None,
        target_section_id: Optional[int] = None,
        scheduled_at: Optional[datetime] = None,
        parent_ids: Optional[List[int]] = None
    ) -> Notification:
        """
        إنشاء إشعار جديد.
        
        Args:
            title: عنوان الإشعار
            message: نص الإشعار
            notification_type: نوع الإشعار
            target_type: نوع الهدف
            target_grade_id: معرف الصف المستهدف
            target_section_id: معرف الشعبة المستهدفة
            scheduled_at: وقت الإرسال المجدول
            parent_ids: قائمة معرفات أولياء الأمور
        
        Returns:
            الإشعار المنشأ
        """
        with session_scope() as session:
            notification = Notification(
                title=title,
                message=message,
                notification_type=notification_type,
                sender_user_id=self.user.id,
                target_type=target_type,
                target_grade_id=target_grade_id,
                target_section_id=target_section_id,
                scheduled_at=scheduled_at,
                is_active=True
            )
            session.add(notification)
            session.flush()
            
            # إذا كان الإرسال فوري، أرسل الآن
            if not scheduled_at:
                self._send_to_parents(session, notification, parent_ids)
                notification.sent_at = datetime.now()
            
            session.commit()
            logger.info(f"تم إنشاء إشعار: {title}")
            return notification
    
    def _send_to_parents(self, session, notification: Notification, 
                         parent_ids: Optional[List[int]] = None):
        """إرسال الإشعار لأولياء الأمور."""
        # تحديد أولياء الأمور المستهدفين
        parents = self._get_target_parents(session, notification, parent_ids)
        
        for parent in parents:
            log = NotificationLog(
                notification_id=notification.id,
                parent_id=parent.id,
                sent_at=datetime.now(),
                delivery_status='sent'
            )
            session.add(log)
    
    def _get_target_parents(self, session, notification: Notification,
                            parent_ids: Optional[List[int]] = None) -> List[Parent]:
        """الحصول على أولياء الأمور المستهدفين."""
        if parent_ids:
            # إرسال لأولياء أمور محددين
            return session.execute(
                select(Parent).where(Parent.id.in_(parent_ids))
            ).scalars().all()
        
        # حسب نوع الهدف
        if notification.target_type == 'all':
            return session.execute(select(Parent)).scalars().all()
        
        elif notification.target_type == 'grade':
            if notification.target_grade_id:
                students = session.execute(
                    select(Student).where(Student.grade_id == notification.target_grade_id)
                ).scalars().all()
                parent_ids = [s.parent_id for s in students if s.parent_id]
                return session.execute(
                    select(Parent).where(Parent.id.in_(parent_ids))
                ).scalars().all()
        
        elif notification.target_type == 'section':
            if notification.target_section_id:
                students = session.execute(
                    select(Student).where(Student.section_id == notification.target_section_id)
                ).scalars().all()
                parent_ids = [s.parent_id for s in students if s.parent_id]
                return session.execute(
                    select(Parent).where(Parent.id.in_(parent_ids))
                ).scalars().all()
        
        return []
    
    def send_notification(self, notification: Notification):
        """إرسال إشعار موجود."""
        with session_scope() as session:
            self._send_to_parents(session, notification)
            notification.sent_at = datetime.now()
            session.commit()
    
    def mark_as_read(self, notification_log_id: int):
        """تحديد إشعار كمقروء."""
        with session_scope() as session:
            log = session.get(NotificationLog, notification_log_id)
            if log:
                log.delivery_status = 'read'
                log.read_at = datetime.now()
                session.commit()
    
    def get_unread_notifications(self, parent_id: int) -> List[NotificationLog]:
        """الحصول على الإشعارات غير المقروءة."""
        with session_scope() as session:
            return session.execute(
                select(NotificationLog)
                .join(Notification, NotificationLog.notification_id == Notification.id)
                .where(
                    NotificationLog.parent_id == parent_id,
                    NotificationLog.delivery_status != 'read'
                )
                .order_by(Notification.created_at.desc())
            ).scalars().all()
    
    def get_all_notifications(self, limit: int = 100) -> List[Notification]:
        """الحصول على جميع الإشعارات."""
        with session_scope() as session:
            return session.execute(
                select(Notification)
                .order_by(Notification.created_at.desc())
                .limit(limit)
            ).scalars().all()
    
    def cancel_notification(self, notification_id: int):
        """إلغاء إشعار."""
        with session_scope() as session:
            notification = session.get(Notification, notification_id)
            if notification:
                notification.is_active = False
                session.commit()
    
    def delete_notification(self, notification_id: int):
        """حذف إشعار."""
        with session_scope() as session:
            notification = session.get(Notification, notification_id)
            if notification:
                session.delete(notification)
                session.commit()
    
    def get_notification_stats(self) -> Dict:
        """الحصول على إحصائيات الإشعارات."""
        with session_scope() as session:
            total = session.execute(
                select(func.count(Notification.id))
            ).scalar()
            
            sent = session.execute(
                select(func.count(Notification.id)).where(
                    Notification.sent_at.isnot(None)
                )
            ).scalar()
            
            read = session.execute(
                select(func.count(NotificationLog.id)).where(
                    NotificationLog.delivery_status == 'read'
                )
            ).scalar()
            
            return {
                'total': total,
                'sent': sent,
                'read': read,
                'unread': sent - read
            }
    
    # دوال مساعدة لإنشاء إشعارات محددة
    
    def notify_attendance(self, student: Student, status: str, date):
        """إشعار بالحضور/الغياب."""
        title = f"{'حضور' if status == 'حاضر' else 'غياب'} - {student.full_name}"
        message = f"تم تسجيل {'حضور' if status == 'حاضر' else 'غياب'} للطالب {student.full_name} بتاريخ {date}"
        
        self.create_notification(
            title=title,
            message=message,
            notification_type=NotificationType.ATTENDANCE.value if status == 'حاضر' else NotificationType.ABSENCE.value,
            target_type='parent',
            parent_ids=[student.parent_id] if student.parent_id else None
        )
    
    def notify_homework(self, student: Student, homework_title: str):
        """إشعار بالواجب."""
        self.create_notification(
            title=f"واجب جديد - {homework_title}",
            message=f"تم إضافة واجب جديد: {homework_title}",
            notification_type=NotificationType.HOMEWORK.value,
            target_type='parent',
            parent_ids=[student.parent_id] if student.parent_id else None
        )
    
    def notify_behavior(self, student: Student, behavior_type: str, title: str):
        """إشعار بالسلوك."""
        self.create_notification(
            title=f"{behavior_type} - {title}",
            message=f"تم تسجيل {behavior_type} للطالب {student.full_name}: {title}",
            notification_type=NotificationType.BEHAVIOR.value,
            target_type='parent',
            parent_ids=[student.parent_id] if student.parent_id else None
        )
    
    def notify_grades(self, student: Student, term: int):
        """إشعار بالنتائج."""
        self.create_notification(
            title=f"نتائج الفصل {term} - {student.full_name}",
            message=f"تم رصد نتائج الفصل {term} للطالب {student.full_name}",
            notification_type=NotificationType.RESULTS.value,
            target_type='parent',
            parent_ids=[student.parent_id] if student.parent_id else None
        )
    
    def notify_fees(self, student: Student, amount, due_date):
        """إشعار بالرسوم."""
        self.create_notification(
            title=f"استحقاق رسوم - {student.full_name}",
            message=f"يستحق مبلغ {amount} للطالب {student.full_name} بتاريخ {due_date}",
            notification_type=NotificationType.FEES.value,
            target_type='parent',
            parent_ids=[student.parent_id] if student.parent_id else None
        )