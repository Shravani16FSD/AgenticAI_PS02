import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import UserSkill
from ..schemas import UserSkillResponse, UserSkillCreate, LogPracticeRequest

router = APIRouter(prefix="/api/skills", tags=["Skills"])

@router.get("", response_model=List[UserSkillResponse])
def get_user_skills(user_id: str = "default_user", db: Session = Depends(get_db)):
    skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    return skills

@router.post("", response_model=UserSkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_in: UserSkillCreate,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    new_skill = UserSkill(
        id=f"skill-{uuid.uuid4().hex[:8]}",
        user_id=user_id,
        name=skill_in.name,
        category=skill_in.category or "General",
        status=skill_in.status or "learning",
        hours_spent=skill_in.hours_spent,
        target_hours=skill_in.target_hours,
        last_practiced="Just added"
    )
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill

@router.post("/{skill_id}/log", response_model=UserSkillResponse)
def log_practice_hours(
    skill_id: str,
    log_in: LogPracticeRequest,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    skill = db.query(UserSkill).filter(
        UserSkill.id == skill_id,
        UserSkill.user_id == user_id
    ).first()

    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    skill.hours_spent += log_in.hours
    if skill.hours_spent >= skill.target_hours:
        skill.status = "proficient"
    elif skill.hours_spent >= (skill.target_hours * 0.4):
        skill.status = "practicing"
    else:
        skill.status = "learning"

    skill.last_practiced = "Today"
    skill.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(skill)
    return skill
