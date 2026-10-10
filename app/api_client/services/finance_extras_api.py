"""خدمة السندات + البدلات + السلف + الرواتب + كشف حساب الموظف."""

import logging
from typing import Dict, List, Optional

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class FinanceExtrasApiService:
    def __init__(self, client: ApiClient):
        self.client = client

    # ============ Expenses ============
    def list_expenses(self, academic_year_id: Optional[int] = None) -> Dict:
        params = {}
        if academic_year_id:
            params['academic_year_id'] = academic_year_id
        return self.client.get("/api/finance/expenses/", params=params)

    def get_expense(self, vid: int) -> Dict:
        return self.client.get(f"/api/finance/expenses/{vid}")

    def get_next_voucher_number(self) -> str:
        r = self.client.get("/api/finance/expenses/next-number")
        return r['voucher_number']

    def create_expense(self, payload: Dict) -> Dict:
        return self.client.post("/api/finance/expenses/", json=payload)

    def update_expense(self, vid: int, payload: Dict) -> Dict:
        return self.client.put(f"/api/finance/expenses/{vid}", json=payload)

    def cancel_expense(self, vid: int, reason: str) -> Dict:
        return self.client.post(
            f"/api/finance/expenses/{vid}/cancel",
            json={'reason': reason},
        )

    # ============ Allowances ============
    def list_allowances(self, academic_year_id: Optional[int] = None) -> List[Dict]:
        params = {}
        if academic_year_id:
            params['academic_year_id'] = academic_year_id
        return self.client.get("/api/finance/allowances/", params=params)

    def get_allowance(self, rid: int) -> Dict:
        return self.client.get(f"/api/finance/allowances/{rid}")

    def create_allowance(self, payload: Dict) -> Dict:
        return self.client.post("/api/finance/allowances/", json=payload)

    def update_allowance(self, rid: int, payload: Dict) -> Dict:
        return self.client.put(f"/api/finance/allowances/{rid}", json=payload)

    def delete_allowance(self, rid: int) -> Dict:
        return self.client.delete(f"/api/finance/allowances/{rid}")

    # ============ Loans ============
    def list_loans(self, academic_year_id: Optional[int] = None) -> Dict:
        params = {}
        if academic_year_id:
            params['academic_year_id'] = academic_year_id
        return self.client.get("/api/finance/loans/", params=params)

    def get_loan(self, lid: int) -> Dict:
        return self.client.get(f"/api/finance/loans/{lid}")

    def create_loan(self, payload: Dict) -> Dict:
        return self.client.post("/api/finance/loans/", json=payload)

    def update_loan(self, lid: int, payload: Dict) -> Dict:
        return self.client.put(f"/api/finance/loans/{lid}", json=payload)

    def delete_loan(self, lid: int) -> Dict:
        return self.client.delete(f"/api/finance/loans/{lid}")

    # ============ Payroll ============
    def list_payroll(self, month: int, year: int) -> Dict:
        return self.client.get("/api/finance/payroll/", params={
            'month': month, 'year': year,
        })

    def generate_payroll(self, month: int, year: int) -> Dict:
        return self.client.post(
            "/api/finance/payroll/generate",
            params={'month': month, 'year': year},
        )

    def pay_salary(self, payroll_id: int) -> Dict:
        return self.client.post(f"/api/finance/payroll/{payroll_id}/pay")

    # ============ Employee Statement ============
    def get_employee_statement(self, employee_id: int) -> Dict:
        return self.client.get(
            f"/api/finance/employee-statement/{employee_id}"
        )