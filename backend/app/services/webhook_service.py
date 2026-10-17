"""
GitHub Webhook and Asynchronous Reassessment Service for SkillTrace AI.
Enforces:
1. HMAC-SHA256 signature verification with GITHUB_WEBHOOK_SECRET.
2. Idempotent event processing via persistent delivery IDs (X-GitHub-Delivery).
3. Authorization check against registered user repositories.
4. Identification of changed, added, and removed files from push events.
5. Asynchronous reassessment queueing and background job status tracking.
6. Multi-version assessment creation with previous version preservation.
"""

from __future__ import annotations
import hmac
import hashlib
import json
import uuid
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from ..config import settings
from ..models import (
    WebhookEvent,
    GitHubRepository,
    BackgroundJob,
    CommitRecord,
    SkillAssessment,
    UserProfile
)
from .github_service import github_service
from .assessment_engine import assessment_engine

logger = logging.getLogger("skilltrace.webhook")


class WebhookService:
    def __init__(self):
        pass

    def verify_signature(self, payload_bytes: bytes, signature_header: Optional[str]) -> bool:
        """
        Validates GitHub webhook HMAC-SHA256 signature.
        Header format: sha256=<hex_digest>
        """
        secret = settings.GITHUB_WEBHOOK_SECRET
        if not secret:
            logger.warning("GITHUB_WEBHOOK_SECRET is not configured.")
            return False

        if not signature_header or not signature_header.startswith("sha256="):
            return False

        expected_signature = "sha256=" + hmac.new(
            secret.encode("utf-8"),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature_header)

    async def process_webhook_event(
        self,
        db: Session,
        event_id: str,
        event_type: str,
        payload_bytes: bytes,
        signature_header: Optional[str]
    ) -> Dict[str, Any]:
        """
        Handles incoming GitHub webhook delivery idempotently.
        """
        now_utc = datetime.now(timezone.utc)

        # 1. Idempotency Check
        existing_event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
        if existing_event:
            return {
                "status": "duplicate",
                "event_id": event_id,
                "event_type": event_type,
                "message": f"Webhook delivery {event_id} already recorded with status: {existing_event.status}",
                "queued_job_id": None
            }

        # 2. Verify HMAC Signature
        signature_valid = self.verify_signature(payload_bytes, signature_header)
        if not signature_valid:
            # Record failed event for audit trail
            event_rec = WebhookEvent(
                id=event_id,
                event_type=event_type,
                repo_full_name="unknown",
                payload={},
                signature_valid=False,
                status="rejected",
                error_message="Invalid HMAC-SHA256 signature",
                processed_at=now_utc,
                created_at=now_utc
            )
            db.add(event_rec)
            db.commit()
            return {
                "status": "rejected",
                "event_id": event_id,
                "event_type": event_type,
                "message": "Invalid webhook signature",
                "queued_job_id": None
            }

        # 3. Parse JSON Payload
        try:
            payload = json.loads(payload_bytes.decode("utf-8"))
        except Exception as e:
            return {
                "status": "rejected",
                "event_id": event_id,
                "event_type": event_type,
                "message": f"Malformed JSON payload: {e}",
                "queued_job_id": None
            }

        repo_meta = payload.get("repository", {})
        repo_full_name = repo_meta.get("full_name")

        # 4. Check Repository Authorization
        repo_rec = None
        if repo_full_name:
            repo_rec = db.query(GitHubRepository).filter(
                GitHubRepository.repo_full_name == repo_full_name,
                GitHubRepository.is_authorized == True
            ).first()

        # If repo is not authorized or not found
        if not repo_rec and event_type == "push":
            event_rec = WebhookEvent(
                id=event_id,
                event_type=event_type,
                repo_full_name=repo_full_name or "unknown",
                sender=payload.get("sender", {}).get("login"),
                payload=payload,
                signature_valid=True,
                status="ignored",
                error_message=f"Repository '{repo_full_name}' is not an authorized repository.",
                processed_at=now_utc,
                created_at=now_utc
            )
            db.add(event_rec)
            db.commit()
            return {
                "status": "ignored",
                "event_id": event_id,
                "event_type": event_type,
                "message": f"Repository '{repo_full_name}' is not authorized for assessment.",
                "queued_job_id": None
            }

        # 5. Handle Non-push events (e.g. ping)
        if event_type != "push":
            event_rec = WebhookEvent(
                id=event_id,
                event_type=event_type,
                repo_full_name=repo_full_name,
                sender=payload.get("sender", {}).get("login"),
                payload=payload,
                signature_valid=True,
                status="processed",
                processed_at=now_utc,
                created_at=now_utc
            )
            db.add(event_rec)
            db.commit()
            return {
                "status": "processed",
                "event_id": event_id,
                "event_type": event_type,
                "message": f"Webhook '{event_type}' event acknowledged.",
                "queued_job_id": None
            }

        # 6. Extract Push Metadata
        commit_sha = payload.get("after") or payload.get("head_commit", {}).get("id") or "HEAD"
        head_commit = payload.get("head_commit") or {}
        commit_msg = head_commit.get("message", "Push event trigger")
        author_name = head_commit.get("author", {}).get("name", "Unknown Author")

        added_files = head_commit.get("added", [])
        modified_files = head_commit.get("modified", [])
        removed_files = head_commit.get("removed", [])

        # Store commit record
        commit_rec = CommitRecord(
            id=f"commit-{uuid.uuid4().hex[:8]}",
            repo_full_name=repo_full_name,
            commit_sha=commit_sha,
            author_name=author_name,
            commit_message=commit_msg,
            committed_at=now_utc,
            files_added=added_files,
            files_modified=modified_files,
            files_removed=removed_files,
            created_at=now_utc
        )
        db.add(commit_rec)

        # 7. Queue Background Job
        job_id = f"job-{uuid.uuid4().hex[:10]}"
        user_id = repo_rec.user_id if repo_rec else "default_user"

        background_job = BackgroundJob(
            id=job_id,
            job_type="webhook_reassessment",
            status="pending",
            target_id=repo_full_name,
            started_at=now_utc,
            created_at=now_utc
        )
        db.add(background_job)

        event_rec = WebhookEvent(
            id=event_id,
            event_type=event_type,
            repo_full_name=repo_full_name,
            sender=payload.get("sender", {}).get("login"),
            payload=payload,
            signature_valid=True,
            status="processed",
            processed_at=now_utc,
            created_at=now_utc
        )
        db.add(event_rec)
        db.commit()

        # Return immediately so webhook caller is not blocked
        return {
            "status": "queued",
            "event_id": event_id,
            "event_type": event_type,
            "message": f"Push event queued for reassessment on commit {commit_sha[:7]}.",
            "queued_job_id": job_id
        }

    async def execute_background_reassessment(
        self,
        db: Session,
        job_id: str,
        repo_full_name: str,
        commit_sha: str,
        user_id: str = "default_user",
        files: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Executes asynchronous reassessment for a background job.
        Updates BackgroundJob status to completed or failed.
        """
        bg_job = db.query(BackgroundJob).filter(BackgroundJob.id == job_id).first()
        if bg_job:
            bg_job.status = "in_progress"
            db.commit()

        try:
            # Find any active job listings or recent assessments for this repo
            recent_asm = (
                db.query(SkillAssessment)
                .filter(
                    SkillAssessment.user_id == user_id,
                    SkillAssessment.repo_full_name == repo_full_name
                )
                .order_by(SkillAssessment.version.desc())
                .first()
            )
            target_job_id = recent_asm.job_id if recent_asm else None

            # Execute assessment engine
            new_assessment = await assessment_engine.execute_assessment(
                db=db,
                user_id=user_id,
                repo_full_name=repo_full_name,
                commit_sha=commit_sha,
                job_id=target_job_id,
                files=files
            )

            if bg_job:
                bg_job.status = "completed"
                bg_job.completed_at = datetime.now(timezone.utc)
                bg_job.result_summary = {
                    "assessment_id": new_assessment.id,
                    "version": new_assessment.version,
                    "overall_score": new_assessment.overall_score,
                    "commit_sha": commit_sha,
                    "summary": new_assessment.summary
                }
                db.commit()

        except Exception as e:
            logger.error(f"Background reassessment failed for job {job_id}: {e}")
            if bg_job:
                bg_job.status = "failed"
                bg_job.error_message = str(e)
                bg_job.completed_at = datetime.now(timezone.utc)
                db.commit()


webhook_service = WebhookService()
