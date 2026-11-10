"""Optional ingest authentication for local development and deployed agents."""

from hmac import compare_digest

from fastapi import Header, HTTPException, status

from app.core.config import settings


def verify_agent_token(authorization: str | None = Header(default=None)) -> None:
    """Require Authorization: Bearer <token> when AGENT_TOKEN is configured."""
    configured = settings.AGENT_TOKEN
    if not configured:
        return
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not compare_digest(token, configured):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing agent token",
            headers={"WWW-Authenticate": "Bearer"},
        )
