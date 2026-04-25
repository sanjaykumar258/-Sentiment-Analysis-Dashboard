# components/auth.py — Simple local user authentication
# Users are stored in data/users.json with SHA-256 hashed passwords

import json
import hashlib
import os

USERS_FILE = "data/users.json"


def _hash_password(password: str) -> str:
    """Hash a password with SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def _load_users() -> dict:
    """Load users from JSON file."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def _save_users(users: dict):
    """Save users to JSON file."""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def signup(email: str, password: str, name: str = "", prehashed: bool = False) -> dict:
    """Create a new user. Returns {ok, msg, name}.

    Args:
        email: User's email address.
        password: Plain-text password OR already-hashed hex string.
        name: Optional display name.
        prehashed: If True, `password` is already a SHA-256 hex digest
                   (sent from the browser); skip double-hashing.
    """
    email = email.strip().lower()
    if not email or "@" not in email:
        return {"ok": False, "msg": "Invalid email address."}

    # Length check only applies to plain-text passwords
    if not prehashed and len(password) < 6:
        return {"ok": False, "msg": "Password must be at least 6 characters."}

    users = _load_users()
    if email in users:
        return {"ok": False, "msg": "This email is already registered. Try signing in."}

    hashed = password if prehashed else _hash_password(password)
    users[email] = {
        "name": name.strip() or email.split("@")[0],
        "password": hashed,
    }
    _save_users(users)
    return {"ok": True, "msg": "Account created!", "name": users[email]["name"]}


def signin(email: str, password: str, prehashed: bool = False) -> dict:
    """Validate user credentials. Returns {ok, msg, name}.

    Args:
        email: User's email address.
        password: Plain-text password OR already-hashed hex string.
        prehashed: If True, `password` is already a SHA-256 hex digest.
    """
    email = email.strip().lower()
    users = _load_users()

    if email not in users:
        return {"ok": False, "msg": "No account found with this email."}

    hashed = password if prehashed else _hash_password(password)
    if users[email]["password"] != hashed:
        return {"ok": False, "msg": "Incorrect password."}

    return {"ok": True, "msg": "Welcome back!", "name": users[email]["name"]}
