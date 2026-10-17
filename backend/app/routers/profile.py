from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import UserProfile
from ..schemas import UserProfileResponse, UserProfileUpdate
from ..auth import get_authenticated_user

router = APIRouter(prefix="/api/profile", tags=["Profile"])

@router.get("/users", response_model=List[UserProfileResponse])
def list_user_profiles(db: Session = Depends(get_db)):
    users = db.query(UserProfile).order_by(UserProfile.created_at.asc()).all()
    return users

@router.get("", response_model=UserProfileResponse)
def get_user_profile(
    user_id: Optional[str] = None,
    current_user: UserProfile = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    if user_id:
        user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not user:
            if user_id == "default_user":
                # Create default if missing
                user = UserProfile(
                    id=user_id,
                    name="Alex Morgan",
                    study_status="Third-year CS & HCI Student",
                    target_career_id="ai-product-engineer",
                    interests=["Human-Centered AI", "Web Architecture", "Design Systems"],
                    current_skills=["TypeScript", "React", "Basic Python"],
                    primary_goal="Secure a Summer 2027 AI Product Engineering Internship",
                    weekly_hours=8,
                    onboarding_completed=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                raise HTTPException(status_code=404, detail=f"User profile '{user_id}' not found")
        return user

@router.put("", response_model=UserProfileResponse)
def update_user_profile(
    updates: UserProfileUpdate,
    user_id: Optional[str] = None,
    current_user: UserProfile = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    target_user = db.query(UserProfile).filter(UserProfile.id == user_id).first() if user_id else current_user
    if not target_user:
        raise HTTPException(status_code=404, detail="User profile not found")

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(target_user, field, value)

    target_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(target_user)
    return target_user
