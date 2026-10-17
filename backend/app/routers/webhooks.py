"""
GitHub Webhook Router for SkillTrace AI.
Provides:
- POST /api/webhooks/github
- GET /api/webhooks/events
"""

from typing import List
from fastapi import APIRouter, Request, Header, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db, SessionLocal
from ..models import WebhookEvent
from ..schemas import WebhookResponse
from ..services.webhook_service import webhook_service

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


async def _run_async_reassessment(job_id: str, repo_full_name: str, commit_sha: str):
    """Background task runner to execute repository reassessment."""
    db = SessionLocal()
    try:
        await webhook_service.execute_background_reassessment(
            db=db,
            job_id=job_id,
            repo_full_name=repo_full_name,
            commit_sha=commit_sha
        )
    finally:
        db.close()


@router.post("/github", response_model=WebhookResponse)
async def receive_github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_delivery: str = Header(..., alias="X-GitHub-Delivery"),
    x_github_event: str = Header(..., alias="X-GitHub-Event"),
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256"),
    db: Session = Depends(get_db)
):
    """
    Receives GitHub webhook events (push, ping), validates HMAC-SHA256 signatures,
    enforces idempotency, and queues background reassessment jobs.
    """
    payload_bytes = await request.body()

    res = await webhook_service.process_webhook_event(
        db=db,
        event_id=x_github_delivery,
        event_type=x_github_event,
        payload_bytes=payload_bytes,
        signature_header=x_hub_signature_256
    )

    if res["status"] == "rejected":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=res["message"]
        )

    # Queue background task if a job was created
    queued_job_id = res.get("queued_job_id")
    if queued_job_id and x_github_event == "push":
        import json
        try:
            payload = json.loads(payload_bytes.decode("utf-8"))
            repo_full_name = payload.get("repository", {}).get("full_name", "")
            commit_sha = payload.get("after") or payload.get("head_commit", {}).get("id") or "HEAD"
            background_tasks.add_task(
                _run_async_reassessment,
                job_id=queued_job_id,
                repo_full_name=repo_full_name,
                commit_sha=commit_sha
            )
        except Exception:
            pass

    return res


@router.get("/events")
def list_webhook_events(db: Session = Depends(get_db)):
    """List recent webhook event deliveries."""
    events = db.query(WebhookEvent).order_by(WebhookEvent.created_at.desc()).limit(50).all()
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "repo_full_name": e.repo_full_name,
            "sender": e.sender,
            "status": e.status,
            "signature_valid": e.signature_valid,
            "error_message": e.error_message,
            "created_at": e.created_at
        }
        for e in events
    ]
