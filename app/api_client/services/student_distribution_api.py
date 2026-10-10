"""خدمة توزيع الطلاب."""

import logging
from typing import Dict, List

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class StudentDistributionApiService:
    def __init__(self, client: ApiClient):
        self.client = client

    def distribute(self, student_ids: List[int], section_id: int) -> Dict:
        return self.client.post(
            "/api/students/distribute",
            json={
                'student_ids': student_ids,
                'section_id': section_id,
            },
        )