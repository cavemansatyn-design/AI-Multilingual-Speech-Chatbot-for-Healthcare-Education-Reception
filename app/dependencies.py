"""
FastAPI dependencies: auth, DB client, config.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer

from app.config import Settings, get_settings
from database.mongodb_client import MongoDBClient
from models.user_model import TokenData, UserInDB
from services.security_service import decode_token

# OAuth2PasswordBearer for login form; HTTPBearer for protected routes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)


def get_config() -> Settings:
    return get_settings()


def get_db_client() -> MongoDBClient:
    return MongoDBClient()


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    config: Settings = Depends(get_config),
    db: MongoDBClient = Depends(get_db_client),
) -> Optional[UserInDB]:
    """Return current user if valid Bearer token provided; else None."""
    if not credentials:
        return None
    token_data = decode_token(credentials.credentials, config.secret_key, config.algorithm)
    if not token_data or not token_data.username:
        return None
    user_doc = db.get_user_by_username(token_data.username)
    if not user_doc:
        return None
    return UserInDB(
        id=str(user_doc["_id"]),
        username=user_doc["username"],
        email=user_doc["email"],
        hashed_password=user_doc["hashed_password"],
        full_name=user_doc.get("full_name"),
        role=user_doc.get("role", "user"),
        disabled=user_doc.get("disabled", False),
    )


async def get_current_user(
    current_user: Optional[UserInDB] = Depends(get_current_user_optional),
) -> UserInDB:
    """Require authenticated user; raise 401 if not."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="User disabled")
    return current_user


def require_role(*allowed_roles: str):
    """Dependency factory: require user to have one of the given roles."""

    async def _require_role(
        current_user: UserInDB = Depends(get_current_user),
    ) -> UserInDB:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _require_role
