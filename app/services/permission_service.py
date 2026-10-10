"""
خدمة الصلاحيات - التحقق من صلاحيات المستخدم.
"""

import logging
from typing import Dict, Optional
from sqlalchemy import select

from app.database.session import session_scope
from app.database.models import User, Role, Permission, RolePermission

logger = logging.getLogger(__name__)


class PermissionService:
    """خدمة إدارة الصلاحيات."""
    
    def __init__(self, user: User):
        self.user = user
        self.role_name = ""
        self.permissions: Dict[str, Dict[str, bool]] = {}
        self._load_permissions()
    
    def _load_permissions(self):
        """تحميل صلاحيات المستخدم."""
        try:
            with session_scope() as session:
                role = session.get(Role, self.user.role_id) if self.user.role_id else None
                
                if role:
                    self.role_name = role.role_name
                    
                    role_permissions = session.execute(
                        select(RolePermission, Permission)
                        .join(Permission, RolePermission.permission_id == Permission.id)
                        .where(RolePermission.role_id == role.id)
                    ).all()
                    
                    for rp, perm in role_permissions:
                        self.permissions[perm.module_name] = {
                            'can_view': rp.can_view,
                            'can_add': rp.can_add,
                            'can_edit': rp.can_edit,
                            'can_delete': rp.can_delete,
                            'can_print': rp.can_print,
                            'can_cancel': rp.can_cancel,
                        }
                    
                    logger.info(f"تم تحميل صلاحيات الدور: {role.role_name}")
        except Exception as e:
            logger.error(f"فشل تحميل الصلاحيات: {str(e)}")
    
    def is_admin(self) -> bool:
        """التحقق من كون المستخدم مدير نظام."""
        return self.role_name == "مدير النظام"
    
    def can_view(self, module: str) -> bool:
        """التحقق من صلاحية العرض."""
        if self.is_admin():
            return True
        return self.permissions.get(module, {}).get('can_view', False)
    
    def can_add(self, module: str) -> bool:
        """التحقق من صلاحية الإضافة."""
        if self.is_admin():
            return True
        return self.permissions.get(module, {}).get('can_add', False)
    
    def can_edit(self, module: str) -> bool:
        """التحقق من صلاحية التعديل."""
        if self.is_admin():
            return True
        return self.permissions.get(module, {}).get('can_edit', False)
    
    def can_delete(self, module: str) -> bool:
        """التحقق من صلاحية الحذف."""
        if self.is_admin():
            return True
        return self.permissions.get(module, {}).get('can_delete', False)
    
    def can_print(self, module: str) -> bool:
        """التحقق من صلاحية الطباعة."""
        if self.is_admin():
            return True
        return self.permissions.get(module, {}).get('can_print', False)
    
    def can_cancel(self, module: str) -> bool:
        """التحقق من صلاحية الإلغاء."""
        if self.is_admin():
            return True
        return self.permissions.get(module, {}).get('can_cancel', False)
    
    def has_permission(self, module: str, action: str) -> bool:
        """التحقق من صلاحية محددة."""
        if self.is_admin():
            return True
        
        action_map = {
            'view': 'can_view',
            'add': 'can_add',
            'edit': 'can_edit',
            'delete': 'can_delete',
            'print': 'can_print',
            'cancel': 'can_cancel',
        }
        
        key = action_map.get(action, 'can_view')
        return self.permissions.get(module, {}).get(key, False)