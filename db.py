# ============================================================
#  db.py — All PostgreSQL Database Operations
# ============================================================

import psycopg2
import psycopg2.extras
import bcrypt
from db_config import DB_CONFIG


# ------------------------------------------------------------------
# Connection
# ------------------------------------------------------------------

def get_connection():
    """Return a fresh psycopg2 connection using DB_CONFIG."""
    return psycopg2.connect(**DB_CONFIG)


# ------------------------------------------------------------------
# Initialization
# ------------------------------------------------------------------

def initialize_db():
    """
    Create all tables if they don't exist and seed the default
    admin account (username: admin, password: admin123).
    """
    conn = get_connection()
    cur  = conn.cursor()

    # ── users ──────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         SERIAL PRIMARY KEY,
            username   VARCHAR(50) UNIQUE NOT NULL,
            password   VARCHAR(255) NOT NULL,
            role       VARCHAR(10)  NOT NULL DEFAULT 'user',
            status     VARCHAR(20)  NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'pending'")

    # ── encryption_keys ───────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS encryption_keys (
            id         SERIAL PRIMARY KEY,
            user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
            key_name   VARCHAR(100) NOT NULL,
            algorithm  VARCHAR(20)  NOT NULL,
            key_data   BYTEA        NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # ── activity_logs ─────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id          SERIAL PRIMARY KEY,
            user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
            action      VARCHAR(20) NOT NULL,
            algorithm   VARCHAR(20) NOT NULL,
            key_id      INTEGER REFERENCES encryption_keys(id) ON DELETE SET NULL,
            source_file TEXT,
            output_file TEXT,
            status      VARCHAR(20) DEFAULT 'success',
            timestamp   TIMESTAMP  DEFAULT NOW()
        )
    """)

    # ── seed admin ────────────────────────────────────────────────
    cur.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cur.fetchone():
        hashed = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode()
        cur.execute(
            "INSERT INTO users (username, password, role, status) VALUES (%s, %s, %s, %s)",
            ('admin', hashed, 'admin', 'approved')
        )
    else:
        cur.execute("UPDATE users SET status = 'approved' WHERE username = 'admin'")

    conn.commit()
    cur.close()
    conn.close()


# ------------------------------------------------------------------
# User Operations
# ------------------------------------------------------------------

def create_user(username, hashed_password, role='user'):
    """
    Insert a new user. Returns the new user's id, or None if the
    username already exists.
    """
    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password, role) "
            "VALUES (%s, %s, %s) RETURNING id",
            (username, hashed_password, role)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    except psycopg2.IntegrityError:
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()


def get_user_by_username(username):
    """Return a dict for the user, or None if not found."""
    conn = get_connection()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None


def get_all_users():
    """Return list of all non-admin users (for Admin dashboard)."""
    conn = get_connection()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        "SELECT id, username, role, status, created_at FROM users "
        "WHERE role != 'admin' ORDER BY created_at DESC"
    )
    users = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return users


def approve_user(user_id):
    """Approve a pending user."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("UPDATE users SET status = 'approved' WHERE id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()


def reject_user(user_id):
    """Reject a pending user."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("UPDATE users SET status = 'rejected' WHERE id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()


def delete_user(user_id):
    """Delete a user by their id. Cascades to keys and activity logs."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()


# ------------------------------------------------------------------
# Encryption Key Operations
# ------------------------------------------------------------------

def save_key(user_id, key_name, algorithm, key_data: bytes):
    """Save an encryption key to the database. Returns the new key id."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO encryption_keys (user_id, key_name, algorithm, key_data) "
        "VALUES (%s, %s, %s, %s) RETURNING id",
        (user_id, key_name, algorithm, psycopg2.Binary(key_data))
    )
    key_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return key_id


def get_user_keys(user_id):
    """Return all keys belonging to a user as a list of dicts."""
    conn = get_connection()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        "SELECT id, key_name, algorithm, key_data, created_at "
        "FROM encryption_keys WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    keys = []
    for row in cur.fetchall():
        d = dict(row)
        d['key_data'] = bytes(d['key_data'])   # memoryview → bytes
        keys.append(d)
    cur.close()
    conn.close()
    return keys


def delete_key(key_id, user_id):
    """Delete a key — only if it belongs to the given user."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "DELETE FROM encryption_keys WHERE id = %s AND user_id = %s",
        (key_id, user_id)
    )
    conn.commit()
    cur.close()
    conn.close()


# ------------------------------------------------------------------
# Activity Log Operations
# ------------------------------------------------------------------

def log_activity(user_id, action, algorithm, key_id,
                 source_file, output_file, status='success'):
    """Insert one activity log entry."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO activity_logs "
        "(user_id, action, algorithm, key_id, source_file, output_file, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (user_id, action, algorithm, key_id, source_file, output_file, status)
    )
    conn.commit()
    cur.close()
    conn.close()


def get_all_activity_logs():
    """Return all activity logs joined with username (for Admin)."""
    conn = get_connection()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT al.id,
               u.username,
               al.action,
               al.algorithm,
               al.source_file,
               al.output_file,
               al.status,
               al.timestamp
        FROM   activity_logs al
        JOIN   users u ON al.user_id = u.id
        ORDER  BY al.timestamp DESC
    """)
    logs = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return logs


def get_user_activity_logs(user_id):
    """Return activity logs for a single user."""
    conn = get_connection()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT al.id,
               al.action,
               al.algorithm,
               al.source_file,
               al.output_file,
               al.status,
               al.timestamp
        FROM   activity_logs al
        WHERE  al.user_id = %s
        ORDER  BY al.timestamp DESC
    """, (user_id,))
    logs = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return logs
