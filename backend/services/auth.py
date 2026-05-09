import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from config import settings
from database.models import User

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    return pwd_context.verify(password, stored_hash)


def create_access_token(email: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.TOKEN_TTL_SECONDS)
    payload = {
        "sub": email,
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, str]]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get("sub")
        if not email:
            return None
        return {"email": email}
    except JWTError:
        return None


def register_user(db: Session, email: str, password: str) -> User:
    normalized_email = email.strip().lower()
    
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")

    try:
        existing_user = db.query(User).filter(User.email == normalized_email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists.")

        user = User(email=normalized_email, password_hash=hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Database error during signup: {exc}")
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable",
        )


def authenticate_user(db: Session, email: str, password: str) -> User:
    normalized_email = email.strip().lower()
    try:
        user = db.query(User).filter(User.email == normalized_email).first()
        if not user:
            logger.warning(f"Login failed: User {normalized_email} not found.")
            raise HTTPException(status_code=401, detail="Invalid credentials.")
        
        if not verify_password(password, user.password_hash):
            logger.warning(f"Login failed: Incorrect password for {normalized_email}.")
            raise HTTPException(status_code=401, detail="Invalid credentials.")
            
        return user
    except SQLAlchemyError as exc:
        logger.error(f"Database error during authentication for {normalized_email}: {exc}")
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable",
        )
