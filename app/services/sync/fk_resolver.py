"""
FK Resolver - يحوّل FK IDs المحلية إلى sync_uuids قبل الإرسال.

عند Push، نستبدل:
  'academic_year_id': 1
بـ:
  'academic_year_id': 1,           # للإبقاء
  'academic_year_uuid': 'abc-...'  # ← للمزامنة

السحابة تستخدم UUID لإيجاد المرجع الصحيح.
"""

import logging
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class FKResolver:
    """يحوّل FK IDs إلى UUIDs للمزامنة."""

    # ✅ خريطة: (اسم الحقل، موديل المرجع، حقل العرض)
    FK_MAP = {
        # Users
        'employee_id': ('employees', 'id'),
        'role_id': ('roles', 'id'),

        # Students
        'grade_id': ('grades', 'id'),
        'section_id': ('sections', 'id'),
        'parent_id': ('parents', 'id'),
        'academic_year_id': ('academic_years', 'id'),

        # Fees & Receipts
        'fee_type_id': ('fee_types', 'id'),
        'student_id': ('students', 'id'),
        'student_fee_id': ('student_fees', 'id'),
        'installment_id': ('fee_installments', 'id'),
        'created_by_user_id': ('users', 'id'),

        # Employees
        'employee_id': ('employees', 'id'),

        # Academic
        'subject_id': ('subjects', 'id'),
        'teacher_id': ('employees', 'id'),

        # Notifications
        'notification_id': ('notifications', 'id'),

        # Schedules
        'homework_id': ('homeworks', 'id'),
        'exam_id': ('final_exam_schedules', 'id'),

        # Misc
        'closed_by_user_id': ('users', 'id'),
        'resolved_by_user_id': ('users', 'id'),
    }

    # ⚠️ الحقول التي لا نحولها (reference إلى نفس الجدول)
    SKIP_FIELDS = {
        'id', 'sync_uuid', 'sync_version',
        'sync_updated_at', 'sync_source', 'is_synced',
        'created_at', 'updated_at', 'deleted_at',
    }

    @classmethod
    def enrich_payload(
        cls,
        session: Session,
        entity_type: str,
        payload: dict,
    ) -> dict:
        """
        يُغني payload بـ UUIDs لحقول FK.
        
        Returns:
            payload جديد يحتوي حقول إضافية مثل:
            'academic_year_uuid': 'abc-...'
        """
        if not payload:
            return payload

        from app.database.models import Base

        # بناء خريطة model_name → class
        models_by_table = {}
        for mapper in Base.registry.mappers:
            tbl = getattr(mapper.class_, '__tablename__', None)
            if tbl:
                models_by_table[tbl] = mapper.class_

        enriched = dict(payload)

        for field_name, value in payload.items():
            if field_name in cls.SKIP_FIELDS:
                continue
            if not field_name.endswith('_id'):
                continue
            if value is None:
                continue

            # ابحث في FK_MAP
            fk_info = cls.FK_MAP.get(field_name)
            if not fk_info:
                continue

            ref_table, ref_pk = fk_info
            ref_model = models_by_table.get(ref_table)
            if not ref_model:
                continue

            # ابحث عن المرجع المحلي
            try:
                ref_obj = session.query(ref_model).filter_by(
                    **{ref_pk: value}
                ).first()

                if ref_obj and getattr(ref_obj, 'sync_uuid', None):
                    # ✅ أضف uuid
                    uuid_field = field_name.replace('_id', '_uuid')
                    enriched[uuid_field] = ref_obj.sync_uuid

            except Exception as e:
                logger.debug(f"FK resolve فشل لـ {field_name}={value}: {e}")

        return enriched