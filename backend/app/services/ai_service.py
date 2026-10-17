"""
AI Service Module for Chapter AI Career Coach.
Provides grounded conversational mentorship powered by Google Gemini via the Interactions API.
"""

import logging
from typing import AsyncIterator, List, Optional, Tuple, Dict, Any
from google import genai
from google.genai import errors

from ..config import settings
from ..models import UserProfile, CareerPath, RoadmapTask, UserSkill, ChatMessage

logger = logging.getLogger("chapter.ai_service")

# Canonical model ID — updated to gemini-3.8-flash per Google Gemini Interactions API standard.
# Override via GEMINI_MODEL in backend/.env.
_DEFAULT_MODEL = "gemini-3.8-flash"



class GeminiServiceError(Exception):
    """Base exception for Gemini AI service issues."""
    pass


class MissingApiKeyError(GeminiServiceError):
    """Raised when GEMINI_API_KEY is missing, empty, or set to placeholder text."""
    pass


class GeminiRateLimitError(GeminiServiceError):
    """Raised when Gemini returns HTTP 429 Too Many Requests."""
    pass


class GeminiTimeoutError(GeminiServiceError):
    """Raised when a request to Gemini times out."""
    pass


class GeminiProviderError(GeminiServiceError):
    """Raised when Gemini returns an upstream provider error."""
    pass


def has_configured_api_key() -> bool:
    """
    Checks whether a valid, non-placeholder GEMINI_API_KEY is configured.
    Never logs or exposes the key value.
    """
    key = (settings.GEMINI_API_KEY or "").strip()
    if not key:
        return False
    if key in ("your_gemini_api_key_here", "placeholder", "TODO"):
        return False
    if key.startswith("your_"):
        return False
    return True


def get_gemini_client() -> genai.Client:
    """
    Returns an authenticated Google GenAI client.
    Raises MissingApiKeyError if the API key is missing or invalid.
    """
    if not has_configured_api_key():
        raise MissingApiKeyError(
            "Gemini API key is not configured on the backend. Please add GEMINI_API_KEY to backend/.env with a valid key from Google AI Studio (https://aistudio.google.com/)."
        )
    return genai.Client(api_key=settings.GEMINI_API_KEY.strip())


def build_grounded_mentor_context(
    user: Optional[UserProfile],
    career: Optional[CareerPath],
    skills: List[UserSkill],
    tasks: List[RoadmapTask],
) -> str:
    """
    Constructs a structured, bounded markdown block of user context to ground the AI mentor.
    Safely limits array sizes to avoid context window inflation.
    """
    sections: List[str] = []

    # 1. User Profile Context
    name = (user.name if user and user.name else "Learner").strip()
    study_status = (user.study_status if user and user.study_status else "Student / Self-Directed Learner").strip()
    primary_goal = (user.primary_goal if user and user.primary_goal else "Career growth in technology").strip()
    weekly_hours = user.weekly_hours if user and user.weekly_hours else 8
    interests = user.interests if user and isinstance(user.interests, list) else []
    interests_str = ", ".join(interests[:6]) if interests else "Software Engineering, Product Design"

    sections.append(f"""### USER PROFILE
- **Name:** {name}
- **Current Study Status / Background:** {study_status}
- **Primary Goal:** {primary_goal}
- **Available Bandwidth:** {weekly_hours} hours per week
- **Stated Interests:** {interests_str}""")

    # 2. Target Career Context
    if career:
        title = career.title or "Technology Specialist"
        description = career.description or ""
        responsibilities = career.responsibilities if isinstance(career.responsibilities, list) else []
        resp_str = "; ".join(responsibilities[:3]) if responsibilities else "Building resilient systems"
        next_step = career.recommended_next_step or "Focus on foundational milestone projects"

        sections.append(f"""### TARGET CAREER DIRECTION: {title}
- **Overview:** {description}
- **Core Responsibilities:** {resp_str}
- **Recommended Focus:** {next_step}""")
    else:
        sections.append("""### TARGET CAREER DIRECTION
- Not yet specified. Help the user explore career options based on their interests and strengths.""")

    # 3. User Skills & Gaps
    if skills:
        practiced_items = []
        gap_items = []
        for s in skills[:12]:
            s_name = s.name or "Skill"
            if s.is_gap:
                gap_items.append(f"{s_name} (target {s.target_hours}h)")
            else:
                practiced_items.append(f"{s_name} ({s.hours_spent}h practiced / {s.target_hours}h target)")

        practiced_str = ", ".join(practiced_items) if practiced_items else "Foundational fundamentals"
        gap_str = ", ".join(gap_items) if gap_items else "None currently flagged"

        sections.append(f"""### SKILL PROFILE
- **Tracked Skills:** {practiced_str}
- **Identified Skill Gaps:** {gap_str}""")

    # 4. Active Roadmap Tasks & Milestones
    if tasks:
        in_progress = [t.title for t in tasks if t.status == "in_progress"][:4]
        todo = [t.title for t in tasks if t.status == "todo"][:4]
        completed = [t.title for t in tasks if t.status == "completed"][:3]

        in_progress_str = "; ".join(in_progress) if in_progress else "None currently active"
        todo_str = "; ".join(todo) if todo else "None queued"
        completed_str = "; ".join(completed) if completed else "None completed yet"

        sections.append(f"""### ROADMAP MILESTONES
- **Currently In Progress:** {in_progress_str}
- **Next Up (To Do):** {todo_str}
- **Completed:** {completed_str}""")

    return "\n\n".join(sections)


