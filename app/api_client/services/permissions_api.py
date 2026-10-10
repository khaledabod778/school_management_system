"""خدمة الأدوار والصلاحيات."""

import logging
from typing import Dict, List

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class PermissionsApiService:
    def __init__(self, client: ApiClient):
        self.client = client

    # ============ Modules ============
    def get_modules(self) -> Dict:
        return self.client.get("/api/permissions/modules")

    # ============ Roles ============
    def list_roles(self) -> List[Dict]:
        return self.client.get("/api/permissions/roles")

    def create_role(self, payload: Dict) -> Dict:
        return self.client.post("/api/permissions/roles", json=payload)

    def update_role(self, role_id: int, payload: Dict) -> Dict:
        return self.client.put(
            f"/api/permissions/roles/{role_id}", json=payload
        )

    def delete_role(self, role_id: int) -> Dict:
        return self.client.delete(f"/api/permissions/roles/{role_id}")

    # ============ Matrix ============
    def get_role_matrix(self, role_id: int) -> Dict:
        return self.client.get(
            f"/api/permissions/roles/{role_id}/matrix"
        )

    def save_role_matrix(self, role_id: int, payload: Dict) -> Dict:
        return self.client.post(
            f"/api/permissions/roles/{role_id}/matrix", json=payload
        )