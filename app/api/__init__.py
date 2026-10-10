"""
حزمة API للتكامل المستقبلي.
"""

from .fastapi_app import app, run_server
from .sync_endpoints import router as sync_router

# تسجيل نقاط نهاية المزامنة
app.include_router(sync_router)

__all__ = ['app', 'run_server']