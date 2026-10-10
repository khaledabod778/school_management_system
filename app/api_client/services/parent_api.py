"""
خدمة أولياء الأمور عبر Local API.
"""

import logging
from typing import List, Dict, Optional

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class ParentApiService:
    """واجهة خدمات أولياء الأمور."""

    def __init__(self, client: ApiClient):
        self.client = client

    def list_parents(self, search: Optional[str] = None) -> List[Dict]:
        """قائمة أولياء الأمور."""
        params = {}
        if search:
            params['search'] = search
        data = self.client.get("/api/parents/", params=params)
        return data.get('parents', [])

    def get(self, parent_id: int) -> Dict:
        """تفاصيل ولي أمر."""
        return self.client.get(f"/api/parents/{parent_id}")

    def create(self, data: Dict) -> Dict:
        """إضافة ولي أمر."""
        return self.client.post("/api/parents/", json=data)

    def update(self, parent_id: int, data: Dict) -> Dict:
        """تعديل ولي أمر."""
        return self.client.put(f"/api/parents/{parent_id}", json=data)

    def delete(self, parent_id: int) -> Dict:
        """حذف ولي أمر."""
        return self.client.delete(f"/api/parents/{parent_id}")