def get_mentor_system_instruction(grounded_context: str) -> str:
    """
    Combines the persona guidelines and grounded context into the model's system instruction.
    """
    return f"""You are "NEXORA", an empathetic, pragmatic, and highly knowledgeable AI Career Mentor designed specifically for university students, bootcamp grads, and early-career software developers and product designers.

YOUR PERSONA AND COMMUNICATION STYLE:
1. **Thoughtful & Editorial:** Speak like a respected staff engineer, product mentor, or trusted advisor who values craftsmanship, systems thinking, and human ergonomics.
2. **Honest & Grounded:** Never make false hiring guarantees or cheerlead with hollow clichés ("You can do anything you set your mind to!"). Instead, discuss realistic industry standards, genuine technical trade-offs, and how hiring managers actually evaluate candidates.
3. **Respect Realistic Bandwidth:** The student has a specific weekly budget (e.g. 8 hours/week). When suggesting practice or project ideas, design actions that fit realistically into this time rather than overwhelming 40-hour laundry lists.
4. **Ask Clarifying Questions:** If essential context about their exact tech stack, current project, or prior experience is missing, ask 1 focused, practical follow-up question instead of inventing or assuming facts.
5. **Formatting:** Use clean GitHub-flavored markdown with concise headers (### or ####), bullet points, and bold text for key principles. Keep paragraphs concise and scannable.

RECOMMENDED FOLLOW-UP PROMPTS:
At the very end of your response, output exactly 2 to 3 concise, highly relevant follow-up questions or next actions that the user can ask or click. Format each one on its own line starting with "Follow-up: " like this:
Follow-up: <Concise question 1>
Follow-up: <Concise question 2>

---
{grounded_context}
"""


def format_chat_steps(
    history: List[ChatMessage],
    current_prompt: str,
    max_history_turns: int = 8
) -> List[Dict[str, Any]]:
    """
    Transforms database ChatMessage records into Interactions API step dicts.
    The Interactions API expects a list of steps with type 'user_input' or
    'model_output', each containing a 'content' array of text parts.

    Constraints enforced:
    - First step must be 'user_input'
    - Consecutive steps of the same type are coalesced
    - Current prompt is appended as the final 'user_input' step
    """
    steps: List[Dict[str, Any]] = []

    # Limit to the most recent turns to conserve context window
    recent_history = history[-max_history_turns:] if len(history) > max_history_turns else history

    for msg in recent_history:
        text = (msg.text or "").strip()
        if not text:
            continue

        step_type = "user_input" if msg.sender == "user" else "model_output"

        # First step must be user_input
        if not steps and step_type != "user_input":
            continue

        # Coalesce consecutive steps of the same type
        if steps and steps[-1]["type"] == step_type:
            existing_text = steps[-1]["content"][0]["text"]
            steps[-1]["content"][0]["text"] = f"{existing_text}\n\n{text}"
        else:
            steps.append({"type": step_type, "content": [{"type": "text", "text": text}]})

    # Append current user prompt as final user_input step
    trimmed_prompt = current_prompt.strip()
    if steps and steps[-1]["type"] == "user_input":
        existing_text = steps[-1]["content"][0]["text"]
        steps[-1]["content"][0]["text"] = f"{existing_text}\n\n{trimmed_prompt}"
    else:
        steps.append({"type": "user_input", "content": [{"type": "text", "text": trimmed_prompt}]})

    return steps


# Backwards compatibility alias
format_chat_contents = format_chat_steps


