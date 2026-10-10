"""
إعدادات التطبيق وقاعدة البيانات.

v2.0:
- تشفير تلقائي للحقول الحساسة (passwords, api keys)
- فك تشفير شفّاف عند القراءة
"""

import os
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from app.core.secrets_manager import secrets_manager


@dataclass
class DatabaseConfig:
    """إعدادات قاعدة البيانات."""

    # الإعدادات المحلية
    local_host: str = "localhost"
    local_port: int = 5432
    local_db_name: str = "school_management"
    local_user: str = "postgres"
    local_password: str = "postgres"

    # الإعدادات السحابية
    cloud_host: str = ""
    cloud_port: int = 5432
    cloud_db_name: str = "school_management"
    cloud_user: str = "postgres"
    cloud_password: str = ""
    cloud_sslmode: str = "require"

    cloud_api_url: str = ""
    cloud_api_key: str = ""

    # إعدادات عامة
    debug: bool = False
    echo: bool = False

    def to_dict(self, for_storage: bool = False) -> dict:
        """
        تحويل إلى dict.
        
        Args:
            for_storage: إذا True، شفّر الحقول الحساسة
        """
        data = asdict(self)
        if for_storage:
            data = secrets_manager.encrypt_dict(data)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'DatabaseConfig':
        """تحميل من dict مع فك تشفير الحقول الحساسة."""
        # ✅ فك التشفير أولاً
        data = secrets_manager.decrypt_dict(data)
        # ✅ فلترة المفاتيح غير المعروفة
        valid = cls.__dataclass_fields__.keys()
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class AppConfig:
    """إعدادات التطبيق العامة."""

    app_name: str = "نظام إدارة المدرسة"
    app_version: str = "1.0.0"
    language: str = "ar"
    theme: str = "light"
    font_family: str = "Cairo"
    font_size: int = 12

    sync_enabled: bool = True
    sync_interval: int = 60
    sync_auto_start: bool = True
    sync_health_check_interval: int = 30

    # ✅ جديد: حماية البيانات
    backup_before_pull: bool = True           # نسخة احتياطية قبل Pull كبير
    backup_threshold: int = 100               # عدد التغييرات لتفعيل النسخة
    compression_enabled: bool = True          # ضغط payloads

    backup_enabled: bool = True
    backup_interval: str = "daily"
    backup_directory: str = "backups"

    database_mode: str = "local"
    use_cloud_primary: bool = False

    # ✅ v3: إعدادات Local API
    api_mode: str = "local"  # local / remote / auto
    api_url: str = "http://192.168.1.100:8000"
    api_timeout: int = 30
    api_auto_login: bool = True

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'AppConfig':
        valid_keys = cls.__dataclass_fields__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)


class ConfigManager:
    """مدير الإعدادات."""

    _instance: Optional['ConfigManager'] = None
    _config_file = "config.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.app_config = AppConfig()
        self.database_config = DatabaseConfig()
        self._load_config()

    def _load_config(self) -> None:
        """تحميل الإعدادات من الملف."""
        config_path = Path(self._config_file)

        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if 'app' in data:
                    self.app_config = AppConfig.from_dict(data['app'])

                if 'database' in data:
                    self.database_config = DatabaseConfig.from_dict(
                        data['database']
                    )

                logging.info("✅ تم تحميل الإعدادات")
            except Exception as e:
                logging.error(f"فشل تحميل الإعدادات: {e}")
        else:
            self.save_config()

    def save_config(self) -> None:
        """حفظ الإعدادات (مع تشفير الحقول الحساسة)."""
        try:
            data = {
                'app': self.app_config.to_dict(),
                # ✅ شفّر الحقول الحساسة عند الكتابة
                'database': self.database_config.to_dict(for_storage=True),
            }

            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            logging.info("✅ تم حفظ الإعدادات (الحقول الحساسة مشفّرة)")
        except Exception as e:
            logging.error(f"فشل حفظ الإعدادات: {e}")

    def update_app_config(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self.app_config, key):
                setattr(self.app_config, key, value)
        self.save_config()

    def update_database_config(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self.database_config, key):
                setattr(self.database_config, key, value)
        self.save_config()


config_manager = ConfigManager()