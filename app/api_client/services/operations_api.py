"""خدمة المتابعة اليومية: الحضور + الواجبات + السلوك."""

import logging
from typing import Dict, List, Optional

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class OperationsApiService:
    def __init__(self, client: ApiClient):
        self.client = client

    # ==================== Attendance ====================
    def get_attendance(
        self,
        academic_year_id: int,
        grade_id: int,
        section_id: int,
        attendance_date: str,
    ) -> Dict:
        return self.client.get(
            "/api/operations/attendance/",
            params={
                'academic_year_id': academic_year_id,
                'grade_id': grade_id,
                'section_id': section_id,
                'attendance_date': attendance_date,
            },
        )

    def save_attendance(self, payload: Dict) -> Dict:
        return self.client.post(
            "/api/operations/attendance/", json=payload
        )

    # ==================== Homeworks ====================
    def list_homeworks(self, academic_year_id: int) -> Dict:
        return self.client.get(
            "/api/operations/homeworks/",
            params={'academic_year_id': academic_year_id},
        )

    def get_homework(self, homework_id: int) -> Dict:
        return self.client.get(
            f"/api/operations/homeworks/{homework_id}"
        )

    def create_homework(self, payload: Dict) -> Dict:
        return self.client.post(
            "/api/operations/homeworks/", json=payload
        )

    def update_homework(self, homework_id: int, payload: Dict) -> Dict:
        return self.client.put(
            f"/api/operations/homeworks/{homework_id}", json=payload
        )

    def delete_homework(self, homework_id: int) -> Dict:
        return self.client.delete(
            f"/api/operations/homeworks/{homework_id}"
        )

    # ==================== Behavior ====================
    def list_behavior(self, academic_year_id: int) -> List[Dict]:
        return self.client.get(
            "/api/operations/behavior/",
            params={'academic_year_id': academic_year_id},
        )

    def get_behavior(self, record_id: int) -> Dict:
        return self.client.get(
            f"/api/operations/behavior/{record_id}"
        )

    def create_behavior(self, payload: Dict) -> Dict:
        return self.client.post(
            "/api/operations/behavior/", json=payload
        )

    def update_behavior(self, record_id: int, payload: Dict) -> Dict:
        return self.client.put(
            f"/api/operations/behavior/{record_id}", json=payload
        )

    def delete_behavior(self, record_id: int) -> Dict:
        return self.client.delete(
            f"/api/operations/behavior/{record_id}"
        )