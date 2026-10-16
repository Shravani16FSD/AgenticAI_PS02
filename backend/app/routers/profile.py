from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import UserProfile
from ..schemas import UserProfileResponse, UserProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["Profile"])

@router.get("", response_model=UserProfileResponse)
def get_user_profile(user_id: str = "default_user", db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user:
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
    return user

@router.put("", response_model=UserProfileResponse)
def update_user_profile(
    updates: UserProfileUpdate,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user
