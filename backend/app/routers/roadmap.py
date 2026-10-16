import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import RoadmapTask
from ..schemas import RoadmapTaskResponse, RoadmapTaskCreate, RoadmapTaskUpdate

router = APIRouter(prefix="/api/roadmap", tags=["Roadmap"])

@router.get("", response_model=List[RoadmapTaskResponse])
def get_roadmap_tasks(user_id: str = "default_user", db: Session = Depends(get_db)):
    tasks = db.query(RoadmapTask).filter(
        RoadmapTask.user_id == user_id
    ).order_by(RoadmapTask.phase_id.asc(), RoadmapTask.created_at.asc()).all()
    return tasks

@router.post("/tasks", response_model=RoadmapTaskResponse, status_code=status.HTTP_201_CREATED)
def create_roadmap_task(
    task_in: RoadmapTaskCreate,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    new_task = RoadmapTask(
        id=f"task-{uuid.uuid4().hex[:8]}",
        user_id=user_id,
        phase_id=task_in.phase_id,
        phase_name=task_in.phase_name,
        title=task_in.title,
        description=task_in.description,
        skill=task_in.skill,
        estimated_time=task_in.estimated_time,
        status=task_in.status or "not_started",
        resource_name=task_in.resource_name,
        resource_type=task_in.resource_type,
        resource_url=task_in.resource_url,
        notes=task_in.notes
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.patch("/tasks/{task_id}", response_model=RoadmapTaskResponse)
def update_roadmap_task(
    task_id: str,
    updates: RoadmapTaskUpdate,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    task = db.query(RoadmapTask).filter(
        RoadmapTask.id == task_id,
        RoadmapTask.user_id == user_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = updates.model_dump(exclude_unset=True)
    if "status" in update_data:
        task.status = update_data["status"]
        if task.status == "completed":
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None

    for field in ["title", "description", "skill", "estimated_time", "resource_name", "resource_url", "notes"]:
        if field in update_data:
            setattr(task, field, update_data[field])

    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task

@router.delete("/tasks/{task_id}")
def delete_roadmap_task(
    task_id: str,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    task = db.query(RoadmapTask).filter(
        RoadmapTask.id == task_id,
        RoadmapTask.user_id == user_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully", "task_id": task_id}
