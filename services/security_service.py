"""
Security: password hashing (bcrypt) and JWT authentication.
"""

from datetime import datetime, timedelta
from typing import Optional, List

import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel

from models.user_model import TokenData


def get_password_hash(password: str) -> str:
    """Hash password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(
    data: dict,
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: Optional[timedelta] = None,
    expire_minutes: int = 30,
) -> str:
    """
    Create JWT access token.

    Args:
        data: Payload (e.g. {"sub": username, "role": role}).
        secret_key: Secret for signing.
        algorithm: JWT algorithm.
        expires_delta: Override expiration.
        expire_minutes: Used if expires_delta not set.

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def decode_token(
    token: str,
    secret_key: str,
    algorithm: str = "HS256",
) -> Optional[TokenData]:
    """
    Decode JWT and return TokenData. Returns None if invalid.
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role")
        scopes: List[str] = payload.get("scopes", [])
        return TokenData(username=username, role=role, scopes=scopes)
    except JWTError:
        return None
