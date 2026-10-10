"""
إنشاء جدول عمليات المزامنة.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text
from app.database.connection import db_manager
from app.database.session import init_database


def create_sync_operations_table():
    """إنشاء جدول عمليات المزامنة."""
    print("إنشاء جدول عمليات المزامنة...")
    
    init_database(use_local=True)
    
    with db_manager.engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sync_operations (
                id SERIAL PRIMARY KEY,
                entity_type VARCHAR(50) NOT NULL,
                entity_id INTEGER NOT NULL,
                operation_type VARCHAR(20) NOT NULL,
                data_json TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                retry_count INTEGER DEFAULT 0,
                user_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced_at TIMESTAMP,
                error_message TEXT
            )
        """))
        conn.commit()
    
    print("✓ تم إنشاء جدول عمليات المزامنة")


if __name__ == "__main__":
    create_sync_operations_table()