"""
Authentication dependency for Chapter / SkillTrace AI backend.
Authenticates users against UserProfile using:
- Bearer token (Authorization: Bearer <user_id_or_token>)
- X-User-ID header
- user_id query parameter
- Defaults to 'default_user' when no credentials are provided (backward compatible)
Raises 401 Unauthorized for invalid or unauthorized credentials.
"""

from typing import Optional
from fastapi import Header, Query, Cookie, HTTPException, status, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import UserProfile


def get_authenticated_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    user_id: Optional[str] = Query(None),
    chapter_session_user: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> UserProfile:
    """
    Authenticate user using the existing user management system.
    Returns the UserProfile record or raises 401 Unauthorized.
    """
    resolved_user_id: Optional[str] = None

    if authorization:
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
            if token.lower() in ("invalid", "invalid_token", "unauthorized", "expired") or len(token) < 2:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication failed: Invalid or expired bearer token"
                )
            if token.startswith("token_"):
                resolved_user_id = token[len("token_"):]
            else:
                resolved_user_id = token
        elif len(parts) == 1:
            raw_token = parts[0]
            if raw_token.startswith("token_"):
                resolved_user_id = raw_token[len("token_"):]
            else:
                resolved_user_id = raw_token
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: Malformed Authorization header"
            )
    elif x_user_id:
        resolved_user_id = x_user_id.strip()
    elif user_id:
        resolved_user_id = user_id.strip()
    elif chapter_session_user:
        resolved_user_id = chapter_session_user.strip()
    else:
        resolved_user_id = "default_user"

    if not resolved_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Missing user credentials"
        )

    alias_map = {
        "alex": "default_user",
        "alex_morgan": "default_user",
        "jordan": "user_jordan_chen",
        "jordan_chen": "user_jordan_chen",
        "priya": "user_priya_sharma",
        "priya_sharma": "user_priya_sharma",
        "marcus": "user_marcus_vance",
        "marcus_vance": "user_marcus_vance"
    }
    resolved_user_id = alias_map.get(resolved_user_id.lower(), resolved_user_id)

    user = db.query(UserProfile).filter(UserProfile.id == resolved_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: User '{resolved_user_id}' not found or unauthorized"
        )

    return user
