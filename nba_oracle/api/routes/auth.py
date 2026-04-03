from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from nba_oracle.api.dependencies import get_request_actor, require_bootstrapped_auth
from nba_oracle.auth import create_access_token, verify_password
from nba_oracle.config import ORACLE_PASSWORD_HASH, ORACLE_TOKEN_TTL_MINUTES
from nba_oracle.security import check_login_allowed, check_rate_limit, clear_failed_logins, log_auth_event, record_failed_login


router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    password: str


@router.post("/login")
def login(payload: LoginRequest, request: Request) -> dict[str, object]:
    require_bootstrapped_auth()
    actor = get_request_actor(request)
    rate_limit = check_rate_limit(actor)
    if not rate_limit.allowed:
        log_auth_event("login_rate_limited", actor=actor, detail=rate_limit.reason)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=rate_limit.reason,
            headers={"Retry-After": str(rate_limit.retry_after_seconds)},
        )
    allowed = check_login_allowed(actor)
    if not allowed.allowed:
        log_auth_event("login_blocked", actor=actor, detail=allowed.reason)
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=allowed.reason)
    if not verify_password(payload.password, ORACLE_PASSWORD_HASH):
        record_failed_login(actor)
        log_auth_event("login_failed", actor=actor, detail="invalid_credentials")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials")
    clear_failed_logins(actor)
    log_auth_event("login_success", actor=actor, detail="operator")
    token = create_access_token(
        subject="oracle-operator",
        extra={"role": "operator", "actor": actor},
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in_minutes": ORACLE_TOKEN_TTL_MINUTES,
        "role": "operator",
    }
