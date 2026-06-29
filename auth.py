import hashlib
import os
from models.database import get_connection


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a random salt."""
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a plaintext password against a stored salt:hash string."""
    try:
        salt, hashed = stored_hash.split(":", 1)
        return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
    except Exception:
        return False


def register_admin(full_name: str, email: str, username: str, password: str) -> dict:
    """
    Register a new admin account.
    Returns {'success': True} or {'success': False, 'error': '...'}.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Check uniqueness
        cursor.execute("SELECT id FROM admins WHERE username = ? OR email = ?", (username, email))
        existing = cursor.fetchone()
        if existing:
            return {"success": False, "error": "Username or email already exists."}

        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO admins (full_name, email, username, password_hash) VALUES (?, ?, ?, ?)",
            (full_name, email, username, password_hash),
        )
        conn.commit()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def login_admin(username: str, password: str) -> dict:
    """
    Validate login credentials.
    Returns {'success': True, 'admin': {...}} or {'success': False, 'error': '...'}.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
        admin = cursor.fetchone()
        if not admin:
            return {"success": False, "error": "Invalid username or password."}
        if not verify_password(password, admin["password_hash"]):
            return {"success": False, "error": "Invalid username or password."}
        return {
            "success": True,
            "admin": {
                "id": admin["id"],
                "full_name": admin["full_name"],
                "email": admin["email"],
                "username": admin["username"],
            },
        }
    finally:
        conn.close()


def get_admin_by_id(admin_id: int) -> dict | None:
    """Fetch an admin record by primary key."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email, username FROM admins WHERE id = ?", (admin_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
