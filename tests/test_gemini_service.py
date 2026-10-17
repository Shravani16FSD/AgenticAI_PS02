"""
Unit and integration tests for Google Gemini integration in Chapter / SkillTrace AI backend.
Validates:
1. Official google-genai SDK compatibility.
2. Missing key and placeholder detection (no crash, safe fallback).
3. Invalid API key handling (APIError/ClientError 400/403).
4. Quota and rate limit errors (ClientError 429).
5. Timeout handling (asyncio.TimeoutError).
6. Server and provider failure handling (ServerError 500/503).
7. Model configurability (GEMINI_MODEL).
8. Strict credential safety (API key never leaked in responses, errors, or dicts).
9. Integration with FastAPI /api/chat router endpoints.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient

from backend.app.gemini_service import GeminiService, GeminiResponse
from backend.app.config import settings
from backend.app.main import app
from google.genai import errors


@pytest.fixture
def test_client():
    return TestClient(app)


def test_missing_api_key_detection():
    """Verify service gracefully detects unconfigured or placeholder keys."""
    # Empty key
    svc_empty = GeminiService(api_key="")
    assert svc_empty.is_configured is False

    # Default placeholder key
    svc_placeholder = GeminiService(api_key="your_gemini_api_key_here")
    assert svc_placeholder.is_configured is False

    # Whitespace key
    svc_whitespace = GeminiService(api_key="   ")
    assert svc_whitespace.is_configured is False

    # Synchronous call should not raise and return safe fallback
    resp_sync = svc_empty.send_message("What skills do I need for AI?")
    assert resp_sync.success is False
    assert resp_sync.status == "missing_key"
    assert resp_sync.is_fallback is True
    assert "offline contextual mode" in resp_sync.text


@pytest.mark.anyio
async def test_missing_api_key_async():
    """Verify async calls with missing key return safe fallback without crashing."""
    svc = GeminiService(api_key="")
    resp = await svc.send_message_async("How can I become an AI engineer?")
    assert resp.success is False
    assert resp.status == "missing_key"
    assert resp.is_fallback is True
    assert "offline contextual mode" in resp.text


def test_configurable_model_selection():
    """Verify model selection is configurable at initialization and per-request."""
    svc = GeminiService(api_key="test-key-12345", model="gemini-2.5-flash")
    assert svc.model == "gemini-2.5-flash"

    svc_custom = GeminiService(api_key="test-key-12345", model="gemini-2.5-pro")
    assert svc_custom.model == "gemini-2.5-pro"


@pytest.mark.anyio
async def test_mocked_gemini_success():
    """Verify successful response generation with a mocked Google GenAI client."""
    svc = GeminiService(api_key="AIzaSyTestValidFakeKey1234567890", model="gemini-2.5-flash")

    # Mock response
    mock_resp = MagicMock()
    mock_resp.text = "Focus on Python AST analysis, FastAPI REST design, and vector indexing."

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_resp
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)

    svc.set_mock_client(mock_client)

    # Test sync
    resp_sync = svc.send_message("Give me a study plan")
    assert resp_sync.success is True
    assert resp_sync.status == "success"
    assert "Python AST analysis" in resp_sync.text

    # Test async
    resp_async = await svc.send_message_async("Give me a study plan")
    assert resp_async.success is True
    assert resp_async.status == "success"
    assert "FastAPI REST design" in resp_async.text


@pytest.mark.anyio
async def test_invalid_key_handling():
    """Verify 400/403 invalid key errors are caught and categorized safely without crashing."""
    raw_key = "AIzaSy_FAKE_INVALID_KEY_99999"
    svc = GeminiService(api_key=raw_key)

    mock_client = MagicMock()
    # Simulate Google GenAI ClientError on invalid key
    client_err = errors.ClientError(400, "API key not valid. Please pass a valid API key.")
    mock_client.aio.models.generate_content = AsyncMock(side_effect=client_err)
    mock_client.models.generate_content.side_effect = client_err
    svc.set_mock_client(mock_client)

    resp = await svc.send_message_async("Test career question")
    assert resp.success is False
    assert resp.status == "invalid_key"
    assert resp.is_fallback is True
    assert "Authentication failed" in resp.error_detail
    # Never expose key in error detail or text
    assert raw_key not in resp.error_detail
    assert raw_key not in resp.text


@pytest.mark.anyio
async def test_quota_error_handling():
    """Verify 429 quota exhaustion is caught and handled safely."""
    svc = GeminiService(api_key="AIzaSyTestQuotaKey")

    mock_client = MagicMock()
    quota_err = errors.ClientError(429, "Resource has been exhausted (e.g. check quota).")
    mock_client.aio.models.generate_content = AsyncMock(side_effect=quota_err)
    svc.set_mock_client(mock_client)

    resp = await svc.send_message_async("Test career question")
    assert resp.success is False
    assert resp.status == "quota_exceeded"
    assert resp.is_fallback is True
    assert "quota" in resp.error_detail.lower()


@pytest.mark.anyio
async def test_timeout_handling():
    """Verify timeouts are intercepted without crashing the server."""
    svc = GeminiService(api_key="AIzaSyTestTimeoutKey", timeout_seconds=0.1)

    mock_client = MagicMock()

    async def slow_call(*args, **kwargs):
        await asyncio.sleep(0.5)
        mock_r = MagicMock()
        mock_r.text = "Slow response"
        return mock_r

    mock_client.aio.models.generate_content = AsyncMock(side_effect=slow_call)
    svc.set_mock_client(mock_client)

    resp = await svc.send_message_async("Long running request")
    assert resp.success is False
    assert resp.status == "timeout"
    assert resp.is_fallback is True
    assert "timed out" in resp.error_detail.lower()


@pytest.mark.anyio
async def test_server_error_handling():
    """Verify 500/503 server errors are intercepted safely."""
    svc = GeminiService(api_key="AIzaSyTestServerKey")

    mock_client = MagicMock()
    server_err = errors.ServerError(503, "The model is overloaded. Please try again later.")
    mock_client.aio.models.generate_content = AsyncMock(side_effect=server_err)
    svc.set_mock_client(mock_client)

    resp = await svc.send_message_async("Test query during outage")
    assert resp.success is False
    assert resp.status == "provider_error"
    assert resp.is_fallback is True
    assert "unavailable" in resp.error_detail.lower() or "overloaded" in resp.error_detail.lower()


def test_api_key_never_exposed_in_dict_or_sanitize():
    """Verify that credentials are strictly sanitized and never leaked."""
    secret = "AIzaSySuperSecretKey987654321012345"
    svc = GeminiService(api_key=secret)

    # Test sanitizer
    leak_string = f"Error communicating with Gemini at https://api.google.com?key={secret}"
    sanitized = svc._sanitize(leak_string)
    assert secret not in sanitized
    assert "[REDACTED_API_KEY]" in sanitized

    # Test response to_dict
    resp = GeminiResponse(
        text="Normal response",
        success=True,
        status="success",
        model="gemini-2.5-flash",
        error_detail=f"Occurred while using {secret}"
    )
    # Sanitize before creating dict
    resp.error_detail = svc._sanitize(resp.error_detail)
    d = resp.to_dict()
    assert secret not in str(d)


def test_chat_provider_status_endpoint(test_client):
    """Verify /api/chat/status exposes provider metadata without exposing secrets."""
    response = test_client.get("/api/chat/status")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "google-gemini"
    assert data["sdk"] == "google-genai"
    assert "model" in data
    assert "configured" in data
    # Guarantee no key or secret attributes exist in JSON payload
    assert "api_key" not in data
    assert "key" not in data
    assert "secret" not in data


def test_chat_message_fallback_streaming(test_client):
    """Verify /api/chat produces valid streaming response even when Gemini key is unconfigured."""
    response = test_client.post(
        "/api/chat?stream=true",
        json={"message": "What should I learn to become an AI engineer?"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    content = response.text
    assert len(content) > 50
    # Confirms resilient contextual advice is delivered
    assert "AI Product Engineering" in content or "Roadmap" in content
