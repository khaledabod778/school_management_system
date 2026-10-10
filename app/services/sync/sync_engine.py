"""
محرك المزامنة الرئيسي - يتعامل مع Push و Pull.
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple

from sqlalchemy import select, func, text
from sqlalchemy.orm import Session

from app.core.config import config_manager
from app.database.session import session_scope
from app.database.models.sync import (
    SyncConflict, SyncMetadata, SyncInstance, SyncQueue
)
from app.services.sync.sync_queue_manager import SyncQueueManager
from app.services.sync.conflict_resolver import ConflictResolver

logger = logging.getLogger(__name__)


class SyncEngine:
    """
    محرك المزامنة الرئيسي.
    
    يتعامل مع:
    1. Push: إرسال التغييرات المحلية إلى السحابة
    2. Pull: سحب التغييرات من السحابة إلى المحلي
    3. Conflict Resolution
    """
    
    # مفتاح التتبع في metadata
    KEY_LAST_PUSH = "sync_last_push_at"
    KEY_LAST_PULL = "sync_last_pull_at"
    KEY_INSTANCE_ID = "sync_instance_id"
    
    def __init__(self):
        self.cloud_api_url = self._get_cloud_api_url()
        # self.instance_id = self._get_or_create_instance_id()
        self.timeout = 30
        self.session = requests.Session()
        # مفتاح cursor
        self.KEY_LAST_CURSOR = "sync_last_cursor"

        # ✅ لا نقرأ instance_id الآن - فقط نخزّنه كـ None
        self._instance_id: Optional[str] = None
    
    def _get_cloud_api_url(self) -> str:
        """الحصول على عنوان Cloud API."""
        config = config_manager.database_config
        # يمكن تخزينه في config.json
        cloud_api = getattr(config, 'cloud_api_url', None)
        if not cloud_api:
            # بناء من معلومات المضيف
            return "https://api.school-erp.com"  # افتراضي
        return cloud_api
        
    @property
    def instance_id(self) -> str:
        """
        ✅ الحصول على instance_id من ChangeTracker (المصدر الوحيد).

        هذا يمنع اختلاف المعرفات بين الطبقات.
        """
        if self._instance_id is None:
            from app.services.sync.change_tracker import ChangeTracker
            self._instance_id = ChangeTracker.get_instance_id()
        return self._instance_id
    
    def _get_or_create_instance_id(self) -> str:
        """إنشاء/قراءة سجل النسخة في DB (لا يُنشئ معرفاً جديداً)."""
        import socket
        import re
        import hashlib
        from app.database.session import session_scope
        from app.database.connection import db_manager
        from sqlalchemy import select as sa_select

        def _sanitize_hostname(hostname: str) -> str:
            ascii_name = re.sub(r'[^a-zA-Z0-9\-_]', '', hostname)
            if not ascii_name:
                ascii_name = hashlib.md5(
                    hostname.encode('utf-8')
                ).hexdigest()[:8]
            return ascii_name

        try:
            if not db_manager._is_initialized:
                logger.warning("DB غير مهيأة")
                return self._instance_id or "temp-unknown"

            with session_scope() as session:
                # ✅ اقرأ المعرف الموحّد من ChangeTracker
                from app.services.sync.change_tracker import ChangeTracker
                instance_id = ChangeTracker.get_instance_id()

                # تأكد من وجود سجل في sync_instances
                existing = session.execute(
                    sa_select(SyncInstance).where(
                        SyncInstance.instance_id == instance_id
                    )
                ).scalar_one_or_none()

                if not existing:
                    hostname = socket.gethostname()
                    safe_hostname = _sanitize_hostname(hostname)
                    instance = SyncInstance(
                        instance_id=instance_id,
                        instance_name=safe_hostname or "unknown",
                        instance_type='local',
                        hostname=safe_hostname,
                        is_active=True,
                        last_seen_at=datetime.now(),
                    )
                    session.add(instance)

                return instance_id

        except Exception as e:
            logger.warning(f"تعذر قراءة instance_id: {e}")
            from app.services.sync.change_tracker import ChangeTracker
            return ChangeTracker.get_instance_id()
           
    # ==================== الصحة والاتصال ====================
    
    def check_cloud_health(self) -> bool:
        """التحقق من صحة Cloud API."""

        if not self.cloud_api_url or not isinstance(self.cloud_api_url, str):
            logger.warning(f"cloud_api_url غير صالح: {self.cloud_api_url}")
            return False
        try:
            response = self.session.get(
                f"{self.cloud_api_url}/api/sync/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Cloud API غير متاح: {str(e)}")
            return False
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """رؤوس المصادقة (ASCII آمن)."""
        import hashlib
        
        def _ascii_safe(value: str) -> str:
            """جعل القيمة ASCII آمنة."""
            if not value:
                return ''
            try:
                value.encode('ascii')
                return value
            except UnicodeEncodeError:
                return hashlib.md5(value.encode('utf-8')).hexdigest()
        
        api_key = getattr(
            config_manager.database_config, 'cloud_api_key', ''
        ) or ''
        
        return {
            'X-Instance-ID': _ascii_safe(self.instance_id),
            'X-API-Key': _ascii_safe(api_key),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    # ✅ أضف هنا 👇
    def _compress_payload(self, data: dict) -> tuple:
        """
        ✅ v2.0: ضغط payload إذا كان أكبر من حد معيّن.
        
        Returns:
            (bytes, is_compressed)
        """
        import gzip
        import json

        if not config_manager.app_config.compression_enabled:
            return json.dumps(data).encode('utf-8'), False

        raw = json.dumps(data, ensure_ascii=False).encode('utf-8')

        # اضغط فقط إذا > 1 KB
        if len(raw) < 1024:
            return raw, False

        compressed = gzip.compress(raw, compresslevel=6)

        # استخدم المضغوط فقط إذا وفّر > 20%
        if len(compressed) < len(raw) * 0.8:
            return compressed, True

        return raw, False
    # ✅ نهاية الإضافة
    
    # ==================== PUSH: من المحلي إلى السحابة ====================
    
    def push_to_cloud(self, batch_size: int = 50) -> Dict[str, int]:
        """إرسال التغييرات المحلية إلى السحابة (مع ترتيب التبعيات)."""
        import hashlib
        
        stats = {'pushed': 0, 'failed': 0, 'conflicts': 0}
        
        if not self.check_cloud_health():
            logger.warning("Cloud غير متاح - تخطي Push")
            return stats
        
        # ✅ ترتيب الجداول حسب التبعيات
        # كل جدول يُرسل بعد جداوله المعتمدة
        TABLE_DEPENDENCY_ORDER = {
            # المستوى 0: لا يعتمد على شيء
            'roles': 0,
            'school_info': 0,
            'academic_years': 0,
            'fee_types': 0,
            'subjects': 0,
            
            # المستوى 1: يعتمد على المستوى 0
            'grades': 1,
            'employees': 1,
            
            # المستوى 2
            'sections': 2,
            'users': 2,
            'parents': 2,
            'grade_fee_structures': 2,
            
            # المستوى 3
            'students': 3,
            'teacher_subject_sections': 3,
            'student_fees': 3,
            
            # المستوى 4
            'fee_installments': 4,
            'receipts': 4,
            'parent_devices': 4,
            'student_documents': 4,
            'homeworks': 4,
            'daily_attendance': 4,
            'monthly_evaluations': 4,
            'term_exam_scores': 4,
            'behavioral_records': 4,
            'notifications': 4,
            
            # المستوى 5
            'notification_logs': 5,
            'payroll_records': 5,
            'employee_loans': 5,
            'employee_allowances_deductions': 5,
            'expense_vouchers': 5,
            'weekly_schedules': 5,
            'monthly_exam_schedules': 5,
            'final_exam_schedules': 5,
            'student_academic_history': 5,
            'annual_closing_logs': 5,
            'print_archive': 5,
            'import_export_logs': 5,
            'backup_logs': 5,
            'system_audit_logs': 5,
        }
        
        def _sort_by_dependency(items):
            """
            ✅ v3: ترتيب ذكي حسب التبعيات.
            
            - يعتمد على TABLE_DEPENDENCY_ORDER
            - لكن INSERT يأتي قبل UPDATE لنفس الجدول
            - DELETE يأتي أخيراً
            """
            # ترتيب العمليات حسب العملية
            OP_PRIORITY = {
                'INSERT': 0,
                'UPDATE': 1,
                'DELETE': 2,
            }

            return sorted(
                items,
                key=lambda item: (
                    # 1. حسب الجدول أولاً
                    TABLE_DEPENDENCY_ORDER.get(item.entity_type, 99),
                    # 2. ثم حسب العملية (INSERT قبل UPDATE قبل DELETE)
                    OP_PRIORITY.get(item.operation, 1),
                    # 3. ثم حسب ID
                    item.id
                )
            )
        
        def _generate_idempotency_key(item) -> str:
            content = (
                f"{item.entity_type}:"
                f"{item.entity_uuid}:"
                f"{item.operation}:"
                f"{item.created_at.isoformat() if item.created_at else 'unknown'}"
            )
            return hashlib.sha256(content.encode('utf-8')).hexdigest()[:64]
        
        try:
            with session_scope() as session:
                pending = SyncQueueManager.get_pending_operations(
                    session, direction='to_cloud', limit=batch_size
                )
                
                if not pending:
                    logger.debug("لا توجد عمليات للمزامنة")
                    return stats

                # ✅ 1. حل التبعيات (يُضيف عمليات جديدة للـ session)
                deps_added = 0
                for item in pending:
                    before = len(session.new)
                    self._resolve_dependencies(session, item)
                    after = len(session.new)
                    if after > before:
                        deps_added += (after - before)

                # ✅ 2. flush لتثبيت التبعيات الجديدة
                if deps_added > 0:
                    session.flush()
                    logger.info(
                        f"➕ أُضيفت {deps_added} تبعية جديدة - "
                        f"سيُعاد جلب الطابور"
                    )

                    # ✅ 3. أعِد جلب الطابور (ليشمل التبعيات الجديدة)
                    pending = SyncQueueManager.get_pending_operations(
                        session, direction='to_cloud', limit=batch_size
                    )

                # ✅ 4. رتّب حسب التبعيات
                pending_sorted = _sort_by_dependency(pending)
                
                logger.info(
                    f"إرسال {len(pending_sorted)} عملية (مرتبة حسب التبعيات):"
                )
                for item in pending_sorted:
                    logger.debug(
                        f"  [{TABLE_DEPENDENCY_ORDER.get(item.entity_type, 99)}] "
                        f"{item.operation} {item.entity_type}"
                    )
                
                # تجهيز الدفعة
                batch_data = []
                for item in pending_sorted:
                    batch_data.append({
                        'idempotency_key': _generate_idempotency_key(item),
                        'entity_type': item.entity_type,
                        'entity_uuid': item.entity_uuid,
                        'operation_type': item.operation,
                        'payload': item.payload,
                        'local_updated_at': (
                            item.created_at.isoformat()
                            if item.created_at else None
                        ),
                        'sync_version': item.sync_version or 1,
                    })
                
                # إرسال
                # ✅ v2.0: دعم الضغط
                payload = {
                    'instance_id': self.instance_id,
                    'device_id': self.instance_id,
                    'operations': batch_data,
                }

                raw, compressed = self._compress_payload(payload)

                headers = self._get_auth_headers()
                try:
                    if compressed:
                        headers['Content-Encoding'] = 'gzip'
                        headers['Content-Type'] = 'application/json'
                        response = self.session.post(
                            f"{self.cloud_api_url}/api/sync/push",
                            data=raw,
                            headers=headers,
                            timeout=self.timeout,
                        )
                    else:
                        response = self.session.post(
                            f"{self.cloud_api_url}/api/sync/push",
                            json=payload,
                            headers=headers,
                            timeout=self.timeout,
                        )

                    if response.status_code != 200:
                        raise Exception(
                            f"HTTP {response.status_code}: {response.text[:500]}"
                        )

                    result = response.json()

                except Exception as e:
                    logger.error(f"فشل إرسال الدفعة: {str(e)}")
                    for item in pending_sorted:
                        SyncQueueManager.mark_failed(session, item, str(e))
                    stats['failed'] = len(pending_sorted)
                    return stats                
                
                # معالجة الاستجابة
                results_map = {
                    r.get('entity_uuid'): r
                    for r in result.get('results', [])
                }
                
                for item in pending_sorted:
                    item_result = results_map.get(item.entity_uuid)
                    
                    if not item_result:
                        SyncQueueManager.mark_failed(
                            session, item, "لا توجد نتيجة"
                        )
                        stats['failed'] += 1
                        continue
                    
                    status = item_result.get('status')
                    
                    if status in ('synced', 'already_applied'):
                        SyncQueueManager.mark_synced(session, item)
                        stats['pushed'] += 1
                    elif status == 'conflict':
                        SyncQueueManager.mark_conflict(
                            session, item,
                            local_data=item.payload,
                            cloud_data=item_result.get('cloud_data', {}),
                            reason=item_result.get('reason', 'تعارض')
                        )
                        stats['conflicts'] += 1
                    else:
                        # ✅ v3: سجّل السبب الفعلي
                        error_msg = item_result.get('error', 'خطأ')
                        error_code = item_result.get('error_code')
                        logger.error(
                            f"❌ رفض السحابة: "
                            f"{item.entity_type}/{item.entity_uuid[:8]} "
                            f"[{error_code}] {error_msg[:300]}"
                        )
                        SyncQueueManager.mark_failed(
                            session, item,
                            error_msg,
                            error_code=error_code,
                        )
                        stats['failed'] += 1
                
                SyncMetadata.set(
                    session, self.KEY_LAST_PUSH, datetime.now().isoformat()
                )
        
        except Exception as e:
            logger.error(f"خطأ في Push: {str(e)}")
        
        return stats

    def _resolve_dependencies(self, session, item):
        """
        ✅ v3: إصلاح التبعيات فعلياً - يتعامل مع 2 و 3 عنصر tuples.
        
        البنية: (fk_field, ref_table) أو (fk_field, ref_table, ref_pk)
        إذا لم يُحدَّد ref_pk، نفترض 'id'.
        """
        if item.operation not in ('INSERT', 'UPDATE'):
            return

        payload = item.payload or {}

        # ✅ v3: FK_MAP موسّع مع دعم الصيغتين
        FK_MAP = {
            'users': [
                ('employee_id', 'employees'),
                ('role_id', 'roles'),
            ],
            'students': [
                ('grade_id', 'grades'),
                ('section_id', 'sections'),
                ('parent_id', 'parents'),
                ('academic_year_id', 'academic_years'),
            ],
            'sections': [
                ('grade_id', 'grades'),
            ],
            'grade_fee_structures': [
                ('grade_id', 'grades'),
                ('fee_type_id', 'fee_types'),
                ('academic_year_id', 'academic_years'),
            ],
            'student_fees': [
                ('student_id', 'students'),
                ('academic_year_id', 'academic_years'),
            ],
            'fee_installments': [
                ('student_fee_id', 'student_fees'),
            ],
            'receipts': [
                ('student_id', 'students'),
                ('installment_id', 'fee_installments'),
                ('created_by_user_id', 'users'),
            ],
            'homeworks': [
                ('grade_id', 'grades'),
                ('section_id', 'sections'),
                ('subject_id', 'subjects'),
                ('academic_year_id', 'academic_years'),
            ],
            'daily_attendance': [
                ('student_id', 'students'),
                ('grade_id', 'grades'),
                ('section_id', 'sections'),
            ],
            # ✅ v3: إضافات
            'notification_logs': [
                ('parent_id', 'parents'),
                ('notification_id', 'notifications'),
            ],
            'notifications': [
                ('created_by_user_id', 'users'),
            ],
            'behavioral_records': [
                ('student_id', 'students'),
                ('created_by_user_id', 'users'),
            ],
            'monthly_evaluations': [
                ('student_id', 'students'),
                ('subject_id', 'subjects'),
                ('academic_year_id', 'academic_years'),
            ],
            'term_exam_scores': [
                ('student_id', 'students'),
                ('subject_id', 'subjects'),
                ('academic_year_id', 'academic_years'),
            ],
            'employee_allowances_deductions': [
                ('employee_id', 'employees'),
            ],
            'employee_loans': [
                ('employee_id', 'employees'),
            ],
            'payroll_records': [
                ('employee_id', 'employees'),
            ],
            'expense_vouchers': [
                ('created_by_user_id', 'users'),
            ],
            'parent_devices': [
                ('parent_id', 'parents'),
            ],
            'student_documents': [
                ('student_id', 'students'),
            ],
            'student_academic_history': [
                ('student_id', 'students'),
                ('academic_year_id', 'academic_years'),
                ('grade_id', 'grades'),
                ('section_id', 'sections'),
            ],
            'teacher_subject_sections': [
                ('academic_year_id', 'academic_years'),
                ('grade_id', 'grades'),
                ('section_id', 'sections'),
                ('subject_id', 'subjects'),
                ('teacher_id', 'employees'),
            ],
        }

        deps_to_add = []
        missing_deps = []

        for entry in FK_MAP.get(item.entity_type, []):
            # ✅ v3: دعم كلتا الصيغتين
            if len(entry) == 2:
                fk_field, ref_table = entry
                ref_pk = 'id'
            elif len(entry) == 3:
                fk_field, ref_table, ref_pk = entry
            else:
                logger.warning(f"إدخال FK_MAP غير صالح: {entry}")
                continue

            ref_id = payload.get(fk_field)
            if not ref_id:
                continue

            ref_model = self._get_model_class(ref_table)
            if not ref_model:
                continue

            # ابحث عن الكائن المحلي
            ref_obj = session.query(ref_model).filter_by(
                **{ref_pk: ref_id}
            ).first()

            if not ref_obj:
                missing_deps.append(f"{ref_table}#{ref_id}")
                continue

            ref_sync_uuid = getattr(ref_obj, 'sync_uuid', None)
            if not ref_sync_uuid:
                continue

            # ✅ FIX: ابحث في الطابور بأي حالة (pending, synced, failed)
            # السبب: الاعتماد على pending/processing فقط يؤدي لتكرار لا نهائي
            # لأن التبعية تُزامن ثم تُعتبر "غير موجودة" في الدورة التالية.
            ref_item = session.execute(
                select(SyncQueue).where(
                    SyncQueue.entity_type == ref_table,
                    SyncQueue.entity_uuid == ref_sync_uuid,
                    SyncQueue.direction == 'to_cloud',
                    # ← أزلنا شرط status ليشمل كل الحالات
                ).order_by(SyncQueue.id.desc()).limit(1)
            ).scalar_one_or_none()

            if ref_item:
                # ارفع الأولوية إن كانت لا تزال معلقة
                if ref_item.status in ('pending', 'processing'):
                    if ref_item.priority > item.priority:
                        ref_item.priority = max(1, item.priority - 1)
                # إن كانت synced أو conflict → تجاهل تماماً
                continue

            # مُزامن مسبقاً؟
            if getattr(ref_obj, 'is_synced', False):
                continue

            # أضفه إلى الطابور
            # ✅ v4: منع التكرار
            ref_uuid = getattr(ref_obj, 'sync_uuid', None)
            if not ref_uuid:
                continue

            # هل هو موجود في session.new (مضاف حديثاً)؟
            already_in_new = any(
                getattr(o, 'sync_uuid', None) == ref_uuid
                and o.__class__.__name__ == ref_obj.__class__.__name__
                for o in session.new
                if hasattr(o, 'sync_uuid')
            )

            if already_in_new:
                continue

            deps_to_add.append(ref_obj)

        # أضف التبعيات
        from app.services.sync.sync_queue_manager import SyncQueueManager
        for dep_obj in deps_to_add:
            try:
                SyncQueueManager.enqueue(
                    session=session,
                    entity=dep_obj,
                    operation='INSERT',
                    direction='to_cloud',
                    priority=max(1, item.priority - 1),
                )
                logger.info(
                    f"➕ أضيفت تبعية للطابور: "
                    f"{dep_obj.__class__.__tablename__}/"
                    f"{dep_obj.sync_uuid[:8]} "
                    f"(من أجل {item.entity_type}/{item.entity_uuid[:8]})"
                )
            except Exception as e:
                logger.error(f"فشل إضافة تبعية: {e}")

        if missing_deps:
            logger.warning(
                f"⚠️ {item.entity_type}#{item.entity_local_id} "
                f"يشير إلى تبعيات غير موجودة محلياً: {missing_deps}"
            )
            item.next_retry_at = datetime.now() + timedelta(seconds=60)
            item.status = 'pending'
            
    @staticmethod
    def _get_model_class(table_name: str):
        """الحصول على موديل SQLAlchemy من اسم الجدول."""
        from app.database.models import Base
        for mapper in Base.registry.mappers:
            if getattr(mapper.class_, '__tablename__', None) == table_name:
                return mapper.class_
        return None
    
    
    # ==================== PULL: من السحابة إلى المحلي ====================
    
    def pull_from_cloud(self, batch_size: int = 500) -> Dict[str, int]:
        """
        سحب التغييرات من السحابة (Cursor-based).
        
        ✅ v2.0: يستخدم cursor بدلاً من timestamp - آمن ضد clock skew.
        """
        stats = {'pulled': 0, 'applied': 0, 'conflicts': 0, 'failed': 0}

        if not self.check_cloud_health():
            logger.warning("Cloud غير متاح - تخطي Pull")
            return stats

        # ✅ أضف هنا 👇
        # Backup قبل Pull كبير
        if config_manager.app_config.backup_before_pull:
            estimated_changes = self._estimate_pull_size()
            threshold = config_manager.app_config.backup_threshold

            if estimated_changes >= threshold:
                logger.warning(
                    f"⚠️ Pull كبير متوقع ({estimated_changes} تغيير) - "
                    f"إنشاء نسخة احتياطية..."
                )
                from app.services.backup_service import BackupService
                backup_path = BackupService.create_backup(
                    reason="pre_pull",
                    include_db=True,
                )
                if backup_path:
                    logger.info(f"✅ نسخة احتياطية: {backup_path}")
                else:
                    logger.error(
                        "❌ فشل النسخ الاحتياطي - تخطي Pull لأمان البيانات"
                    )
                    return stats
        # ✅ نهاية الإضافة        

        try:
            with session_scope() as session:
                # ✅ الحصول على آخر cursor
                cursor_str = SyncMetadata.get(session, self.KEY_LAST_CURSOR)
                cursor = int(cursor_str) if cursor_str else 0

                logger.info(f"سحب التغييرات من السحابة (cursor={cursor})")

                # ✅ طلب التغييرات
                response = self.session.get(
                    f"{self.cloud_api_url}/api/sync/pull",
                    params={
                        'instance_id': self.instance_id,
                        'device_id': self.instance_id,
                        'cursor': cursor,
                        'limit': batch_size,
                    },
                    headers=self._get_auth_headers(),
                    timeout=self.timeout
                )

                if response.status_code != 200:
                    logger.error(
                        f"فشل Pull: HTTP {response.status_code} - "
                        f"{response.text[:200]}"
                    )
                    return stats

                data = response.json()
                changes = data.get('changes', [])
                new_cursor = data.get('cursor', cursor)

                logger.info(
                    f"تم استلام {len(changes)} تغيير "
                    f"(cursor: {cursor} → {new_cursor})"
                )

                # ✅ تطبيق التغييرات - كترتيب id تصاعدي
                for change in changes:
                    try:
                        self._apply_cloud_change(session, change)
                        stats['applied'] += 1
                    except Exception as e:
                        logger.error(
                            f"فشل تطبيق التغيير "
                            f"{change.get('entity_type')}/"
                            f"{change.get('entity_uuid', '')[:8]}: {e}",
                            exc_info=True
                        )
                        stats['failed'] += 1

                stats['pulled'] = len(changes)

                # ✅ حفظ cursor الجديد
                SyncMetadata.set(
                    session, self.KEY_LAST_CURSOR, str(new_cursor)
                )
                SyncMetadata.set(
                    session, self.KEY_LAST_PULL, datetime.now().isoformat()
                )

        except Exception as e:
            logger.error(f"خطأ في Pull: {e}", exc_info=True)

        return stats

    def _estimate_pull_size(self) -> int:
        """تقدير عدد التغييرات المتوقعة من Pull."""
        try:
            with session_scope() as session:
                cursor_str = SyncMetadata.get(session, self.KEY_LAST_CURSOR)
                cursor = int(cursor_str) if cursor_str else 0

            # طلب HEAD فقط (بدون بيانات)
            response = self.session.head(
                f"{self.cloud_api_url}/api/sync/pull/count",
                params={
                    'instance_id': self.instance_id,
                    'device_id': self.instance_id,
                    'cursor': cursor,
                },
                headers=self._get_auth_headers(),
                timeout=5,
            )

            if response.status_code == 200:
                return int(response.headers.get('X-Pending-Count', 0))

        except Exception as e:
            logger.debug(f"تعذّر تقدير Pull: {e}")

        # افتراض محافظ
        return 0
        
    def _apply_cloud_change(self, session: Session, change: dict):
        """
        تطبيق تغيير واحد من السحابة.
        
        ✅ v2.0: يضبط sync_source='cloud' قبل الحذف/التعديل لتفادي
        إعادة التسجيل في الطابور.
        """
        from app.database.models import Base

        entity_type = change['entity_type']
        entity_uuid = change['entity_uuid']

        operation = (
            change.get('operation_type')
            or change.get('operation')
        )
        payload = change.get('payload')
        cloud_version = change.get('sync_version', 1)

        if not operation:
            raise ValueError(
                f"لا يوجد operation_type: {list(change.keys())}"
            )
        
        # ✅ v2.0: دعم Soft Delete من السحابة
        is_soft_delete = (
            operation == 'DELETE'
            or (payload and payload.get('deleted_at'))
        )

        # الحصول على موديل الكيان
        model_class = None
        for mapper in Base.registry.mappers:
            if getattr(mapper.class_, '__tablename__', None) == entity_type:
                model_class = mapper.class_
                break

        if not model_class:
            raise ValueError(f"جدول غير معروف: {entity_type}")

        # البحث عن الصف المحلي
        local_obj = session.query(model_class).filter_by(
            sync_uuid=entity_uuid
        ).first()

        # ============ DELETE ============
        if operation == 'DELETE':
            if local_obj:
                local_obj.sync_source = 'cloud'

                local_version = local_obj.sync_version or 1
                if local_version > cloud_version:
                    self._create_conflict(
                        session, entity_type, entity_uuid,
                        local_data=local_obj.to_sync_dict(),
                        cloud_data=None,
                        reason=f"حذف سحابي مع تعديل محلي أحدث",
                    )
                else:
                    # ✅ حذف ناعم إذا كان الحقل موجوداً
                    if hasattr(local_obj, 'deleted_at'):
                        local_obj.deleted_at = datetime.now()
                        local_obj.sync_version = cloud_version
                        local_obj.sync_source = 'cloud'
                        local_obj.is_synced = True
                    else:
                        session.delete(local_obj)
            return
        
        # ============ INSERT / UPDATE ============
        if operation in ('INSERT', 'UPDATE'):
            if local_obj:
                local_version = local_obj.sync_version or 1

                if local_version > cloud_version:
                    # تعارض: النسخة المحلية أحدث
                    self._create_conflict(
                        session, entity_type, entity_uuid,
                        local_data=local_obj.to_sync_dict(),
                        cloud_data=payload,
                        reason=f"نسخة محلية أحدث "
                               f"({local_version} > {cloud_version})",
                    )
                    return

                if local_version == cloud_version:
                    # ✅ v3: قارن المحتوى بدلاً من افتراض التعارض
                    if self._is_same_content(local_obj, payload):
                        # نفس المحتوى - فقط علّم كمزامن
                        local_obj.sync_source = 'cloud'
                        local_obj.is_synced = True
                        logger.debug(
                            f"↺ تجاهل تغيير مطابق: "
                            f"{entity_type}/{entity_uuid[:8]}"
                        )
                        return

                    # محتوى مختلف بنفس النسخة - تعارض حقيقي
                    self._create_conflict(
                        session, entity_type, entity_uuid,
                        local_data=local_obj.to_sync_dict(),
                        cloud_data=payload,
                        reason=(
                            f"نفس النسخة ({local_version}) لكن "
                            f"محتوى مختلف"
                        ),
                    )
                    return
                
                # ✅ النسخة السحابية أحدث - طبّق
                self._set_fields(local_obj, payload)
                local_obj.sync_version = cloud_version
                local_obj.sync_source = 'cloud'  # ✅
                local_obj.is_synced = True
            else:
                # ✅ صف جديد من السحابة
                new_obj = model_class()
                self._set_fields(new_obj, payload)

                if not getattr(new_obj, 'sync_uuid', None):
                    new_obj.sync_uuid = entity_uuid

                new_obj.sync_version = cloud_version
                new_obj.sync_source = 'cloud'  # ✅
                new_obj.is_synced = True

                session.add(new_obj)

    def _is_same_content(self, obj, payload: dict) -> bool:
        """
        ✅ v3: هل المحتوى المحلي مطابق للـ payload القادم من السحابة؟
        
        نتجاهل الحقول الميتاداتا والمتغيرة باستمرار.
        """
        if not payload:
            return False

        # الحقول التي لا تُقارن
        IGNORE = {
            'id', 'created_at', 'updated_at',
            'sync_updated_at', 'sync_version',
            'sync_source', 'is_synced',
        }

        # احصل على بيانات الصف المحلي
        local_data = obj.get_sync_data()

        # قارن الحقول المشتركة (بعد تجاهل الميتاداتا)
        for key, cloud_val in payload.items():
            if key in IGNORE:
                continue

            local_val = local_data.get(key)

            # ✅ تحويل للتوافق مع JSON (مثل isoformat)
            from app.database.models.sync_mixin import SyncableMixin
            local_safe = SyncableMixin._make_json_safe(local_val)

            # مقارنة مباشرة
            if local_safe != cloud_val:
                # مقارنة كـ strings (للتواريخ والأرقام)
                if str(local_safe) != str(cloud_val):
                    logger.debug(
                        f"فرق في {key}: {local_safe!r} != {cloud_val!r}"
                    )
                    return False

        return True                

    def _create_conflict(
        self,
        session: Session,
        entity_type: str,
        entity_uuid: str,
        local_data: dict,
        cloud_data: Optional[dict],
        reason: str,
        sync_queue_id: Optional[int] = None,
    ):
        """
        إنشاء/تحديث سجل تعارض.
        
        ✅ v3.1: إذا كان هناك تعارض مفتوح لنفس الكيان،
        يُحدّثه بدل إنشاء صف جديد (يمنع التراكم).
        """
        # ✅ v3.1: ابحث عن تعارض مفتوح مسبقاً لنفس الكيان
        existing = session.query(SyncConflict).filter_by(
            entity_type=entity_type,
            entity_uuid=entity_uuid,
            status='open',
        ).first()

        if existing:
            # حدّث البيانات بدل إنشاء جديد
            existing.local_version = local_data
            existing.cloud_version = cloud_data
            existing.conflict_reason = reason
            if sync_queue_id is not None:
                existing.sync_queue_id = sync_queue_id
            logger.debug(
                f"↻ تحديث تعارض موجود: "
                f"{entity_type}/{entity_uuid[:8]}"
            )
            return existing

        # البحث عن queue_item إن لم يُمرَّر
        if sync_queue_id is None:
            existing_queue = session.execute(
                select(SyncQueue).where(
                    SyncQueue.entity_type == entity_type,
                    SyncQueue.entity_uuid == entity_uuid,
                    SyncQueue.direction == 'to_cloud',
                    SyncQueue.status.in_(['pending', 'processing']),
                ).limit(1)
            ).scalar_one_or_none()
            if existing_queue:
                sync_queue_id = existing_queue.id

        conflict = SyncConflict(
            sync_queue_id=sync_queue_id,
            entity_type=entity_type,
            entity_uuid=entity_uuid,
            local_version=local_data,
            cloud_version=cloud_data,
            status='open',
            conflict_reason=reason,
            resolution_strategy='pending',
        )
        session.add(conflict)
        logger.warning(
            f"⚠️ تعارض جديد: {entity_type}/{entity_uuid[:8]} - {reason} "
            f"(queue_id={sync_queue_id})"
        )
        return conflict 
    # ==================== المزامنة الكاملة ====================
    
    def full_sync(self) -> Dict[str, Dict]:
        """مزامنة كاملة (Pull قبل Push)."""
        logger.info("=" * 60)
        logger.info("بدء مزامنة كاملة")
        logger.info("=" * 60)
        
        results = {
            'pull': {'pulled': 0, 'applied': 0, 'failed': 0},
            'push': {'pushed': 0, 'failed': 0, 'conflicts': 0},
            'conflicts_resolved': {'resolved': 0, 'failed': 0},
        }
        
        try:
            # ✅ 1. Pull أولاً (لتحديث sync_version)
            logger.info("1. سحب التغييرات من السحابة...")
            results['pull'] = self.pull_from_cloud()
            
            # ✅ 2. ثم Push (بدون تعارضات)
            logger.info("2. إرسال التغييرات المحلية...")
            results['push'] = self.push_to_cloud()
            
            # ✅ 3. حل التعارضات المتبقية
            logger.info("3. حل التعارضات...")
            with session_scope() as session:
                results['conflicts_resolved'] = ConflictResolver.auto_resolve_all(session)
            
            logger.info("=" * 60)
            logger.info(f"نتائج المزامنة:")
            logger.info(f"  Pull: {results['pull']}")
            logger.info(f"  Push: {results['push']}")
            logger.info(f"  Conflicts: {results['conflicts_resolved']}")
            logger.info("=" * 60)
        
        except Exception as e:
            logger.error(f"فشل المزامنة الكاملة: {str(e)}")
        
        return results

    def get_sync_status(self) -> Dict[str, Any]:
        """الحصول على حالة المزامنة الحالية."""
        try:
            with session_scope() as session:
                queue_stats = SyncQueueManager.get_stats(session)
                
                conflicts_count = session.query(SyncConflict).filter(
                    SyncConflict.status == 'open'
                ).count()
                
                last_push = SyncMetadata.get(session, self.KEY_LAST_PUSH)
                last_pull = SyncMetadata.get(session, self.KEY_LAST_PULL)
                
                return {
                    'queue': queue_stats,
                    'open_conflicts': conflicts_count,
                    'last_push': last_push,
                    'last_pull': last_pull,
                    'instance_id': self.instance_id,
                    'cloud_available': self.check_cloud_health(),
                }
        except Exception as e:
            logger.error(f"فشل الحصول على الحالة: {str(e)}")
            return {}



    def get_detailed_status(self) -> Dict[str, Any]:
        """حالة مفصّلة (مع مقاييس)."""
        from app.services.sync.sync_metrics import SyncMetrics

        try:
            with session_scope() as session:
                health = SyncMetrics.get_health_status(session)
                top_tables = SyncMetrics.get_top_tables(session, limit=5)

                return {
                    **health,
                    'top_tables': [
                        {
                            'table': t.entity_type,
                            'pending': t.pending,
                            'failed': t.failed,
                            'synced_1h': t.synced_last_hour,
                        }
                        for t in top_tables
                    ],
                    'instance_id': self.instance_id,
                    'cloud_available': self.check_cloud_health(),
                }
        except Exception as e:
            logger.error(f"فشل الحصول على الحالة المفصّلة: {e}")
            return {'status': 'error', 'error': str(e)}