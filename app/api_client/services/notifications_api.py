"""خدمة الإشعارات."""

import logging
from typing import Dict, List, Optional

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class NotificationsApiService:
    def __init__(self, client: ApiClient):
        self.client = client

    # ============ List / CRUD ============
    def list_notifications(self, limit: int = 500) -> List[Dict]:
        return self.client.get(
            "/api/notifications/", params={'limit': limit}
        )

    def get_notification(self, notification_id: int) -> Dict:
        return self.client.get(f"/api/notifications/{notification_id}")

    def delete_notification(self, notification_id: int) -> Dict:
        return self.client.delete(f"/api/notifications/{notification_id}")

    # ============ Dialog helpers ============
    def list_grades(self) -> List[Dict]:
        return self.client.get("/api/notifications/grades")

    def list_sections(self, grade_id: int) -> List[Dict]:
        return self.client.get(
            "/api/notifications/sections", params={'grade_id': grade_id}
        )

    def list_parents(self, limit: int = 50) -> List[Dict]:
        return self.client.get(
            "/api/notifications/parents", params={'limit': limit}
        )

    # ============ Send ============
    def resolve_targets(self, payload: Dict) -> Dict:
        return self.client.post(
            "/api/notifications/resolve-targets", json=payload
        )

    def send_notification(self, payload: Dict) -> Dict:
        return self.client.post("/api/notifications/send", json=payload)