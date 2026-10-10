"""
إدارة جلسات قاعدة البيانات.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from .connection import db_manager


def get_session() -> Session:
    return db_manager.session


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    with db_manager.session_scope() as session:
        yield session


def init_database(use_local: bool = True) -> None:
    """
    تهيئة قاعدة البيانات.
    
    Args:
        use_local: True للاتصال المحلي، False للسحابي
    """
    db_manager.initialize(use_cloud=not use_local)


def create_tables() -> None:
    db_manager.create_all_tables()


def close_database() -> None:
    db_manager.close()


def check_cloud_connection() -> bool:
    """فحص الاتصال بالسحابة."""
    return db_manager.check_cloud_connection()