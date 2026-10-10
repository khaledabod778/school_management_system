"""
نقاط نهاية المزامنة على Cloud API.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.session import session_scope
from app.database.models import Base

router = APIRouter(prefix="/api/sync", tags=["sync"])


class SyncOperation(BaseModel):
    operation: str  # INSERT/UPDATE/DELETE
    entity_type: str
    entity_uuid: str
    payload: Optional[Dict[str, Any]] = None
    old_payload: Optional[Dict[str, Any]] = None
    sync_version: int = 1
    source_instance_id: Optional[str] = None
    created_at: Optional[str] = None


class PushRequest(BaseModel):
    instance_id: str
    operations: List[SyncOperation]


class PushResult(BaseModel):
    entity_uuid: str
    status: str  # synced/conflict/failed
    error: Optional[str] = None
    error_code: Optional[str] = None
    cloud_data: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None


@router.get("/health")
async def health_check():
    """فحص صحة Cloud API."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@router.post("/push")
async def push_changes(
    request: PushRequest,
    x_instance_id: Optional[str] = Header(None),
):
    """استقبال تغييرات من عميل."""
    results = []
    
    with session_scope() as session:
        for op in request.operations:
            try:
                result = _process_operation(session, op, request.instance_id)
                results.append(result)
            except Exception as e:
                results.append(PushResult(
                    entity_uuid=op.entity_uuid,
                    status="failed",
                    error=str(e)
                ))
    
    return {
        "success": True,
        "results": [r.dict() for r in results],
        "server_time": datetime.now().isoformat()
    }


@router.get("/pull")
async def pull_changes(
    instance_id: str,
    since: str,
    limit: int = 500,
):
    """إرسال التغييرات إلى عميل."""
    # هنا يتم الاستعلام عن sync_queue في Cloud
    # وإرجاع العمليات الموجهة لهذا العميل
    changes = []
    
    return {
        "success": True,
        "changes": changes,
        "count": len(changes),
        "server_time": datetime.now().isoformat()
    }


def _process_operation(session: Session, op: SyncOperation, source_instance: str) -> PushResult:
    """معالجة عملية واحدة."""
    # الحصول على الموديل
    model_class = None
    for mapper in Base.registry.mappers:
        if hasattr(mapper.class_, '__tablename__'):
            if mapper.class_.__tablename__ == op.entity_type:
                model_class = mapper.class_
                break
    
    if not model_class:
        return PushResult(
            entity_uuid=op.entity_uuid,
            status="failed",
            error=f"جدول غير معروف: {op.entity_type}"
        )
    
    # البحث عن الصف
    existing = session.query(model_class).filter_by(sync_uuid=op.entity_uuid).first()
    
    if op.operation == 'DELETE':
        if existing:
            session.delete(existing)
        return PushResult(entity_uuid=op.entity_uuid, status="synced")
    
    if op.operation in ('INSERT', 'UPDATE'):
        if existing:
            # تحقق من التعارض
            if existing.sync_version > op.sync_version:
                return PushResult(
                    entity_uuid=op.entity_uuid,
                    status="conflict",
                    cloud_data=existing.to_sync_dict(),
                    reason=f"النسخة السحابية أحدث ({existing.sync_version} > {op.sync_version})"
                )
            
            # تحديث
            for key, value in (op.payload or {}).items():
                if hasattr(existing, key) and key not in ('id', 'sync_uuid'):
                    setattr(existing, key, value)
            existing.sync_version = op.sync_version + 1
        else:
            # إدراج جديد
            new_obj = model_class()
            for key, value in (op.payload or {}).items():
                if hasattr(new_obj, key) and key != 'id':
                    setattr(new_obj, key, value)
            new_obj.sync_source = 'cloud'
            session.add(new_obj)
        
        return PushResult(entity_uuid=op.entity_uuid, status="synced")
    
    return PushResult(
        entity_uuid=op.entity_uuid,
        status="failed",
        error=f"عملية غير معروفة: {op.operation}"
    )