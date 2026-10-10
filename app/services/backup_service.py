"""
خدمة النسخ الاحتياطي التلقائي.

تُستخدم لحماية البيانات قبل عمليات خطيرة (Pull كبير، إلخ).
"""

import logging
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core.config import config_manager

logger = logging.getLogger(__name__)


class BackupService:
    """خدمة النسخ الاحتياطي."""

    MAX_BACKUPS = 10  # الحد الأقصى للاحتفاظ بالنسخ

    @classmethod
    def create_backup(
        cls,
        reason: str = "manual",
        include_db: bool = True,
    ) -> Optional[Path]:
        """
        إنشاء نسخة احتياطية.
        
        Args:
            reason: سبب النسخة (manual/pre_pull/pre_migration)
            include_db: تضمين نسخة من قاعدة البيانات
        
        Returns:
            مسار ملف النسخة (أو None عند الفشل)
        """
        try:
            backup_dir = cls._get_backup_dir()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{reason}_{timestamp}"
            backup_path = backup_dir / backup_name
            backup_path.mkdir(parents=True, exist_ok=True)

            # ✅ 1. نسخ config.json (مشفر بالكامل)
            config_file = Path("config.json")
            if config_file.exists():
                shutil.copy2(
                    config_file,
                    backup_path / "config.json"
                )

            # ✅ 2. نسخ master.key (حرج!)
            from app.core.secrets_manager import secrets_manager
            if secrets_manager.key_path.exists():
                shutil.copy2(
                    secrets_manager.key_path,
                    backup_path / "master.key"
                )

            # ✅ 3. dump قاعدة البيانات (إذا PostgreSQL محلي)
            if include_db:
                db_dump = cls._dump_local_db(backup_path)
                if not db_dump:
                    logger.warning(
                        "⚠️ فشل dump قاعدة البيانات - النسخة ستحتوي "
                        "الإعدادات فقط"
                    )

            # ✅ 4. metadata
            metadata = {
                'created_at': datetime.now().isoformat(),
                'reason': reason,
                'app_version': config_manager.app_config.app_version,
                'includes_db': include_db,
            }
            import json
            with open(backup_path / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            # ✅ 5. تنظيف النسخ القديمة
            cls._cleanup_old_backups(backup_dir)

            logger.info(f"✅ نسخة احتياطية: {backup_path}")
            return backup_path

        except Exception as e:
            logger.error(f"فشل النسخ الاحتياطي: {e}", exc_info=True)
            return None

    # ==================== DB Dump ====================

    @classmethod
    def _dump_local_db(cls, backup_path: Path) -> bool:
        """dump قاعدة البيانات المحلية (PostgreSQL)."""
        try:
            cfg = config_manager.database_config
            dump_file = backup_path / "database.dump"

            # ✅ استخدم pg_dump
            env = os.environ.copy()
            if cfg.local_password:
                env['PGPASSWORD'] = cfg.local_password

            cmd = [
                'pg_dump',
                '-h', cfg.local_host,
                '-p', str(cfg.local_port),
                '-U', cfg.local_user,
                '-d', cfg.local_db_name,
                '-F', 'c',  # custom format (مضغوط)
                '-f', str(dump_file),
            ]

            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300,  # 5 دقائق
            )

            if result.returncode != 0:
                logger.error(f"pg_dump فشل: {result.stderr[:500]}")
                return False

            logger.info(f"✅ DB dump: {dump_file.stat().st_size / 1024 / 1024:.1f} MB")
            return True

        except FileNotFoundError:
            logger.warning("pg_dump غير مثبّت - تخطي dump قاعدة البيانات")
            return False
        except Exception as e:
            logger.error(f"فشل dump: {e}")
            return False

    # ==================== Utilities ====================

    @classmethod
    def _get_backup_dir(cls) -> Path:
        """الحصول على مجلد النسخ."""
        cfg = config_manager.app_config.backup_directory
        backup_dir = Path(cfg)
        if not backup_dir.is_absolute():
            backup_dir = Path.cwd() / backup_dir
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir

    @classmethod
    def _cleanup_old_backups(cls, backup_dir: Path):
        """حذف النسخ القديمة (الاحتفاظ بـ MAX_BACKUPS)."""
        try:
            backups = sorted(
                [d for d in backup_dir.iterdir() if d.is_dir()],
                key=lambda d: d.stat().st_mtime,
                reverse=True,
            )

            for old in backups[cls.MAX_BACKUPS:]:
                shutil.rmtree(old, ignore_errors=True)
                logger.debug(f"حُذفت النسخة القديمة: {old.name}")

        except Exception as e:
            logger.warning(f"فشل تنظيف النسخ: {e}")

    @classmethod
    def list_backups(cls) -> list:
        """قائمة النسخ المتاحة."""
        try:
            backup_dir = cls._get_backup_dir()
            backups = []
            for d in sorted(
                backup_dir.iterdir(),
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            ):
                if not d.is_dir():
                    continue

                metadata = {}
                meta_file = d / "metadata.json"
                if meta_file.exists():
                    import json
                    try:
                        metadata = json.loads(meta_file.read_text('utf-8'))
                    except Exception:
                        pass

                size = sum(
                    f.stat().st_size for f in d.rglob('*') if f.is_file()
                )

                backups.append({
                    'name': d.name,
                    'path': str(d),
                    'size_mb': round(size / 1024 / 1024, 2),
                    'created_at': metadata.get('created_at'),
                    'reason': metadata.get('reason'),
                    'includes_db': metadata.get('includes_db', False),
                })
            return backups

        except Exception as e:
            logger.error(f"فشل قراءة النسخ: {e}")
            return []