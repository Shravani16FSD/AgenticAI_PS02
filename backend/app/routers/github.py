"""
GitHub Integration Router for SkillTrace AI.
Provides:
- GET /api/github/status
- POST /api/github/connect
- POST /api/github/disconnect
- GET /api/github/repositories
- POST /api/github/repositories/{repo_id}/authorize
"""

import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import GitHubAccount, GitHubRepository, UserProfile
from ..schemas import (
    GitHubAccountResponse,
    GitHubConnectRequest,
    GitHubRepoResponse,
    AuthorizeRepoRequest
)
from ..services.github_service import github_service
from ..auth import get_authenticated_user

router = APIRouter(prefix="/api/github", tags=["GitHub Integration"])


@router.get("/status")
def get_github_status(
    user_id: Optional[str] = None,
    current_user: UserProfile = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """Check GitHub connection status for the current user."""
    uid = user_id if (user_id and user_id != "default_user") else current_user.id
    account = db.query(GitHubAccount).filter(GitHubAccount.user_id == uid).first()
    if not account:
        return {
            "connected": False,
            "account": None,
            "authorized_repositories_count": 0
        }

    authorized_count = (
        db.query(GitHubRepository)
        .filter(GitHubRepository.user_id == uid, GitHubRepository.is_authorized == True)
        .count()
    )

    return {
        "connected": True,
        "account": {
            "id": account.id,
            "github_username": account.github_username,
            "avatar_url": account.avatar_url,
            "html_url": account.html_url,
            "connected_at": account.connected_at
        },
        "authorized_repositories_count": authorized_count
    }


@router.post("/connect", response_model=GitHubAccountResponse)
async def connect_github_account(
    req: GitHubConnectRequest,
    user_id: Optional[str] = None,
    current_user: UserProfile = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Connect a user's GitHub account using an official personal access token or OAuth token.
    Token is stored server-side and never returned in plain text.
    """
    uid = user_id if (user_id and user_id != "default_user") else current_user.id
    try:
        user_info = await github_service.verify_token(req.token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to authenticate with GitHub: {str(e)}")

    username = user_info.get("login") or req.username or "github-user"
    avatar = user_info.get("avatar_url")
    html_url = user_info.get("html_url")
    now_utc = datetime.now(timezone.utc)

    # Check if account already registered for this user
    account = db.query(GitHubAccount).filter(GitHubAccount.user_id == uid).first()
    if account:
        account.github_username = username
        account.access_token = req.token
        account.avatar_url = avatar
        account.html_url = html_url
        account.updated_at = now_utc
    else:
        account = GitHubAccount(
            id=f"gha-{uuid.uuid4().hex[:8]}",
            user_id=uid,
            github_username=username,
            github_user_id=str(user_info.get("id")),
            access_token=req.token,
            avatar_url=avatar,
            html_url=html_url,
            connected_at=now_utc,
            updated_at=now_utc
        )
        db.add(account)

    db.commit()
    db.refresh(account)

    # Automatically sync repositories
    try:
        repos = await github_service.list_repositories(req.token)
        for r in repos:
            full_name = r.get("full_name")
            if not full_name:
                continue
            existing_repo = db.query(GitHubRepository).filter(
                GitHubRepository.user_id == user_id,
                GitHubRepository.repo_full_name == full_name
            ).first()
            if not existing_repo:
                db.add(GitHubRepository(
                    id=f"repo-{uuid.uuid4().hex[:8]}",
                    user_id=user_id,
                    account_id=account.id,
                    repo_full_name=full_name,
                    default_branch=r.get("default_branch", "main"),
                    is_private=r.get("private", False),
                    html_url=r.get("html_url"),
                    is_authorized=True,
                    last_synced_at=now_utc
                ))
        db.commit()
    except Exception as sync_err:
        logger.warning(f"Failed to auto-sync repos on connect: {sync_err}")

    return account


@router.post("/disconnect")
def disconnect_github_account(
    user_id: Optional[str] = None,
    current_user: UserProfile = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """Disconnect GitHub account and revoke authorization."""
    uid = user_id if (user_id and user_id != "default_user") else current_user.id
    account = db.query(GitHubAccount).filter(GitHubAccount.user_id == uid).first()
    if not account:
        raise HTTPException(status_code=404, detail="No connected GitHub account found.")

    db.delete(account)
    db.commit()
    return {"message": "GitHub account successfully disconnected."}


@router.get("/repositories", response_model=List[GitHubRepoResponse])
def list_repositories(
    user_id: Optional[str] = None,
    current_user: UserProfile = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """List accessible GitHub repositories for the user."""
    uid = user_id if (user_id and user_id != "default_user") else current_user.id
    repos = db.query(GitHubRepository).filter(GitHubRepository.user_id == uid).all()
    return repos


@router.post("/repositories/{repo_id}/authorize", response_model=GitHubRepoResponse)
def toggle_repository_authorization(
    repo_id: str,
    req: AuthorizeRepoRequest,
    user_id: Optional[str] = None,
    current_user: UserProfile = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    """Authorize or revoke permission for scanning a repository."""
    uid = user_id if (user_id and user_id != "default_user") else current_user.id
    repo = db.query(GitHubRepository).filter(
        GitHubRepository.id == repo_id,
        GitHubRepository.user_id == uid
    ).first()

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    repo.is_authorized = req.authorized
    repo.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(repo)
    return repo
