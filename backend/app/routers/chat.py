import uuid
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db, SessionLocal
from ..models import ChatMessage, UserProfile, CareerPath, RoadmapTask, UserSkill
from ..schemas import ChatMessageResponse, ChatRequest
from ..services import ai_service

from ..config import settings

logger = logging.getLogger("chapter.routers.chat")

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.get("/status")
def get_chat_status():
    return {
        "provider": "google-gemini",
        "sdk": "google-genai",
        "model": settings.GEMINI_MODEL,
        "configured": ai_service.has_configured_api_key(),
    }



@router.get("/history", response_model=List[ChatMessageResponse])
def get_chat_history(
    user_id: str = "default_user",
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
    if session_id:
        query = query.filter(ChatMessage.session_id == session_id)
    messages = query.order_by(ChatMessage.timestamp.asc()).all()
    return messages


@router.delete("/history")
def clear_chat_history(
    user_id: str = "default_user",
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
    if session_id:
        query = query.filter(ChatMessage.session_id == session_id)
    query.delete(synchronize_session=False)

    active_session = session_id or "default_session"

    # Fetch user's first name if available for personalized greeting
    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    first_name = user.name.split()[0] if user and user.name else "there"

    # Re-insert welcome greeting scoped to this user and session
    welcome = ChatMessage(
        id=f"msg-welcome-{uuid.uuid4().hex[:8]}",
        user_id=user_id,
        session_id=active_session,
        sender="assistant",
        text=f"Hello {first_name}. I am your career mentor.\n\nYour career is a journey, and you do not need to figure everything out today. Whether you want to reflect on what path fits your strengths, structure your weekly learning, or prepare for internship applications, I am here to work through it with you step-by-step.\n\nWhere would you like to start today?",
        suggested_actions=[
            "Help me choose a career direction.",
            "What should I learn to become an AI engineer?",
            "Can you help me prepare for an internship?",
            "Let's make a realistic weekly learning plan."
        ],
        status="delivered",
        timestamp=datetime.utcnow()
    )
    db.add(welcome)
    db.commit()
    return {"message": "Chat history cleared and reset", "session_id": active_session}


@router.post("")
async def send_chat_message(
    chat_in: ChatRequest,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    trimmed_prompt = chat_in.message.strip()
    if not trimmed_prompt:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    session_id = chat_in.session_id or chat_in.conversation_id or "default_session"

    # Check whether Gemini API key is configured before doing anything else
    if not ai_service.has_configured_api_key():
        # Persist the user message first so conversation records are not lost
        user_msg = ChatMessage(
            id=f"msg-user-{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            session_id=session_id,
            sender="user",
            text=trimmed_prompt,
            status="delivered",
            timestamp=datetime.utcnow()
        )
        db.add(user_msg)
        db.commit()

        raise HTTPException(
            status_code=503,
            detail="Gemini API key is not configured on the backend. Please add GEMINI_API_KEY to backend/.env with a valid key from Google AI Studio (https://aistudio.google.com/) to enable live AI mentorship."
        )

    # 1. Fetch live grounding context from database
    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    career = db.query(CareerPath).filter(CareerPath.id == user.target_career_id).first() if user else None
    active_tasks = db.query(RoadmapTask).filter(RoadmapTask.user_id == user_id).all() if user else []
    skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).all() if user else []

    grounded_context = ai_service.build_grounded_mentor_context(user, career, skills, active_tasks)
    system_instruction = ai_service.get_mentor_system_instruction(grounded_context)

    # 2. Persist user message to database
    user_msg_id = f"msg-user-{uuid.uuid4().hex[:8]}"
    user_msg = ChatMessage(
        id=user_msg_id,
        user_id=user_id,
        session_id=session_id,
        sender="user",
        text=trimmed_prompt,
        status="delivered",
        timestamp=datetime.utcnow()
    )
    db.add(user_msg)
    db.commit()

    # 3. Retrieve conversation history for this (user_id, session_id)
    past_history = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.user_id == user_id,
            ChatMessage.session_id == session_id,
            ChatMessage.id != user_msg_id
        )
        .order_by(ChatMessage.timestamp.asc())
        .all()
    )

    steps = ai_service.format_chat_steps(past_history, trimmed_prompt)
    client = ai_service.get_gemini_client()

    # 4. Stream response from Gemini and persist upon completion
    async def response_streamer():
        accumulated_text = ""
        stream_failed = False
        try:
            async for chunk in ai_service.stream_mentorship_response(
                client=client,
                steps=steps,
                system_instruction=system_instruction
            ):

                accumulated_text += chunk
                yield chunk

        except ai_service.GeminiRateLimitError as e:
            stream_failed = True
            err_msg = f"\n\n*[Rate limit reached: {str(e)}]*"
            accumulated_text += err_msg
            yield err_msg
        except ai_service.GeminiProviderError as e:
            stream_failed = True
            err_msg = f"\n\n*[AI provider error: {str(e)}]*"
            accumulated_text += err_msg
            yield err_msg
        except Exception as e:
            stream_failed = True
            err_msg = f"\n\n*[Connection error: {str(e)}]*"
            accumulated_text += err_msg
            yield err_msg
        finally:
            if accumulated_text.strip():
                cleaned_text, follow_ups = ai_service.extract_follow_up_actions(accumulated_text)
                save_db = SessionLocal()
                try:
                    assistant_msg = ChatMessage(
                        id=f"msg-assistant-{uuid.uuid4().hex[:8]}",
                        user_id=user_id,
                        session_id=session_id,
                        sender="assistant",
                        text=cleaned_text,
                        suggested_actions=follow_ups,
                        status="error" if stream_failed else "delivered",
                        timestamp=datetime.utcnow()
                    )
                    save_db.add(assistant_msg)
                    save_db.commit()
                except Exception as ex:
                    save_db.rollback()
                    logger.error(f"Failed to persist assistant response: {ex}")
                finally:
                    save_db.close()

    return StreamingResponse(response_streamer(), media_type="text/plain")
