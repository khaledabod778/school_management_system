"""
حل التعارضات في المزامنة.

v2.0:
- SENSITIVE_FIELDS_BY_TABLE - حساسية حسب السياق
- استراتيجيات أذكى للتعارضات
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, Set

from sqlalchemy.orm import Session

from app.database.models.sync import SyncConflict, SyncQueue

logger = logging.getLogger(__name__)


class ConflictResolver:
    """
    مسؤول عن حل التعارضات.
    """

    # ✅ حقول لا تُدمج أبداً (ميتاداتا)
    NO_MERGE_FIELDS = frozenset({
        'sync_version', 'sync_updated_at', 'updated_at',
        'created_at', 'sync_uuid', 'is_synced',
    })

    # ✅ v2.0: الحقول الحساسة حسب الجدول
    # عند تعارض في هذه الحقول → تدخل يدوي مطلوب
    SENSITIVE_FIELDS_BY_TABLE: Dict[str, Set[str]] = {
        'receipts': {
            'amount_paid', 'payment_method', 'payment_target',
            'status', 'cancellation_reason',
        },
        'expense_vouchers': {
            'amount', 'beneficiary_name', 'payment_method',
            'status', 'expense_category',
        },
        'employee_loans': {
            'total_loan_amount', 'monthly_deduction',
            'remaining_amount', 'status',
        },
        'employee_allowances_deductions': {
            'amount', 'type',
        },
        'payroll_records': {
            'basic_salary', 'net_salary', 'total_allowances',
            'total_deductions', 'loan_deduction', 'payment_status',
        },
        'student_fees': {
            'net_total_required', 'discount_amount',
            'previous_debt', 'current_year_fees',
        },
        'fee_installments': {
            'amount', 'paid_amount', 'installment_type',
        },
        'grade_fee_structures': {
            'amount',
        },
        'students': {
            'student_number', 'status', 'enrollment_type',
            'academic_year_id', 'grade_id', 'section_id',
        },
        'employees': {
            'basic_salary', 'status', 'national_id',
            'payment_method',
        },
        'users': {
            'username', 'role_id', 'status', 'password_hash',
        },
        'academic_years': {
            'is_current', 'status', 'is_closed',
        },
    }

    # ✅ استراتيجية افتراضية حسب الجدول
    DEFAULT_STRATEGY_BY_TABLE: Dict[str, str] = {
        'receipts': 'manual',       # الحركات المالية تحتاج مراجعة
        'expense_vouchers': 'manual',
        'payroll_records': 'manual',
        'employee_loans': 'manual',
    }

    # ==================== API الرئيسي ====================

    @classmethod
    def resolve(
        cls,
        session: Session,
        conflict: SyncConflict,
        strategy: str = "auto"
    ) -> Tuple[bool, Optional[dict], str]:
        """حل تعارض."""
        local_data = conflict.local_version
        cloud_data = conflict.cloud_version
        base_data = conflict.base_version

        conflict_type = cls._detect_conflict_type(
            local_data, cloud_data, base_data,
            entity_type=conflict.entity_type,
        )

        # الحذف لا يُدمج تلقائياً
        if conflict_type == "deleted_local":
            return False, None, "الصف محذوف محلياً - يحتاج قراراً يدوياً"
        if conflict_type == "deleted_cloud":
            return False, None, "الصف محذوف في السحابة - يحتاج قراراً يدوياً"

        local_data = local_data or {}
        cloud_data = cloud_data or {}

        # ✅ اختيار الاستراتيجية تلقائياً
        if strategy == "auto":
            default = cls.DEFAULT_STRATEGY_BY_TABLE.get(
                conflict.entity_type, 'auto'
            )
            if default == 'manual' and conflict_type == 'sensitive':
                return False, None, (
                    f"تعارض في حقول حرجة ({conflict.entity_type}) - "
                    "يتطلب مراجعة يدوية"
                )

            if conflict_type == "no_conflict":
                resolved, reason = cls._merge_fields(
                    local_data, cloud_data, base_data
                )
            elif conflict_type == "sensitive":
                return False, None, "تعارض في حقول حساسة - يتطلب مراجعة يدوية"
            else:
                resolved, reason = cls._last_write_wins(local_data, cloud_data)

        elif strategy == "local_wins":
            resolved = local_data
            reason = "تم اختيار النسخة المحلية (يدوياً)"
        elif strategy == "cloud_wins":
            resolved = cloud_data
            reason = "تم اختيار النسخة السحابية (يدوياً)"
        elif strategy == "merge":
            resolved, reason = cls._merge_fields(
                local_data, cloud_data, base_data
            )
        else:
            return False, None, f"استراتيجية غير معروفة: {strategy}"

        conflict.resolution_strategy = strategy if strategy != "auto" else "merge"
        conflict.resolved_data = resolved
        conflict.resolved_at = datetime.now()
        conflict.status = 'resolved'

        session.flush()
        logger.info(
            f"✅ حل التعارض: {conflict.entity_type}/"
            f"{conflict.entity_uuid[:8]} - {reason}"
        )
        return True, resolved, reason

    # ==================== كشف نوع التعارض ====================

    @classmethod
    def _detect_conflict_type(
        cls,
        local: Optional[dict],
        cloud: Optional[dict],
        base: Optional[dict],
        entity_type: Optional[str] = None,
    ) -> str:
        """اكتشاف نوع التعارض (مع مراعاة الجدول)."""
        if local is None:
            return "deleted_local"
        if cloud is None:
            return "deleted_cloud"

        if local.get('_deleted') or local.get('deleted_at'):
            return "deleted_local"
        if cloud.get('_deleted') or cloud.get('deleted_at'):
            return "deleted_cloud"

        if not base:
            return "real"

        local_changed = set()
        cloud_changed = set()

        for field in set(local.keys()) | set(cloud.keys()):
            if field in cls.NO_MERGE_FIELDS:
                continue

            local_val = local.get(field)
            cloud_val = cloud.get(field)
            base_val = base.get(field)

            if local_val != base_val:
                local_changed.add(field)
            if cloud_val != base_val:
                cloud_changed.add(field)

        conflicting_fields = local_changed & cloud_changed

        if not conflicting_fields:
            return "no_conflict"

        # ✅ فحص الحقول الحساسة حسب الجدول
        sensitive = cls.SENSITIVE_FIELDS_BY_TABLE.get(entity_type, set())
        if conflicting_fields & sensitive:
            return "sensitive"

        return "real"

    # ==================== استراتيجيات الحل ====================

    @classmethod
    def _last_write_wins(
        cls,
        local: dict,
        cloud: dict
    ) -> Tuple[dict, str]:
        """آخر تعديل يفوز."""
        local_time = local.get('sync_updated_at') or local.get('updated_at')
        cloud_time = cloud.get('sync_updated_at') or cloud.get('updated_at')

        if not local_time:
            return cloud, "السحابي أحدث (لا يوجد وقت محلي)"
        if not cloud_time:
            return local, "المحلي أحدث (لا يوجد وقت سحابي)"

        if str(local_time) > str(cloud_time):
            return local, f"المحلي أحدث ({local_time} > {cloud_time})"
        return cloud, f"السحابي أحدث ({cloud_time} > {local_time})"

    @classmethod
    def _merge_fields(
        cls,
        local: dict,
        cloud: dict,
        base: Optional[dict]
    ) -> Tuple[dict, str]:
        """دمج الحقول غير المتعارضة."""
        merged = dict(base) if base else {}
        conflicts = []

        all_fields = set(local.keys()) | set(cloud.keys())

        for field in all_fields:
            if field in cls.NO_MERGE_FIELDS:
                continue

            local_val = local.get(field)
            cloud_val = cloud.get(field)
            base_val = base.get(field) if base else None

            if local_val == cloud_val:
                merged[field] = local_val
                continue

            local_changed = local_val != base_val
            cloud_changed = cloud_val != base_val

            if local_changed and not cloud_changed:
                merged[field] = local_val
            elif cloud_changed and not local_changed:
                merged[field] = cloud_val
            else:
                conflicts.append(field)
                local_time = local.get('sync_updated_at')
                cloud_time = cloud.get('sync_updated_at')
                if str(local_time or '') >= str(cloud_time or ''):
                    merged[field] = local_val
                else:
                    merged[field] = cloud_val

        reason = (
            f"دمج {len(all_fields)} حقل، "
            f"{len(conflicts)} تعارض مُحلّ بـ last-write-wins"
        )
        return merged, reason

    # ==================== Auto-Resolve ====================

    @classmethod
    def auto_resolve_all(cls, session: Session) -> Dict[str, int]:
        """حل جميع التعارضات تلقائياً."""
        conflicts = session.query(SyncConflict).filter(
            SyncConflict.status == 'open'
        ).all()

        stats = {'resolved': 0, 'failed': 0, 'skipped': 0}

        for conflict in conflicts:
            try:
                success, resolved_data, reason = cls.resolve(session, conflict)
                if success:
                    stats['resolved'] += 1
                    cls._requeue_resolved(session, conflict, resolved_data)
                else:
                    stats['failed'] += 1
            except Exception as e:
                logger.error(
                    f"فشل حل التعارض {conflict.id}: {e}", exc_info=True
                )
                stats['skipped'] += 1

        session.flush()
        return stats

    @classmethod
    def _requeue_resolved(
        cls,
        session: Session,
        conflict: SyncConflict,
        resolved_data: dict
    ):
        """إعادة العملية إلى الطابور بعد الحل."""
        if not conflict.sync_queue_id:
            logger.warning(
                f"⚠️ التعارض {conflict.id} لا يوجد له queue_id - "
                "لا يمكن إعادته"
            )
            return

        queue_item = session.get(SyncQueue, conflict.sync_queue_id)
        if queue_item:
            queue_item.payload = resolved_data
            queue_item.status = 'pending'
            queue_item.attempts = 0
            queue_item.next_retry_at = datetime.now()
            queue_item.last_error = None
            session.flush()
            logger.info(
                f"🔄 أُعيد التعارض {conflict.id} إلى الطابور "
                f"(queue_id={queue_item.id})"
            )