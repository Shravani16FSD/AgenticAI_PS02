"""
Comprehensive Stage 3 test suite for the Secure Career Coach backend API.
Validates:
1. Successful response generation with consistent JSON output.
2. Conversation ID support and persistence.
3. User authentication (valid user, invalid user, bad bearer token -> 401).
4. Input validation and sensible size limits (empty message, > 4000 chars -> 400).
5. Missing API key handling (safe 503 error, no crash).
6. Provider error and timeout handling (safe 502/504 errors, no stack traces or raw leaks).
7. Bounded retries for transient errors (retries 503 and recovers).
8. Security sandbox: LLM output containing SQL or shell commands is never executed.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.gemini_service import gemini_service
from backend.app.models import UserProfile, ChatMessage
from backend.app.database import SessionLocal
from google.genai import errors


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_gemini_service():
    """Ensure mock client is reset between test cases."""
    original_mock = gemini_service._mock_client
    original_key = gemini_service._api_key
    yield
    gemini_service._mock_client = original_mock
    gemini_service._api_key = original_key


def test_successful_mocked_response(client):
    """Test successful message sending returning consistent JSON ChatResponse."""
    gemini_service._api_key = "AIzaSy_ValidKeyForTesting12345"

    mock_resp = MagicMock()
    mock_resp.text = "### Recommended Steps for AI Engineering\n1. Master Python AST and FastAPI.\n2. Build a grounded vector RAG demo."

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
    gemini_service.set_mock_client(mock_client)

    payload = {
        "message": "How do I transition to AI Engineering?",
        "conversation_id": "conv-test-101"
    }

    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["conversation_id"] == "conv-test-101"
    assert data["sender"] == "assistant"
    assert "reply" in data
    assert "text" in data
    assert "Recommended Steps for AI Engineering" in data["reply"]
    assert data["status"] == "delivered"
    assert "message_id" in data
    assert len(data["suggested_actions"]) > 0


def test_invalid_input_empty_message(client):
    """Test that empty or whitespace-only messages are rejected with 400."""
    # Empty string
    resp1 = client.post("/api/chat", json={"message": ""})
    assert resp1.status_code in (400, 422)

    # Whitespace only
    resp2 = client.post("/api/chat", json={"message": "     "})
    assert resp2.status_code in (400, 422)
    assert "empty" in resp2.text.lower() or "whitespace" in resp2.text.lower()


def test_invalid_input_oversized_message(client):
    """Test that messages exceeding 4000 characters are rejected with 400/422."""
    oversized = "A" * 4005
    response = client.post("/api/chat", json={"message": oversized})
    assert response.status_code in (400, 422)
    assert "4000" in response.text or "exceed" in response.text.lower()


def test_missing_api_key_error_response(client):
    """Test that missing GEMINI_API_KEY returns a safe 503 error without crashing."""
    gemini_service._api_key = ""
    gemini_service._mock_client = None

    response = client.post("/api/chat", json={"message": "Hello coach"})
    assert response.status_code == 503
    data = response.json()
    assert "GEMINI_API_KEY" in data["detail"] or "unconfigured" in data["detail"].lower()
    # Ensure no secrets or tracebacks are leaked
    assert "traceback" not in response.text.lower()


def test_authentication_failure_invalid_user(client):
    """Test that non-existent user returns 401 Unauthorized."""
    response = client.post(
        "/api/chat?user_id=ghost_non_existent_user_999",
        json={"message": "Can you review my resume?"}
    )
    assert response.status_code == 401
    assert "Authentication failed" in response.json()["detail"]


def test_authentication_failure_invalid_bearer_token(client):
    """Test that invalid bearer token returns 401 Unauthorized."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.post(
        "/api/chat",
        headers=headers,
        json={"message": "How do I prepare for system design?"}
    )
    assert response.status_code == 401
    assert "bearer" in response.json()["detail"].lower() or "token" in response.json()["detail"].lower()


def test_authentication_success_valid_user(client):
    """Test that authenticated user (default_user) is accepted."""
    gemini_service._api_key = "AIzaSy_ValidKeyForTesting12345"
    mock_resp = MagicMock()
    mock_resp.text = "Great question! Let us outline your milestones."
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
    gemini_service.set_mock_client(mock_client)

    headers = {"X-User-ID": "default_user"}
    response = client.post(
        "/api/chat",
        headers=headers,
        json={"message": "Let's review my goals."}
    )
    assert response.status_code == 200
    assert response.json()["reply"] == "Great question! Let us outline your milestones."


def test_provider_error_safe_response(client):
    """Test that provider failures (500/503) return safe HTTP 502 without stack traces."""
    gemini_service._api_key = "AIzaSy_ValidKeyForTesting12345"

    mock_client = MagicMock()
    server_err = errors.ServerError(500, "Internal Google service error: https://internal.google.com/error")
    mock_client.aio.models.generate_content = AsyncMock(side_effect=server_err)
    gemini_service.set_mock_client(mock_client)

    response = client.post(
        "/api/chat",
        json={"message": "Can you give me career advice?"}
    )
    assert response.status_code in (502, 503)
    # Ensure raw Google internal URLs and tracebacks are never exposed
    assert "internal.google.com" not in response.text
    assert "traceback" not in response.text.lower()


def test_provider_timeout_safe_response(client):
    """Test that provider timeouts return safe HTTP 504 Gateway Timeout."""
    gemini_service._api_key = "AIzaSy_ValidKeyForTesting12345"

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(side_effect=asyncio.TimeoutError())
    gemini_service.set_mock_client(mock_client)

    response = client.post(
        "/api/chat",
        json={"message": "Give me a deep architectural review"}
    )
    assert response.status_code == 504
    assert "timed out" in response.json()["detail"].lower()


@pytest.mark.anyio
async def test_bounded_retries_transient_error():
    """Verify that transient 503 error is retried and recovers successfully."""
    svc = gemini_service
    svc._api_key = "AIzaSy_ValidKeyForTesting12345"

    mock_client = MagicMock()
    transient_err = errors.ServerError(503, "The model is overloaded. Please try again later.")
    success_resp = MagicMock()
    success_resp.text = "Recovered after transient overload!"

    # Fail on attempt 1, succeed on attempt 2
    mock_client.aio.models.generate_content = AsyncMock(side_effect=[transient_err, success_resp])
    svc.set_mock_client(mock_client)

    resp = await svc.send_message_async("Test prompt")
    assert resp.success is True
    assert resp.text == "Recovered after transient overload!"
    assert mock_client.aio.models.generate_content.call_count == 2


def test_security_sandbox_no_sql_or_shell_execution(client):
    """
    Test that LLM outputs attempting SQL injection or shell execution are strictly
    treated as inert plain text, never executed, and database integrity is maintained.
    """
    gemini_service._api_key = "AIzaSy_ValidKeyForTesting12345"

    malicious_text = (
        "Here is what you should do:\n"
        "```sql\nDROP TABLE user_profiles;\n```\n"
        "And run: `rm -rf /` or `dir`"
    )

    mock_resp = MagicMock()
    mock_resp.text = malicious_text
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
    gemini_service.set_mock_client(mock_client)

    response = client.post(
        "/api/chat",
        json={"message": "How do I manage databases?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "DROP TABLE user_profiles;" in data["reply"]

    # Verify that database table still exists and default user is intact
    db = SessionLocal()
    try:
        user = db.query(UserProfile).filter(UserProfile.id == "default_user").first()
        assert user is not None
        assert user.name == "Alex Morgan"
    finally:
        db.close()
