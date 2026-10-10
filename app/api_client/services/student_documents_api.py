"""خدمة وثائق الطلاب."""

import logging
from pathlib import Path
from typing import Dict, List

from app.api_client.client import ApiClient

logger = logging.getLogger(__name__)


class StudentDocumentsApiService:
    def __init__(self, client: ApiClient):
        self.client = client

    def list_documents(self, student_id: int) -> List[Dict]:
        return self.client.get(
            f"/api/student-documents/student/{student_id}"
        )

    def upload_document(
        self,
        student_id: int,
        document_type: str,
        file_path: str,
    ) -> Dict:
        """رفع وثيقة."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"الملف غير موجود: {file_path}")

        with p.open('rb') as f:
            files = {
                'file': (p.name, f, 'application/octet-stream'),
            }
            return self.client.post_multipart(
                f"/api/student-documents/student/{student_id}",
                files=files,
                data={'document_type': document_type},
            )

    def download_document(
        self,
        doc_id: int,
        save_path: str,
    ) -> bool:
        """تنزيل وثيقة."""
        return self.client.download_file(
            f"/api/student-documents/{doc_id}/download",
            save_path,
        )

    def delete_document(self, doc_id: int) -> Dict:
        return self.client.delete(f"/api/student-documents/{doc_id}")