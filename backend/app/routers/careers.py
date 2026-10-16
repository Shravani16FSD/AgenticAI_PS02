import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import CareerPath, SavedCareer
from ..schemas import CareerPathResponse

router = APIRouter(prefix="/api/careers", tags=["Careers"])

@router.get("", response_model=List[CareerPathResponse])
def get_all_careers(db: Session = Depends(get_db)):
    careers = db.query(CareerPath).all()
    return careers

@router.get("/saved", response_model=List[str])
def get_saved_career_ids(user_id: str = "default_user", db: Session = Depends(get_db)):
    saved = db.query(SavedCareer).filter(SavedCareer.user_id == user_id).all()
    return [s.career_id for s in saved]

@router.post("/{career_id}/save", status_code=status.HTTP_201_CREATED)
def save_career(career_id: str, user_id: str = "default_user", db: Session = Depends(get_db)):
    # Verify career exists
    career = db.query(CareerPath).filter(CareerPath.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career path not found")

    existing = db.query(SavedCareer).filter(
        SavedCareer.user_id == user_id,
        SavedCareer.career_id == career_id
    ).first()

    if not existing:
        new_save = SavedCareer(
            id=f"sc-{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            career_id=career_id
        )
        db.add(new_save)
        db.commit()

    return {"message": "Career saved successfully", "career_id": career_id}

@router.delete("/{career_id}/save")
def remove_saved_career(career_id: str, user_id: str = "default_user", db: Session = Depends(get_db)):
    existing = db.query(SavedCareer).filter(
        SavedCareer.user_id == user_id,
        SavedCareer.career_id == career_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()

    return {"message": "Career removed from saved list", "career_id": career_id}
