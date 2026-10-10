"""
خدمة المزامنة في الخلفية - تعمل بشكل دوري.
"""

import logging
import threading
import time
from datetime import datetime, timedelta

from app.services.sync.sync_engine import SyncEngine
from app.services.sync.sync_queue_manager import SyncQueueManager
from app.database.session import session_scope

logger = logging.getLogger(__name__)


class BackgroundSyncService:
    """
    خدمة المزامنة في الخلفية.
    
    تعمل بشكل دوري لـ:
    1. فحص الاتصال بالسحابة
    2. مزامنة العمليات المعلقة
    3. تنظيف الطابور
    """
    
    def __init__(
        self,
        sync_interval: int = 60,  # ثواني بين كل مزامنة
        health_check_interval: int = 30,  # ثواني بين فحص الاتصال
        cleanup_interval: int = 3600,  # ثواني بين كل تنظيف
        enabled: bool = True
    ):
        self.sync_interval = sync_interval
        self.health_check_interval = health_check_interval
        self.cleanup_interval = cleanup_interval
        self.enabled = enabled
        
        self._running = False
        self._thread: threading.Thread = None
        self._stop_event = threading.Event()
        
        self.engine = SyncEngine()
        
        # إحصائيات
        self.stats = {
            'cycles_run': 0,
            'last_sync_at': None,
            'last_health_check_at': None,
            'total_pushed': 0,
            'total_pulled': 0,
            'total_conflicts': 0,
            'last_error': None,
        }
        
        # حالة الاتصال
        self.cloud_available = False
    
    def start(self):
        """بدء الخدمة."""
        if self._running:
            logger.warning("الخدمة قيد التشغيل بالفعل")
            return
        
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
            name="BackgroundSyncService"
        )
        self._thread.start()
        
        logger.info("تم بدء خدمة المزامنة في الخلفية")
    
    def stop(self, timeout: int = 10):
        """إيقاف الخدمة."""
        if not self._running:
            return
        
        logger.info("جاري إيقاف خدمة المزامنة...")
        self._running = False
        self._stop_event.set()
        
        if self._thread:
            self._thread.join(timeout=timeout)
        
        logger.info("تم إيقاف خدمة المزامنة")
    
    def _run_loop(self):
        """الحلقة الرئيسية للخدمة."""
        last_sync = 0
        last_health = 0
        last_cleanup = 0
        
        while self._running and not self._stop_event.is_set():
            try:
                now = time.time()
                
                # 1. فحص الاتصال بشكل دوري
                if now - last_health >= self.health_check_interval:
                    self._check_health()
                    last_health = now
                
                # 2. المزامنة إذا كان الاتصال متاحاً
                if self.cloud_available and now - last_sync >= self.sync_interval:
                    self._run_sync_cycle()
                    last_sync = now
                
                # 3. تنظيف الطابور بشكل دوري
                if now - last_cleanup >= self.cleanup_interval:
                    self._cleanup()
                    last_cleanup = now
                
                # انتظار قصير
                self._stop_event.wait(5)
                
            except Exception as e:
                logger.error(f"خطأ في الحلقة الرئيسية: {str(e)}")
                self.stats['last_error'] = str(e)
                self._stop_event.wait(30)
    
    def _check_health(self):
        """فحص صحة الاتصال بالسحابة."""
        try:
            previous = self.cloud_available
            self.cloud_available = self.engine.check_cloud_health()
            self.stats['last_health_check_at'] = datetime.now()
            
            if self.cloud_available != previous:
                status = "متاح ✓" if self.cloud_available else "غير متاح ✗"
                logger.info(f"حالة السحابة: {status}")
        
        except Exception as e:
            logger.error(f"فشل فحص الصحة: {str(e)}")
            self.cloud_available = False
    
    def _run_sync_cycle(self):
        """تشغيل دورة مزامنة واحدة."""
        try:
            logger.info(
                f"🔄 بدء دورة مزامنة | "
                f"Cloud: {self.cloud_available} | "
                f"Last sync: {self.stats['last_sync_at']}"
            )            
            results = self.engine.full_sync()
            
            self.stats['cycles_run'] += 1
            self.stats['last_sync_at'] = datetime.now()
            self.stats['total_pushed'] += results['push']['pushed']
            self.stats['total_pulled'] += results['pull']['applied']
            self.stats['total_conflicts'] += results['push']['conflicts']
            
            logger.info(
                f"✓ دورة اكتملت: "
                f"pushed={results['push']['pushed']}, "
                f"pulled={results['pull']['applied']}, "
                f"conflicts={results['push']['conflicts']}"
            )
        
        except Exception as e:
            logger.error(f"فشل دورة المزامنة: {str(e)}")
            self.stats['last_error'] = str(e)
    
    def _cleanup(self):
        """تنظيف الطابور من العمليات المتزامنة القديمة."""
        try:
            with session_scope() as session:
                count = SyncQueueManager.cleanup_synced(session, older_than_days=7)
                if count > 0:
                    logger.info(f"تم تنظيف {count} عملية متزامنة قديمة")
        except Exception as e:
            logger.error(f"فشل التنظيف: {str(e)}")
    
    def force_sync(self):
        """فرض مزامنة فورية."""
        if not self.cloud_available:
            logger.warning("السحابة غير متاحة")
            return None
        
        logger.info("فرض مزامنة فورية...")
        return self.engine.full_sync()
    
    def get_status(self) -> dict:
        """الحصول على حالة الخدمة."""
        return {
            'running': self._running,
            'cloud_available': self.cloud_available,
            'stats': self.stats,
            'config': {
                'sync_interval': self.sync_interval,
                'health_check_interval': self.health_check_interval,
            }
        }