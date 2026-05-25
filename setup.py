# ============================================================
#  setup.py — One-time database setup script
#  Run this ONCE before launching main.py
# ============================================================

import sys
import psycopg2
from db_config import DB_CONFIG


def create_database():
    """Create the 'file_encryptor' database if it doesn't exist."""
    # Connect to the default 'postgres' database first
    cfg = dict(DB_CONFIG)
    target_db = cfg.pop('dbname')
    cfg['dbname'] = 'postgres'

    try:
        conn = psycopg2.connect(**cfg)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
        if cur.fetchone():
            print(f"[OK] Database '{target_db}' already exists.")
        else:
            cur.execute(f'CREATE DATABASE "{target_db}"')
            print(f"[OK] Database '{target_db}' created successfully.")

        cur.close()
        conn.close()
    except psycopg2.OperationalError as e:
        print(f"[ERROR] Cannot connect to PostgreSQL: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure PostgreSQL service is running.")
        print("  2. Open db_config.py and set the correct password.")
        sys.exit(1)


def create_tables_and_seed():
    """Create all tables and seed the admin account."""
    import db
    try:
        db.initialize_db()
        print("[OK] Tables created (users, encryption_keys, activity_logs).")
        print("[OK] Default admin account seeded: username=admin  password=admin123")
    except Exception as e:
        print(f"[ERROR] Table setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 55)
    print("  SecureVault — Database Setup")
    print("=" * 55)
    print()
    create_database()
    create_tables_and_seed()
    print()
    print("=" * 55)
    print("  Setup complete!  Run:  python main.py")
    print("=" * 55)
