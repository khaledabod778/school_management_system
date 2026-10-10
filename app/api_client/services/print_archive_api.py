"""خدمة أرشيف المطبوعات."""

import logging
from typing import Dict, List

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class PrintArchiveApiService:
    def __init__(self, client: ApiClient):
        self.client = client

    def list_prints(self, limit: int = 1000) -> List[Dict]:
        return self.client.get(
            "/api/print-archive/", params={'limit': limit}
        )

    def get_print(self, print_id: int) -> Dict:
        return self.client.get(f"/api/print-archive/{print_id}")