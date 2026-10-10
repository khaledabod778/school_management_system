"""
خدمة لوحات التحكم عبر Local API.
"""

import logging
from typing import Dict

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class DashboardApiService:
    """خدمة لوحات التحكم."""

    def __init__(self, client: ApiClient):
        self.client = client

    def summary(self, academic_year_id: int) -> Dict:
        """بيانات لوحة التحكم الرئيسية."""
        return self.client.get(
            "/api/dashboard/summary",
            params={'academic_year_id': academic_year_id},
        )

    def accountant(self) -> Dict:
        """بيانات لوحة المحاسب."""
        return self.client.get("/api/dashboard/accountant")