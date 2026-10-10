"""خدمة سجل العمليات."""

import logging
from typing import Dict, Optional

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class AuditLogApiService:
    def __init__(self, client: ApiClient):
        self.client = client

    def list_logs(
        self,
        user_id: Optional[int] = None,
        operation: Optional[str] = None,
        module: Optional[str] = None,
        search: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 1000,
    ) -> Dict:
        params = {'limit': limit}
        if user_id:
            params['user_id'] = user_id
        if operation and operation != "جميع العمليات":
            params['operation'] = operation
        if module:
            params['module'] = module
        if search:
            params['search'] = search
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
        return self.client.get("/api/audit-log/", params=params)

    def get_log(self, log_id: int) -> Dict:
        return self.client.get(f"/api/audit-log/{log_id}")