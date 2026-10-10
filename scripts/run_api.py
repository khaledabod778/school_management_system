"""
سكربت تشغيل واجهة API.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn
from app.api.fastapi_app import app


def main():
    """تشغيل خادم API."""
    print("=" * 60)
    print("تشغيل واجهة API لنظام إدارة المدرسة")
    print("=" * 60)
    print("\nالمستندات متاحة على:")
    print("  - Swagger UI: http://localhost:8000/api/docs")
    print("  - ReDoc: http://localhost:8000/api/redoc")
    print("\nنقاط النهاية الرئيسية:")
    print("  - POST /api/auth/login - تسجيل الدخول")
    print("  - GET /api/students - قائمة الطلاب")
    print("  - GET /api/attendance/{id} - سجل الحضور")
    print("  - GET /api/homeworks/{id} - الواجبات")
    print("  - GET /api/grades/{id} - الدرجات")
    print("  - GET /api/fees/{id} - الرسوم")
    print("  - GET /api/notifications - الإشعارات")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()