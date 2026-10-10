"""مصنع خدمة وثائق الطلاب."""

from app.services.auth_factory import AuthFactory


class StudentDocumentsFactory:
    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        if cls.is_remote():
            from app.api_client.services.student_documents_api import (
                StudentDocumentsApiService,
            )
            client = AuthFactory.get_api_client()
            return StudentDocumentsApiService(client)
        return None