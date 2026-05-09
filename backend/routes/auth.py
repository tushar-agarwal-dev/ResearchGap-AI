from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from database.session import get_db
from database.models import User
from services import auth as auth_service
from models.auth import AuthRequest, LoginResponse
from routes.deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
def signup(payload: AuthRequest, db: Session = Depends(get_db)):
    logger.info(f"Signup attempt for email: {payload.email}")
    user = auth_service.register_user(db, payload.email, payload.password)
    logger.info(f"Signup successful for user: {user.id}")
    return {
        "message": "Signup successful",
        "user": {"id": user.id, "email": user.email}
    }


@router.post("/login", response_model=LoginResponse)
def login(payload: AuthRequest, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for email: {payload.email}")
    user = auth_service.authenticate_user(db, payload.email, payload.password)
    
    # Mandate: Delete previous documents on login (Fresh Session)
    from services import paper_service
    paper_service.delete_user_papers(user.id, db)
    
    token = auth_service.create_access_token(user.email)
    logger.info(f"Login successful for user: {user.id}")
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email},
    }


@router.post("/token")
def token_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    
    # Mandate: Delete previous documents on login (Fresh Session)
    from services import paper_service
    paper_service.delete_user_papers(user.id, db)
    
    access_token = auth_service.create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "data": {"id": current_user.id, "email": current_user.email},
        "error": None
    }


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logs out user and clears all session data (papers) as per requirement."""
    from services import paper_service
    paper_service.delete_user_papers(current_user.id, db)
    return {
        "success": True,
        "message": "Logged out and user session data cleared."
    }
