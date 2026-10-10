"""مصنع خدمة أرشيف المطبوعات."""

from app.services.auth_factory import AuthFactory


class PrintArchiveFactory:
    @classmethod
    def is_remote(cls) -> bool:
        return AuthFactory.is_remote_mode()

    @classmethod
    def get_service(cls):
        if cls.is_remote():
            from app.api_client.services.print_archive_api import (
                PrintArchiveApiService,
            )
            client = AuthFactory.get_api_client()
            return PrintArchiveApiService(client)
        return None