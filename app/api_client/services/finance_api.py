"""خدمة الرسوم + السندات + كشف الحساب."""

import logging
from typing import Dict, List, Optional

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class FinanceApiService:
    def __init__(self, client: ApiClient):
        self.client = client

    # ==================== Fees ====================
    def get_student_fees_data(self, student_id: int,
                              academic_year_id: int) -> Dict:
        return self.client.get(
            f"/api/finance/fees/student/{student_id}",
            params={'academic_year_id': academic_year_id},
        )

    def save_student_fees(self, student_id: int, academic_year_id: int,
                          payload: Dict) -> Dict:
        return self.client.post(
            f"/api/finance/fees/student/{student_id}",
            params={'academic_year_id': academic_year_id},
            json=payload,
        )

    # ==================== Receipts ====================
    def list_receipts(self, academic_year_id: Optional[int] = None,
                      search: Optional[str] = None,
                      status: Optional[str] = None) -> Dict:
        params = {}
        if academic_year_id:
            params['academic_year_id'] = academic_year_id
        if search:
            params['search'] = search
        if status and status != "جميع الحالات":
            params['status'] = status
        return self.client.get("/api/finance/receipts/", params=params)

    def get_receipt(self, receipt_id: int) -> Dict:
        return self.client.get(f"/api/finance/receipts/{receipt_id}")

    def get_next_receipt_number(self) -> str:
        r = self.client.get("/api/finance/receipts/next-number")
        return r['receipt_number']

    def create_receipt(self, payload: Dict) -> Dict:
        return self.client.post("/api/finance/receipts/", json=payload)

    def update_receipt(self, receipt_id: int, payload: Dict) -> Dict:
        return self.client.put(
            f"/api/finance/receipts/{receipt_id}", json=payload
        )

    def cancel_receipt(self, receipt_id: int, reason: str) -> Dict:
        return self.client.post(
            f"/api/finance/receipts/{receipt_id}/cancel",
            json={'reason': reason},
        )

    # ==================== Statement ====================
    def get_statement(self, student_id: int,
                      academic_year_id: int) -> Dict:
        return self.client.get(
            f"/api/finance/statement/student/{student_id}",
            params={'academic_year_id': academic_year_id},
        )