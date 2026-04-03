from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from nba_oracle.auth import decode_access_token
from nba_oracle.config import ORACLE_PASSWORD_HASH
from nba_oracle.security import check_rate_limit


bearer_scheme = HTTPBearer(auto_error=False)


def get_request_actor(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def require_bootstrapped_auth() -> None:
    if not ORACLE_PASSWORD_HASH:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="auth_not_bootstrapped",
        )


def require_authenticated_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    require_bootstrapped_auth()
    actor = get_request_actor(request)
    decision = check_rate_limit(actor)
    if not decision.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=decision.reason,
            headers={"Retry-After": str(decision.retry_after_seconds)},
        )
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing_bearer_token")
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return payload