def extract_follow_up_actions(text: str) -> Tuple[str, List[str]]:
    """
    Extracts 'Follow-up: ...' lines from the end of the response and returns:
    (cleaned_text_without_followups, list_of_suggested_actions).
    """
    lines = text.split("\n")
    cleaned_lines: List[str] = []
    follow_ups: List[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("follow-up:"):
            action = stripped.split(":", 1)[1].strip()
            action = action.strip("\"'*- ")
            if action:
                follow_ups.append(action)
        else:
            cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines).rstrip()

    if not follow_ups:
        follow_ups = [
            "How does this connect to my current roadmap milestone?",
            "Can we plan a 25-minute practice exercise for this?",
            "What common mistakes do candidates make here?"
        ]

    return cleaned_text, follow_ups[:4]


async def stream_mentorship_response(
    client: genai.Client,
    steps: Optional[Any] = None,
    system_instruction: str = "",
    model: Optional[str] = None,
    contents: Optional[Any] = None,
) -> AsyncIterator[str]:
    """
    Executes an asynchronous streaming request via the Gemini Interactions API
    and yields text chunks as they arrive.

    Uses client.aio.interactions.create() with stream=True, which is the
    recommended API for multi-turn conversational AI.

    Handles rate limits, invalid model IDs, authentication failures, and
    other API errors with typed exceptions.
    """
    target_model = model or settings.GEMINI_MODEL or _DEFAULT_MODEL
    logger.info(f"Streaming interaction via Interactions API with model: {target_model}")

    # Support either steps or contents parameter
    raw_input = steps if steps is not None else contents
    if raw_input is None:
        raise ValueError("Either steps or contents must be provided.")

    # Normalize input if needed
    if isinstance(raw_input, str):
        normalized_input = raw_input
    elif isinstance(raw_input, list):
        normalized_input = []
        for item in raw_input:
            if isinstance(item, dict):
                normalized_input.append(item)
            elif hasattr(item, "role") and hasattr(item, "parts"):
                # Convert types.Content to Interactions API step format
                step_type = "user_input" if item.role == "user" else "model_output"
                text_parts = [p.text for p in item.parts if getattr(p, "text", None)]
                normalized_input.append({
                    "type": step_type,
                    "content": [{"type": "text", "text": "\n\n".join(text_parts)}]
                })
            else:
                normalized_input.append(item)
    else:
        normalized_input = raw_input

    try:
        response_stream = await client.aio.interactions.create(
            model=target_model,
            input=normalized_input,
            system_instruction=system_instruction,
            stream=True,
            generation_config={
                "max_output_tokens": 1500,
            },
        )

        async for event in response_stream:
            event_type = getattr(event, "event_type", None)
            if event_type == "step.delta":
                delta = getattr(event, "delta", None)
                if delta and getattr(delta, "type", None) == "text":
                    text_chunk = getattr(delta, "text", None)
                    if text_chunk:
                        yield text_chunk

    except errors.APIError as e:
        code = getattr(e, "code", None)
        message = getattr(e, "message", str(e)) or "Service temporarily unavailable."
        logger.error(f"Gemini APIError: code={code}, message={message}")
        if code == 429:
            raise GeminiRateLimitError(
                "Gemini API rate limit exceeded. Please wait a moment and try again."
            ) from e
        if code in (401, 403):
            raise GeminiProviderError(
                "Gemini API authentication failed. Please verify your GEMINI_API_KEY in backend/.env."
            ) from e
        if code == 404 or "no longer available" in message.lower() or "not found" in message.lower():
            raise GeminiProviderError(
                f"Model '{target_model}' is not available or deprecated: {message}. "
                "Update GEMINI_MODEL in backend/.env to a supported model (e.g. gemini-3.8-flash)."
            ) from e
        if code == 503 or "high demand" in message.lower():
            raise GeminiProviderError(
                "Gemini model is currently experiencing high demand. Please try again in a moment."
            ) from e
        raise GeminiProviderError(
            f"Gemini AI provider returned an error (code={code}): {message}"
        ) from e
    except Exception as e:
        err_str = str(e).lower()
        logger.error(f"Unexpected error during Gemini stream: {type(e).__name__}: {str(e)}")
        if "timeout" in err_str or "timed out" in err_str:
            raise GeminiTimeoutError("Gemini request timed out. Please try again.") from e
        raise GeminiProviderError(
            f"An unexpected error occurred while communicating with Gemini: {str(e)}"
        ) from e

