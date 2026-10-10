"""
عامل تهيئة قاعدة البيانات في الخلفية.
"""

import logging
from PyQt6.QtCore import QThread, pyqtSignal

from app.core.config import config_manager
from app.database.session import (
    init_database, create_tables, check_cloud_connection
)
from app.database.connection import db_manager

logger = logging.getLogger(__name__)


class DatabaseInitWorker(QThread):
    """
    عامل تهيئة قاعدة البيانات في الخلفية.
    
    ✅ لا يجمّد الواجهة أثناء التهيئة
    ✅ يرسل تحديثات الحالة عبر الإشارات
    """
    
    # ✅ إشارات
    status_changed = pyqtSignal(str, int)  # (message, progress)
    finished = pyqtSignal()                 # نجاح
    failed = pyqtSignal(str)                # فشل (رسالة الخطأ)
    
    def __init__(self):
        super().__init__()
        self.database_mode = "local"
        self.is_using_cloud = False
    
    def run(self):
        """تنفيذ التهيئة في الخلفية."""
        try:
            # ============ 1. قراءة الإعدادات ============
            self.status_changed.emit(
                "جاري قراءة الإعدادات...", 5
            )
            self.database_mode = config_manager.app_config.database_mode
            cloud_config = config_manager.database_config
            
            logger.info(f"وضع قاعدة البيانات: {self.database_mode}")
            
            # ============ 2. تهيئة حسب الوضع ============
            if self.database_mode == "cloud":
                if not self._init_cloud(cloud_config):
                    return  # failed تم إرسالها
                    
            elif self.database_mode == "hybrid":
                self._init_hybrid(cloud_config)
                
            else:  # local
                self._init_local()
            
            # ============ 3. فحص الاتصال ============
            self.status_changed.emit(
                "جاري فحص الاتصال...", 50
            )
            
            if not db_manager.check_connection():
                self.failed.emit(
                    "فشل الاتصال بقاعدة البيانات.\n"
                    "يرجى التحقق من إعدادات قاعدة البيانات."
                )
                return
            
            # ============ 4. إنشاء الجداول ============
            self.status_changed.emit(
                "جاري إنشاء الجداول...", 70
            )
            
            try:
                create_tables()
                logger.info("تم إنشاء/التحقق من الجداول")
            except Exception as e:
                logger.warning(f"تحذير في إنشاء الجداول: {str(e)}")
            
            # ============ 5. اكتمال ============
            self.status_changed.emit(
                "اكتملت التهيئة بنجاح", 100
            )
            
            mode_text = "السحابة" if self.is_using_cloud else "المحلي"
            logger.info(
                f"تمت تهيئة قاعدة البيانات بنجاح - الوضع: {mode_text}"
            )
            
            # ✅ إرسال إشارة النجاح
            self.finished.emit()
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة قاعدة البيانات: {str(e)}")
            self.failed.emit(str(e))
    
    # ============================================================
    # ✅ دوال مساعدة للتهيئة
    # ============================================================
    
    def _init_local(self):
        """تهيئة الوضع المحلي."""
        self.status_changed.emit(
            "الاتصال بقاعدة البيانات المحلية...", 20
        )
        
        try:
            init_database(use_local=True)
            self.is_using_cloud = False
            logger.info("تم الاتصال بقاعدة البيانات المحلية")
        except Exception as e:
            logger.error(f"فشل الاتصال بالقاعدة المحلية: {str(e)}")
            raise
    
    def _init_cloud(self, cloud_config) -> bool:
        """تهيئة الوضع السحابي. تُرجع True عند النجاح."""
        if not cloud_config.cloud_host:
            self.failed.emit(
                "وضع قاعدة البيانات 'cloud' مُفعّل لكن لم يتم تكوين "
                "الخادم السحابي.\n\n"
                "يرجى تحديث config.json بمعلومات الخادم السحابي "
                "أو تغيير الوضع إلى 'local'."
            )
            return False
        
        self.status_changed.emit(
            "جاري الاتصال بالخادم السحابي...", 20
        )
        
        try:
            init_database(use_local=False)
            self.is_using_cloud = True
            logger.info("تم الاتصال بالخادم السحابي")
            return True
        except Exception as e:
            logger.error(f"فشل الاتصال بالسحابة: {str(e)}")
            self.failed.emit(
                f"فشل الاتصال بالخادم السحابي:\n{str(e)}\n\n"
                "يرجى التحقق من الإعدادات واتصال الإنترنت."
            )
            return False
    
    def _init_hybrid(self, cloud_config):
        """تهيئة الوضع المختلط."""
        self.status_changed.emit(
            "محاولة الاتصال بالسحابة...", 15
        )
        
        cloud_available = False
        if cloud_config.cloud_host:
            try:
                cloud_available = check_cloud_connection()
            except Exception as e:
                logger.warning(f"تعذر فحص السحابة: {str(e)}")
        
        if cloud_available:
            self.status_changed.emit(
                "تم الاتصال بالسحابة - العمل على السحابة", 25
            )
            try:
                init_database(use_local=False)
                self.is_using_cloud = True
                logger.info("الوضع المختلط: تم الاتصال بالسحابة")
            except Exception as e:
                logger.error(f"فشل الاتصال بالسحابة: {str(e)}")
                # العودة إلى المحلي
                self._init_local()
        else:
            self.status_changed.emit(
                "تعذر الاتصال بالسحابة - العودة للمحلي", 25
            )
            self._init_local()