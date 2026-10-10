"""
إدارة الاتصال بقاعدة البيانات PostgreSQL.
يدعم الاتصال المحلي والسحابي.
"""

import os
import logging
from contextlib import contextmanager
from typing import Generator, Optional
from urllib.parse import quote_plus

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool

from app.core.config import config_manager, DatabaseConfig
from app.core.exceptions import DatabaseConnectionError
from .models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """مدير قاعدة البيانات."""
    
    _instance: Optional['DatabaseManager'] = None
    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None
    _scoped_session: Optional[scoped_session] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.config = config_manager.database_config
        self._is_initialized = False
        self._is_connected = False
        self._is_cloud = False
    
    def _build_connection_string(self, use_cloud: bool = False) -> str:
        """بناء سلسلة الاتصال."""
        if use_cloud:
            host = self.config.cloud_host
            port = self.config.cloud_port
            db_name = self.config.cloud_db_name
            user = self.config.cloud_user
            password = self.config.cloud_password
        else:
            host = self.config.local_host
            port = self.config.local_port
            db_name = self.config.local_db_name
            user = self.config.local_user
            password = self.config.local_password
        
        encoded_password = quote_plus(password)
        
        return (
            f"postgresql+psycopg2://{user}:{encoded_password}"
            f"@{host}:{port}/{db_name}"
        )
    
    def initialize(self, use_cloud: bool = False) -> None:
        """تهيئة محرك قاعدة البيانات."""
        if self._is_initialized:
            return
        
        try:
            connection_string = self._build_connection_string(use_cloud)
            logger.info(f"محاولة الاتصال بـ: {'السحابة' if use_cloud else 'الجهاز المحلي'}")

            if use_cloud:
                # إعدادات محسّنة للاتصال السحابي
                self._engine = create_engine(
                    connection_string,
                    poolclass=QueuePool,
                    pool_size=5,              # عدد اتصالات أقل
                    max_overflow=10,
                    pool_pre_ping=True,
                    pool_recycle=600,         # إعادة التدوير كل 10 دقائق
                    pool_timeout=30,
                    echo=False,
                    connect_args={
                        'connect_timeout': 30,
                        'application_name': 'SchoolManagementSystem',
                        'sslmode': self.config.cloud_sslmode,
                        # Keepalive للاتصال
                        'keepalives': 1,
                        'keepalives_idle': 30,
                        'keepalives_interval': 10,
                        'keepalives_count': 5,
                        # Timeouts للاستعلامات
                        'options': '-c statement_timeout=60000'
                    }
                )
            else:
                # الإعدادات المحلية (كما هي)
                self._engine = create_engine(
                    connection_string,
                    poolclass=QueuePool,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    echo=self.config.echo,
                    connect_args={
                        'connect_timeout': 10,
                        'application_name': 'SchoolManagementSystem',
                    }
                )
            # إضافة SSL للاتصال السحابي
            
            self._setup_engine_events()
            
            self._session_factory = sessionmaker(
                bind=self._engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
                class_=Session
            )
            
            self._scoped_session = scoped_session(self._session_factory)
            self._is_initialized = True
            self._is_cloud = use_cloud
            
            logger.info(f"تم تهيئة قاعدة البيانات ({'سحابية' if use_cloud else 'محلية'}) بنجاح")
            
        except Exception as e:
            logger.error(f"فشل تهيئة قاعدة البيانات: {str(e)}")
            raise DatabaseConnectionError(f"فشل الاتصال بقاعدة البيانات: {str(e)}")
    
    def _setup_engine_events(self) -> None:
        """إعداد مستمعين للأحداث."""
        @event.listens_for(self._engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            self._is_connected = True
        
        @event.listens_for(self._engine, "close")
        def receive_close(dbapi_connection, connection_record):
            self._is_connected = False
    
    @property
    def session(self) -> Session:
        if not self._is_initialized or self._scoped_session is None:
            raise DatabaseConnectionError("قاعدة البيانات غير مهيأة")
        return self._scoped_session()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        session = self.session
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_all_tables(self) -> None:
        if self._engine is None:
            raise DatabaseConnectionError("محرك قاعدة البيانات غير مهيأ")
        from . import models
        Base.metadata.create_all(self._engine)
    
    def check_connection(self) -> bool:
        """فحص الاتصال."""
        if self._engine is None:
            return False
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                conn.commit()
            self._is_connected = True
            return True
        except Exception as e:
            logger.error(f"فشل الاتصال: {str(e)}")
            self._is_connected = False
            return False
    
    def check_cloud_connection(self) -> bool:
        """فحص الاتصال بالخادم السحابي."""
        if not self.config.cloud_host:
            return False
        
        try:
            from sqlalchemy import create_engine
            temp_engine = create_engine(
                self._build_connection_string(use_cloud=True),
                connect_args={
                    'connect_timeout': 5,
                    'sslmode': self.config.cloud_sslmode,
                }
            )
            with temp_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            temp_engine.dispose()
            return True
        except Exception as e:
            logger.debug(f"لا يمكن الاتصال بالسحابة: {str(e)}")
            return False
    
    def close(self) -> None:
        if self._scoped_session:
            self._scoped_session.remove()
        if self._engine:
            self._engine.dispose()
            self._engine = None
        self._is_initialized = False
        self._is_connected = False
    
    @property
    def is_connected(self) -> bool:
        return self._is_connected
    
    @property
    def is_cloud(self) -> bool:
        return self._is_cloud
    
    @property
    def engine(self) -> Optional[Engine]:
        return self._engine


db_manager = DatabaseManager()