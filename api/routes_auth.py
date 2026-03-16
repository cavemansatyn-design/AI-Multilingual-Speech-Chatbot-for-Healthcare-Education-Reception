"""
Authentication: register, login, JWT.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import get_config, get_db_client
from app.config import Settings
from database.mongodb_client import MongoDBClient
from models.user_model import UserCreate, UserResponse, Token
from services.security_service import get_password_hash, verify_password, create_access_token

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(
    user_in: UserCreate,
    config: Settings = Depends(get_config),
    db: MongoDBClient = Depends(get_db_client),
):
    """Register a new user (user role by default)."""
    if db.get_user_by_username(user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.get_user_by_email(user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(user_in.password)
    user_id = db.create_user(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed,
        role=user_in.role if user_in.role in ("user", "admin", "doctor") else "user",
        full_name=user_in.full_name,
    )
    doc = db.get_user_by_username(user_in.username)
    return UserResponse(
        id=user_id,
        username=doc["username"],
        email=doc["email"],
        full_name=doc.get("full_name"),
        role=doc.get("role", "user"),
        disabled=doc.get("disabled", False),
    )


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    config: Settings = Depends(get_config),
    db: MongoDBClient = Depends(get_db_client),
):
    """Login with form body: username, password. Returns JWT."""
    user_doc = db.get_user_by_username(form_data.username)
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not verify_password(form_data.password, user_doc["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if user_doc.get("disabled"):
        raise HTTPException(status_code=400, detail="User disabled")
    token = create_access_token(
        data={"sub": user_doc["username"], "role": user_doc.get("role", "user")},
        secret_key=config.secret_key,
        algorithm=config.algorithm,
        expire_minutes=config.access_token_expire_minutes,
    )
    return Token(access_token=token, token_type="bearer")
