"""خدمة التهيئة الأكاديمية عبر Local API."""

import logging
from typing import Dict, List, Optional

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class AcademicApiService:
    """كل عمليات التهيئة الأكاديمية."""

    def __init__(self, client: ApiClient):
        self.client = client

    # ==================== School Info ====================
    def get_school_info(self) -> Optional[Dict]:
        return self.client.get("/api/academic/school-info/")

    def update_school_info(self, data: Dict) -> Dict:
        return self.client.put("/api/academic/school-info/", json=data)

    # ==================== Academic Years ====================
    def list_years(self) -> List[Dict]:
        return self.client.get("/api/academic/academic-years/")

    def create_year(self, data: Dict) -> Dict:
        return self.client.post("/api/academic/academic-years/", json=data)

    def update_year(self, year_id: int, data: Dict) -> Dict:
        return self.client.put(f"/api/academic/academic-years/{year_id}", json=data)

    def set_current_year(self, year_id: int) -> Dict:
        return self.client.post(
            f"/api/academic/academic-years/{year_id}/set-current"
        )

    # ==================== Grades + Sections ====================
    def list_grades(self) -> List[Dict]:
        return self.client.get("/api/academic/grades/")

    def create_grade(self, data: Dict) -> Dict:
        return self.client.post("/api/academic/grades/", json=data)

    def update_grade(self, grade_id: int, data: Dict) -> Dict:
        return self.client.put(f"/api/academic/grades/{grade_id}", json=data)

    def delete_grade(self, grade_id: int) -> Dict:
        return self.client.delete(f"/api/academic/grades/{grade_id}")

    # ==================== Fee Structure ====================
    def list_fee_types(self) -> List[Dict]:
        return self.client.get("/api/academic/fee-types/")

    def list_fee_structures(self, academic_year_id: int) -> List[Dict]:
        return self.client.get(
            "/api/academic/fee-structures/",
            params={'academic_year_id': academic_year_id},
        )

    def create_fee_structure(self, data: Dict, academic_year_id: int) -> Dict:
        return self.client.post(
            "/api/academic/fee-structures/",
            params={'academic_year_id': academic_year_id},
            json=data,
        )

    def update_fee_structure(self, fee_id: int, data: Dict,
                             academic_year_id: int) -> Dict:
        return self.client.put(
            f"/api/academic/fee-structures/{fee_id}",
            params={'academic_year_id': academic_year_id},
            json=data,
        )

    def delete_fee_structure(self, fee_id: int) -> Dict:
        return self.client.delete(f"/api/academic/fee-structures/{fee_id}")

    # ==================== Subjects ====================
    def list_subjects(self) -> List[Dict]:
        return self.client.get("/api/academic/subjects/")

    def create_subject(self, data: Dict) -> Dict:
        return self.client.post("/api/academic/subjects/", json=data)

    def update_subject(self, sid: int, data: Dict) -> Dict:
        return self.client.put(f"/api/academic/subjects/{sid}", json=data)

    def delete_subject(self, sid: int) -> Dict:
        return self.client.delete(f"/api/academic/subjects/{sid}")

    # ==================== Teacher Assignments ====================
    def list_assignments(self, academic_year_id: int) -> List[Dict]:
        return self.client.get(
            "/api/academic/teacher-assignments/",
            params={'academic_year_id': academic_year_id},
        )

    def create_assignment(self, data: Dict) -> Dict:
        return self.client.post(
            "/api/academic/teacher-assignments/", json=data
        )

    def delete_assignment(self, aid: int) -> Dict:
        return self.client.delete(f"/api/academic/teacher-assignments/{aid}")

    def list_teachers(self) -> List[Dict]:
        return self.client.get("/api/academic/teachers/")