"""
خدمة الطلاب عبر Local API.
"""

import logging
from typing import List, Dict, Optional

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class StudentApiService:
    """واجهة خدمات الطلاب - موازية لـ StudentService المحلي."""

    def __init__(self, client: ApiClient):
        self.client = client

    # ==================== List ====================

    def list_students(
        self,
        academic_year_id: Optional[int] = None,
        search: Optional[str] = None,
        grade_id: Optional[int] = None,
        section_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Dict]:
        """جلب قائمة الطلاب."""
        params = {}
        if academic_year_id is not None:
            params['academic_year_id'] = academic_year_id
        if search:
            params['search'] = search
        if grade_id is not None:
            params['grade_id'] = grade_id
        if section_id is not None:
            params['section_id'] = section_id
        if status and status != 'جميع الحالات':
            params['status'] = status

        data = self.client.get("/api/students/", params=params)
        return data.get('students', [])

    def lookup(
        self,
        academic_year_id: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 30,
    ) -> List[Dict]:
        """قائمة مُبسطة."""
        params = {'limit': limit}
        if academic_year_id is not None:
            params['academic_year_id'] = academic_year_id
        if search:
            params['search'] = search
        return self.client.get("/api/students/lookup/", params=params)

    def get(self, student_id: int) -> Dict:
        """تفاصيل طالب."""
        return self.client.get(f"/api/students/{student_id}")

    # ==================== Write ====================

    def create(self, data: Dict) -> Dict:
        """إضافة طالب جديد."""
        return self.client.post("/api/students/", json=data)

    def update(self, student_id: int, data: Dict) -> Dict:
        """تعديل طالب."""
        return self.client.put(f"/api/students/{student_id}", json=data)

    def delete(self, student_id: int) -> Dict:
        """حذف طالب."""
        return self.client.delete(f"/api/students/{student_id}")

    # ==================== Lookups ====================

    def list_grades(self) -> List[Dict]:
        return self.client.get("/api/lookup/grades/")

    def list_sections(self, grade_id: Optional[int] = None) -> List[Dict]:
        params = {}
        if grade_id is not None:
            params['grade_id'] = grade_id
        return self.client.get("/api/lookup/sections/", params=params)

    def search_parents(self, search: str = "", limit: int = 20) -> List[Dict]:
        params = {'limit': limit}
        if search:
            params['search'] = search
        return self.client.get("/api/lookup/parents/", params=params)

    def list_academic_years(self) -> List[Dict]:
        return self.client.get("/api/lookup/academic-years-list/")