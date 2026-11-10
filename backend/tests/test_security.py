from fastapi import HTTPException
import pytest

from app.core.config import settings
from app.core.security import verify_agent_token


def test_ingest_token_optional_when_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "AGENT_TOKEN", "")
    assert verify_agent_token(None) is None


def test_ingest_token_rejects_missing_or_invalid(monkeypatch):
    monkeypatch.setattr(settings, "AGENT_TOKEN", "example-secret")
    for value in (None, "Bearer wrong", "Basic example-secret", "Bearer"):
        with pytest.raises(HTTPException) as error:
            verify_agent_token(value)
        assert error.value.status_code == 401


def test_ingest_token_accepts_matching_bearer(monkeypatch):
    monkeypatch.setattr(settings, "AGENT_TOKEN", "example-secret")
    assert verify_agent_token("Bearer example-secret") is None
