"""خدمة الموظفين + المستخدمين + الملف الشخصي."""

import logging
from typing import Dict, List, Optional

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class HrUsersApiService:
    def __init__(self, client: ApiClient):
        self.client = client

    # ==================== Employees ====================
    def list_employees(self, search: Optional[str] = None) -> List[Dict]:
        params = {'search': search} if search else {}
        return self.client.get("/api/hr/employees/", params=params)

    def get_employee(self, eid: int) -> Dict:
        return self.client.get(f"/api/hr/employees/{eid}")

    def create_employee(self, data: Dict) -> Dict:
        return self.client.post("/api/hr/employees/", json=data)

    def update_employee(self, eid: int, data: Dict) -> Dict:
        return self.client.put(f"/api/hr/employees/{eid}", json=data)

    def delete_employee(self, eid: int) -> Dict:
        return self.client.delete(f"/api/hr/employees/{eid}")

    # ==================== Users ====================
    def list_users(self) -> List[Dict]:
        return self.client.get("/api/hr/users/")

    def get_user(self, uid: int) -> Dict:
        return self.client.get(f"/api/hr/users/{uid}")

    def create_user(self, data: Dict) -> Dict:
        return self.client.post("/api/hr/users/", json=data)

    def update_user(self, uid: int, data: Dict) -> Dict:
        return self.client.put(f"/api/hr/users/{uid}", json=data)

    def reset_password(self, uid: int) -> Dict:
        return self.client.post(f"/api/hr/users/{uid}/reset-password")

    def toggle_user(self, uid: int) -> Dict:
        return self.client.post(f"/api/hr/users/{uid}/toggle")

    def list_roles(self) -> List[Dict]:
        return self.client.get("/api/hr/roles/")

    # ==================== Profile ====================
    def get_profile(self) -> Dict:
        return self.client.get("/api/hr/profile/")

    def update_profile(self, data: Dict) -> Dict:
        return self.client.put("/api/hr/profile/", json=data)

    def change_password(self, current: str, new: str) -> Dict:
        return self.client.post(
            "/api/hr/profile/change-password",
            json={
                'current_password': current,
                'new_password': new,
            },
        )