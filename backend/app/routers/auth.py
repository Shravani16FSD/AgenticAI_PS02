from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import UserProfile
from ..schemas import UserProfileResponse
from ..auth import get_authenticated_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    user_id: str = Field(..., description="ID of the user to log in as (e.g., default_user, user_jordan_chen, user_priya_sharma, user_marcus_vance)")

class LoginResponse(BaseModel):
    token: str
    user: UserProfileResponse
    message: str

class LogoutResponse(BaseModel):
    message: str

class AvailableUserItem(BaseModel):
    id: str
    name: str
    target_career_id: Optional[str] = ""
    study_status: Optional[str] = ""
    primary_goal: Optional[str] = ""

@router.get("/users", response_model=List[AvailableUserItem])
def list_available_users(db: Session = Depends(get_db)):
    """List all seeded users available for login."""
    users = db.query(UserProfile).order_by(UserProfile.created_at.asc()).all()
    return [
        AvailableUserItem(
            id=u.id,
            name=u.name,
            target_career_id=u.target_career_id or "",
            study_status=u.study_status or "",
            primary_goal=u.primary_goal or ""
        )
        for u in users
    ]

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Log in as one of the registered users."""
    requested_id = request.user_id.strip()
    # Normalize friendly usernames to user_ids if needed
    name_map = {
        "alex": "default_user",
        "alex_morgan": "default_user",
        "jordan": "user_jordan_chen",
        "jordan_chen": "user_jordan_chen",
        "priya": "user_priya_sharma",
        "priya_sharma": "user_priya_sharma",
        "marcus": "user_marcus_vance",
        "marcus_vance": "user_marcus_vance"
    }
    user_id = name_map.get(requested_id.lower(), requested_id)

    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{requested_id}' not found. Available users: default_user, user_jordan_chen, user_priya_sharma, user_marcus_vance"
        )

    token = f"token_{user.id}"
    response.set_cookie(
        key="chapter_session_user",
        value=user.id,
        httponly=False,
        max_age=86400 * 30,
        samesite="lax"
    )

    return LoginResponse(
        token=token,
        user=user,
        message=f"Logged in successfully as {user.name}"
    )

@router.post("/logout", response_model=LogoutResponse)
def logout(response: Response):
    """Log out the current user session."""
    response.delete_cookie(key="chapter_session_user")
    return LogoutResponse(message="Logged out successfully")

@router.get("/me", response_model=UserProfileResponse)
def get_current_user(current_user: UserProfile = Depends(get_authenticated_user)):
    """Retrieve profile of currently authenticated user."""
    return current_user
