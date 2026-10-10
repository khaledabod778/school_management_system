"""خدمة الجداول الدراسية."""

import logging
from typing import Dict, List, Optional

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class SchedulesApiService:
    def __init__(self, client: ApiClient):
        self.client = client

    # ============ Subjects for grade (dialogs) ============
    def subjects_for_grade(
        self, grade_id: int, academic_year_id: int
    ) -> List[Dict]:
        return self.client.get(
            "/api/schedules/subjects-for-grade",
            params={
                'grade_id': grade_id,
                'academic_year_id': academic_year_id,
            },
        )

    # ============ Weekly ============
    def get_weekly(
        self, section_id: int, academic_year_id: int, term: int
    ) -> Dict:
        return self.client.get(
            "/api/schedules/weekly",
            params={
                'section_id': section_id,
                'academic_year_id': academic_year_id,
                'term': term,
            },
        )

    def save_weekly(self, payload: Dict) -> Dict:
        return self.client.post("/api/schedules/weekly", json=payload)

    # ============ Monthly Exam ============
    def get_monthly_exam(
        self,
        section_id: int,
        academic_year_id: int,
        term: int,
        month: int,
    ) -> List[Dict]:
        return self.client.get(
            "/api/schedules/monthly-exam",
            params={
                'section_id': section_id,
                'academic_year_id': academic_year_id,
                'term': term,
                'month': month,
            },
        )

    def save_monthly_exam(self, payload: Dict) -> Dict:
        return self.client.post(
            "/api/schedules/monthly-exam", json=payload
        )

    # ============ Final Exam ============
    def get_final_exam(
        self, grade_id: int, academic_year_id: int, term: int
    ) -> List[Dict]:
        return self.client.get(
            "/api/schedules/final-exam",
            params={
                'grade_id': grade_id,
                'academic_year_id': academic_year_id,
                'term': term,
            },
        )

    def save_final_exam(self, payload: Dict) -> Dict:
        return self.client.post(
            "/api/schedules/final-exam", json=payload
        )