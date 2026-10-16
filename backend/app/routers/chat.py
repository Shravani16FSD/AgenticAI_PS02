import uuid
import asyncio
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ChatMessage, UserProfile, CareerPath, RoadmapTask, UserSkill
from ..schemas import ChatMessageResponse, ChatRequest
from ..config import settings

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.get("/history", response_model=List[ChatMessageResponse])
def get_chat_history(user_id: str = "default_user", db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id
    ).order_by(ChatMessage.timestamp.asc()).all()
    return messages

@router.delete("/history")
def clear_chat_history(user_id: str = "default_user", db: Session = Depends(get_db)):
    db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
    
    # Re-insert welcome greeting
    welcome = ChatMessage(
        id="msg-welcome",
        user_id=user_id,
        sender="assistant",
        text="Hello Alex. I am your career mentor.\n\nYour career is a journey, and you do not need to figure everything out today. Whether you want to reflect on what path fits your strengths, structure your weekly learning, or prepare for internship applications, I am here to work through it with you step-by-step.\n\nWhere would you like to start today?",
        suggested_actions=[
            "Help me choose a career direction.",
            "What should I learn to become an AI engineer?",
            "Can you help me prepare for an internship?",
            "Let's make a realistic weekly learning plan."
        ]
    )
    db.add(welcome)
    db.commit()
    return {"message": "Chat history cleared and reset"}

