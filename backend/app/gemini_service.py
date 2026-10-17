"""
Google Gemini integration service for Chapter / SkillTrace AI.
Provides resilient, production-ready access to Google Gemini using the official google-genai SDK.
Handles missing keys, invalid keys, timeouts, quota limits, and provider failures gracefully without crashing.
"""

import os
import re
import logging
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from .config import settings

logger = logging.getLogger("skilltrace.gemini")

# Known placeholder strings that indicate the API key has not been configured
PLACEHOLDER_KEYS = {
    "",
    "your_gemini_api_key_here",
    "placeholder",
    "your_api_key_here",
    "replace_with_gemini_key",
    "none",
    "null"
}


@dataclass
class GeminiResponse:
    """Structured response object from the Gemini service."""
    text: str
    success: bool
    status: str  # "success", "missing_key", "invalid_key", "timeout", "quota_exceeded", "provider_error"
    model: str
    error_detail: Optional[str] = None
    is_fallback: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary, guaranteeing no secret keys are present."""
        return {
            "text": self.text,
            "success": self.success,
            "status": self.status,
            "model": self.model,
            "error_detail": self.error_detail,
            "is_fallback": self.is_fallback,
            "metadata": self.metadata
        }


class GeminiService:
    """
    Robust Google Gemini service wrapper using Google's official google-genai SDK.
    Guarantees:
    - Never crashes the application on missing or invalid keys, timeouts, or quota limits.
    - Never leaks the API key to logs, exceptions, or responses.
    - Model name, timeouts, and API keys are configurable via environment variables or runtime overrides.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        fallback_model: Optional[str] = None,
        timeout_seconds: Optional[float] = None
    ):
        self._api_key = (api_key if api_key is not None else settings.GEMINI_API_KEY).strip()
        self.model = model or getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash-lite")
        self.fallback_model = fallback_model or getattr(settings, "GEMINI_FALLBACK_MODEL", "gemini-3.8-flash")
        self.timeout_seconds = timeout_seconds if timeout_seconds is not None else getattr(settings, "GEMINI_TIMEOUT_SECONDS", 15.0)
        self._client = None
        self._mock_client = None

    @property
    def is_configured(self) -> bool:
        """Check if a valid, non-placeholder API key is configured."""
        if not self._api_key:
            return False
        if self._api_key.lower() in PLACEHOLDER_KEYS:
            return False
        return True

    def set_mock_client(self, mock_client: Any) -> None:
        """Inject a mock client for deterministic unit testing without external network calls."""
        self._mock_client = mock_client

    def _get_client(self):
        """Lazy-initialize and return the official google-genai Client."""
        if self._mock_client is not None:
            return self._mock_client

        if not self.is_configured:
            return None

        if self._client is None:
            try:
                from google import genai
                from google.genai import types

                http_options = types.HttpOptions(timeout=float(self.timeout_seconds))
                self._client = genai.Client(
                    api_key=self._api_key,
                    http_options=http_options
                )
            except Exception as exc:
                sanitized = self._sanitize(str(exc))
                logger.error("Failed to initialize Google GenAI Client: %s", sanitized)
                return None

        return self._client

    def _sanitize(self, message: str) -> str:
        """Strip any instance of API keys or sensitive authorization tokens from text."""
        if not message:
            return ""
        sanitized = message
        if self._api_key and len(self._api_key) >= 6:
            sanitized = sanitized.replace(self._api_key, "[REDACTED_API_KEY]")
        # Redact generic AIzaSy keys and common API key patterns
        sanitized = re.sub(r"AIza[0-9A-Za-z-_]{35}", "[REDACTED_API_KEY]", sanitized)
        sanitized = re.sub(r"(?i)api[-_]?key['\":\s=]+[a-zA-Z0-9_\-]{8,}", "api_key=[REDACTED]", sanitized)
        return sanitized

    def _classify_error(self, exc: Exception) -> tuple[str, str]:
        """
        Classify exceptions into specific error statuses without leaking sensitive credentials.
        Returns (status, sanitized_detail).
        """
        raw_msg = str(exc)
        sanitized = self._sanitize(raw_msg)
        status_code = getattr(exc, "code", None)

        # 1. Check for Quota / Rate Limiting (429 / RESOURCE_EXHAUSTED)
        if status_code == 429 or "429" in raw_msg or "RESOURCE_EXHAUSTED" in raw_msg or "quota" in raw_msg.lower():
            return "quota_exceeded", "Gemini API quota exceeded or rate limit reached. Please check your plan or retry later."

        # 2. Check for Authentication / Invalid Key (400 / 403 with API_KEY_INVALID or permission denied)
        if (
            status_code in (400, 403)
            and any(term in raw_msg.lower() for term in ["api key not valid", "api_key_invalid", "permission", "unauthenticated", "invalid api key"])
        ):
            return "invalid_key", "Authentication failed: The provided Gemini API key is invalid or lacks required permissions."

        # 3. Check for Timeouts
        if "timeout" in raw_msg.lower() or "timed out" in raw_msg.lower() or status_code in (408, 504):
            return "timeout", f"Request to Gemini API timed out after {self.timeout_seconds}s."

        # 4. Check for Provider / Server Outages (500, 502, 503)
        if status_code in (500, 502, 503) or "server error" in raw_msg.lower() or "unavailable" in raw_msg.lower():
            return "provider_error", "Google Gemini provider temporarily unavailable. Please retry shortly."

        # 5. Generic provider failure
        return "provider_error", f"Gemini provider error: {sanitized}"

    def send_message(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> GeminiResponse:
        """
        Synchronously send a prompt to Gemini and return a resilient GeminiResponse.
        Never throws unhandled exceptions.
        """
        target_model = model or self.model

        if not self.is_configured:
            return GeminiResponse(
                text="The career mentor is currently running in offline contextual mode. To enable real-time Gemini AI coaching, configure GEMINI_API_KEY in backend/.env.",
                success=False,
                status="missing_key",
                model=target_model,
                error_detail="GEMINI_API_KEY environment variable is not configured or is a placeholder.",
                is_fallback=True
            )

        client = self._get_client()
        if client is None:
            return GeminiResponse(
                text="Gemini client could not be initialized. Please check backend configuration.",
                success=False,
                status="provider_error",
                model=target_model,
                error_detail="Failed to instantiate google-genai client.",
                is_fallback=True
            )

        try:
            from google.genai import types

            config = None
            if system_instruction:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature
                )

            # Call SDK generate_content
            response = client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=config
            )

            response_text = getattr(response, "text", "") or ""
            return GeminiResponse(
                text=response_text,
                success=True,
                status="success",
                model=target_model,
                is_fallback=False
            )

        except Exception as exc:
            status, detail = self._classify_error(exc)
            logger.warning("Gemini send_message failed [%s]: %s", status, detail)
            return GeminiResponse(
                text="I encountered a temporary issue connecting to the AI career coaching engine. Operating in safe contextual mode.",
                success=False,
                status=status,
                model=target_model,
                error_detail=detail,
                is_fallback=True
            )

    def _is_transient(self, exc: Exception) -> bool:
        """Determine whether an error is transient and eligible for bounded retry."""
        status_code = getattr(exc, "code", None)
        if status_code in (502, 503, 504):
            return True
        raw_msg = str(exc).lower()
        if any(term in raw_msg for term in ["unavailable", "overloaded", "temporarily", "connection reset", "connection refused", "try again later"]):
            return True
        return False

    async def send_message_async(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 2
    ) -> GeminiResponse:
        """
        Asynchronously send a prompt to Gemini with bounded retries for transient errors.
        Guarantees non-blocking execution and never raises unhandled exceptions.
        """
        target_model = model or self.model

        if not self.is_configured:
            return GeminiResponse(
                text="The career mentor is currently running in offline contextual mode. To enable real-time Gemini AI coaching, configure GEMINI_API_KEY in backend/.env.",
                success=False,
                status="missing_key",
                model=target_model,
                error_detail="GEMINI_API_KEY environment variable is not configured or is a placeholder.",
                is_fallback=True
            )

        client = self._get_client()
        if client is None:
            return GeminiResponse(
                text="Gemini client could not be initialized. Please check backend configuration.",
                success=False,
                status="provider_error",
                model=target_model,
                error_detail="Failed to instantiate google-genai client.",
                is_fallback=True
            )

        from google.genai import types

        config = None
        if system_instruction:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature
            )

        last_exc: Optional[Exception] = None
        for attempt in range(max_retries + 1):
            try:
                coro = client.aio.models.generate_content(
                    model=target_model,
                    contents=prompt,
                    config=config
                )

                response = await asyncio.wait_for(coro, timeout=float(self.timeout_seconds))
                response_text = getattr(response, "text", "") or ""

                return GeminiResponse(
                    text=response_text,
                    success=True,
                    status="success",
                    model=target_model,
                    is_fallback=False
                )

            except asyncio.TimeoutError as exc:
                last_exc = exc
                detail = f"Request to Gemini timed out after {self.timeout_seconds}s."
                logger.warning("Gemini send_message_async timeout (attempt %d/%d): %s", attempt + 1, max_retries + 1, detail)
                break  # Don't retry long timeouts
            except Exception as exc:
                last_exc = exc
                if attempt < max_retries and self._is_transient(exc):
                    backoff = 0.15 * (2 ** attempt)
                    logger.warning(
                        "Transient Gemini error (attempt %d/%d). Retrying in %.2fs: %s",
                        attempt + 1,
                        max_retries + 1,
                        backoff,
                        self._sanitize(str(exc))
                    )
                    await asyncio.sleep(backoff)
                    continue
                break

        if isinstance(last_exc, asyncio.TimeoutError):
            return GeminiResponse(
                text="The AI mentor took longer than expected to respond. Operating in safe contextual mode.",
                success=False,
                status="timeout",
                model=target_model,
                error_detail=f"Request to Gemini timed out after {self.timeout_seconds}s.",
                is_fallback=True
            )

        status, detail = self._classify_error(last_exc or Exception("Unknown error"))
        logger.warning("Gemini send_message_async failed after retries [%s]: %s", status, detail)
        return GeminiResponse(
            text="I encountered a temporary issue connecting to the AI career coaching engine. Operating in safe contextual mode.",
            success=False,
            status=status,
            model=target_model,
            error_detail=detail,
            is_fallback=True
        )

    async def generate_career_advice_async(
        self,
        prompt: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> GeminiResponse:
        """
        Specialized helper for career coaching conversations with tailored system instructions
        and candidate context injection. Enforces sandbox security instructions.
        """
        ctx = user_context or {}
        career_title = ctx.get("career_title", "Software Engineering / Tech")
        study_status = ctx.get("study_status", "Learner")
        primary_goal = ctx.get("primary_goal", "Career growth")
        weekly_hours = ctx.get("weekly_hours", 8)

        system_instruction = (
            "You are an encouraging, pragmatic, and highly analytical AI Career Mentor for NEXORA. "
            "You guide students and engineers through career choices, roadmap planning, real-world portfolio building, "
            "and technical interview readiness. Focus on concrete trade-offs, evidence-based skill proof, and realistic weekly execution. "
            "Never hallucinate credentials. Format responses in clean Markdown with clear headings and bullet points. "
            "SECURITY RESTRICTIONS: You operate strictly as a career advisor. You must NEVER execute or formulate executable SQL, "
            "shell/bash scripts, or unrestricted system commands. You do not have access to any external databases or command shells."
        )

        context_prompt = (
            f"Candidate Context:\n"
            f"- Target Career Track: {career_title}\n"
            f"- Background / Status: {study_status}\n"
            f"- Primary Goal: {primary_goal}\n"
            f"- Available Bandwidth: {weekly_hours} hours per week\n\n"
            f"Candidate Question / Message:\n{prompt}"
        )

        return await self.send_message_async(
            prompt=context_prompt,
            system_instruction=system_instruction
        )


# Global singleton instance configured from backend settings
gemini_service = GeminiService()
