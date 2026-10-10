"""خدمة الدرجات + الشهادات + الأوائل."""

import logging
from typing import Dict, List, Optional

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class GradesApiService:
    def __init__(self, client: ApiClient):
        self.client = client

    # ============ Grades Page ============
    def get_sections_and_subjects(
        self, grade_id: int, academic_year_id: int
    ) -> Dict:
        return self.client.get(
            "/api/grades/sections-and-subjects",
            params={
                'grade_id': grade_id,
                'academic_year_id': academic_year_id,
            },
        )

    def get_students_and_scores(
        self,
        academic_year_id: int,
        grade_id: int,
        section_id: int,
        subject_id: int,
        term: int,
        month: Optional[int],
        is_monthly: bool,
    ) -> Dict:
        params = {
            'academic_year_id': academic_year_id,
            'grade_id': grade_id,
            'section_id': section_id,
            'subject_id': subject_id,
            'term': term,
            'is_monthly': 'true' if is_monthly else 'false',
        }
        if is_monthly and month is not None:
            params['month'] = month
        return self.client.get(
            "/api/grades/students-scores", params=params
        )

    def save_grades(self, payload: Dict) -> Dict:
        return self.client.post("/api/grades/save", json=payload)

    # ============ Certificates Page ============
    def get_certificate(
        self,
        student_id: int,
        academic_year_id: int,
        cert_type: str,
        term: int = 1,
        month: int = 1,
    ) -> Dict:
        return self.client.get(
            f"/api/grades/certificate/{student_id}",
            params={
                'academic_year_id': academic_year_id,
                'cert_type': cert_type,
                'term': term,
                'month': month,
            },
        )

    # ============ Top Students Page ============
    def get_top_students(
        self,
        academic_year_id: int,
        report_type: str,
        grade_id: Optional[int] = None,
        term: int = 1,
        month: int = 1,
    ) -> List[Dict]:
        params = {
            'academic_year_id': academic_year_id,
            'report_type': report_type,
            'term': term,
            'month': month,
        }
        if grade_id is not None:
            params['grade_id'] = grade_id
        return self.client.get(
            "/api/grades/top-students", params=params
        )