# ============================================================
#  auth.py — Authentication: Signup, Login, Password Hashing
# ============================================================

import bcrypt
import db


def hash_password(password: str) -> str:
    """Return a bcrypt hash string for the given plain-text password."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the bcrypt hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def signup(username: str, password: str):
    """
    Validate and register a new user.

    Returns:
        (user_id, None)        on success
        (None,    error_msg)   on failure
    """
    username = username.strip()
    password = password.strip()

    if len(username) < 3:
        return None, "Username must be at least 3 characters."
    if not username.isalnum() and '_' not in username:
        return None, "Username may only contain letters, numbers, or underscores."
    if len(password) < 6:
        return None, "Password must be at least 6 characters."
    if username.lower() == 'admin':
        return None, "The username 'admin' is reserved."

    hashed  = hash_password(password)
    user_id = db.create_user(username, hashed, role='user')

    if user_id is None:
        return None, "Username already taken. Please choose another."

    return user_id, None


def login(username: str, password: str):
    """
    Validate credentials.

    Returns:
        (user_dict, None)      on success
        (None,      error_msg) on failure
    """
    username = username.strip()
    user     = db.get_user_by_username(username)

    if user is None:
        return None, "Username not found."
    if not verify_password(password, user['password']):
        return None, "Incorrect password."

    # Validate approval status for non-admin users
    if user['role'] != 'admin':
        status = user.get('status', 'pending')
        if status == 'pending':
            return None, "Your account is pending admin approval."
        elif status == 'rejected':
            return None, "Your account registration was rejected by the admin."

    return user, None