@router.post("")
async def send_chat_message(
    chat_in: ChatRequest,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    trimmed_prompt = chat_in.message.strip()
    if not trimmed_prompt:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # 1. Fetch live user context from database
    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    career = db.query(CareerPath).filter(CareerPath.id == user.target_career_id).first() if user else None
    active_tasks = db.query(RoadmapTask).filter(RoadmapTask.user_id == user_id).all() if user else []
    skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).all() if user else []

    career_title = career.title if career else "Technology & Engineering"
    study_status = user.study_status if user else "Student"
    primary_goal = user.primary_goal if user else "Career growth"
    weekly_hours = user.weekly_hours if user else 8

    # 2. Persist user message to database
    user_msg_id = f"msg-user-{uuid.uuid4().hex[:8]}"
    user_msg = ChatMessage(
        id=user_msg_id,
        user_id=user_id,
        sender="user",
        text=trimmed_prompt,
        timestamp=datetime.utcnow()
    )
    db.add(user_msg)
    db.commit()

    # 3. Contextual Mentorship Generation
    lower = trimmed_prompt.lower()
    
    if "choose" in lower or "direction" in lower or "not sure" in lower:
        response_md = f"""### Finding a direction that fits you

Choosing a career direction doesn't mean locking in a thirty-year commitment. It means choosing an intentional thesis for the next 6 to 12 months.

Based on your background in **{study_status}** and your stated career direction in **{career_title}**, here is how you can evaluate where to start:

1. **Look at the daily work, not the job title**
   Titles like *{career_title}* sound exciting, but daily work consists of reading documentation, crafting schemas, debugging interfaces, and collaborating on trade-offs.

2. **The Test-Project heuristic**
   Before committing to a long curriculum, spend **5 to 8 hours** building one small, contained artifact (such as a working API client with clean error states). If the friction of that task feels energizing rather than draining, you have strong signal.

3. **Suggested Next Step**
   Focusing on your foundational milestones in your roadmap will give you clarity faster than reading twenty articles.

Would you like to explore what a typical workday looks like for this role, or compare it with another path?"""
        follow_ups = [
            "What does a typical day look like for this role?",
            "How does this compare to Product Design?",
            "Can we plan my first 8-hour exploratory project?"
        ]
    elif "ai engineer" in lower or "learn to become" in lower or "ai product" in lower:
        response_md = f"""### Core Roadmap for AI Product Engineering

To become a capable AI Product Engineer, you do not need a PhD in mathematical optimization. The industry needs engineers who understand **systems engineering, reliability, and human ergonomics**.

Here is a practical breakdown tailored to your weekly commitment of **{weekly_hours} hours/week**:

#### 1. Foundation: Strict Type Systems & API Handling
- Master TypeScript and asynchronous streams (Server-Sent Events / WebSockets).
- *Why it matters:* Foundation models return non-deterministic streams; your client must handle interruptions, timeouts, and structured schemas gracefully.

#### 2. Core: Structured Generation & Schemas
- Work with tools like Pydantic (Python) or Zod (TypeScript) to enforce deterministic JSON outputs.
- Build prompt templates that reject invalid states before they reach the user.

#### 3. Real Application: Context & Vector Grounding
- Implement Retrieval-Augmented Generation (RAG) with local embeddings or lightweight vector indexes.
- Benchmark search accuracy and cost trade-offs.

#### 4. The Differentiator: Systematic Evaluation
- Most candidates stop at "it works in my test prompt." High-impact candidates build automated eval suites testing edge cases.

Spending 30 minutes on schema validation today will make your next project significantly more robust."""
        follow_ups = [
            "How do I test and benchmark prompt reliability?",
            "Which open-source vector store should I start with?",
            "Can you review my schema validation approach?"
        ]
    elif "internship" in lower or "interview" in lower or "job" in lower:
        response_md = f"""### Preparing for Internships with Substance

Hiring teams review hundreds of portfolios with identical tutorial clones. What catches a senior engineer's attention is **craft, error handling, and thoughtful trade-offs**.

Here is a direct checklist for your goal: *"{primary_goal}"*:

1. **Build one deep project over five shallow ones**
   Instead of five half-finished apps, polish one project until it feels production-ready. Ensure it has:
   - Resilient error handling (try disabling your network; does the UI inform you calmly?).
   - Real accessibility (keyboard navigation and WCAG AA contrast).
   - An architectural README explaining what technical trade-offs you made.

2. **Prepare your story around "Friction and Recovery"**
   In interviews, nobody is impressed by stories where everything worked on the first try. Prepare 2-3 stories where a model hallucinated, a stream broke, or a schema failed, and how you engineered a resilient recovery.

3. **Weekly application pace**
   Identify 5-10 teams whose product you genuinely respect, write a concise note referencing specific engineering decisions in their product, and attach your live demo.

Would you like to practice walking through an architectural trade-off, or review your portfolio project checklist?"""
        follow_ups = [
            "Help me outline my project's technical README.",
            "Let's practice a mock interview question.",
            "How do I explain trade-offs during a system design screen?"
        ]
    else:
        response_md = f"""### Addressing your question thoughtfully

Thank you for bringing this up. When considering **"{trimmed_prompt}"**, it helps to look at both the immediate practical step and the broader trajectory.

Here are three key considerations based on your roadmap toward **{career_title}**:

1. **Clarify the concrete outcome**
   What would success look like by the end of this week regarding this question? Is it understanding a concept, making a decision between two paths, or completing a specific prototype?

2. **Ground decisions in your real bandwidth**
   With {weekly_hours} hours available each week, prioritize actions that produce durable artifacts—code you can point to, notes you can reference, or conversations with practitioners.

3. **Immediate recommendation**
   Aligning your next work session with your in-progress milestones will keep your momentum steady.

How would you like to proceed? We can break this down into a 20-minute action item or explore the broader strategy."""
        follow_ups = [
            "Let's break this down into a 20-minute action item.",
            "How does this relate to my current roadmap task?",
            "Can we review my progress so far?"
        ]

    # 4. Persist assistant response to database
    assistant_msg_id = f"msg-assistant-{uuid.uuid4().hex[:8]}"
    assistant_msg = ChatMessage(
        id=assistant_msg_id,
        user_id=user_id,
        sender="assistant",
        text=response_md,
        suggested_actions=follow_ups,
        timestamp=datetime.utcnow()
    )
    db.add(assistant_msg)
    db.commit()

    # 5. Stream the response chunks to client
    async def chunk_generator():
        words = response_md.split(" ")
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + " "
            yield chunk
            await asyncio.sleep(0.03)

    return StreamingResponse(chunk_generator(), media_type="text/plain")
