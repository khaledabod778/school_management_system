#!/usr/bin/env python3
"""
سكربت التشغيل الرئيسي.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_requirements():
    """فحص المتطلبات."""
    required = ['PyQt6', 'sqlalchemy', 'psycopg2', 'qtawesome', 'reportlab', 'fastapi']
    missing = []
    
    for module in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print("المتطلبات الناقصة:")
        for m in missing:
            print(f"  - {m}")
        print("\nتثبيت: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """الدالة الرئيسية."""
    if not check_requirements():
        sys.exit(1)
    
    from app.main import main as run_app
    return run_app()


if __name__ == "__main__":
    sys.exit(main())