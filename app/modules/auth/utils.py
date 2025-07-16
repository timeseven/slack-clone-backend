from datetime import datetime, timedelta, timezone

import jwt
from fastapi.responses import ORJSONResponse

COMMON_COOKIE_PARAMS = {
    "path": "/",
    "domain": None,
    "httponly": True,
    "secure": True,
    "samesite": "lax",
}


# Token
def generate_token(
    token_type: str,
    secret_key: str,
    algorithm: str,
    expires_minutes: int,
    user_id: str,
) -> dict:
    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(minutes=expires_minutes)

    token_payload = {
        "sub": user_id,
        "iat": created_at,
        "exp": expires_at,
        "type": token_type,
    }

    token = jwt.encode(
        payload=token_payload,
        key=secret_key,
        algorithm=algorithm,
    )

    return token, expires_at


# Cookie
def set_token_cookies(
    response: ORJSONResponse,
    access_token: str | None = None,
    access_expires_at: datetime | None = None,
    refresh_token: str | None = None,
    refresh_expires_at: datetime | None = None,
):
    if access_token and access_expires_at:
        response.set_cookie(
            key="access_token",
            value=access_token,
            expires=access_expires_at,
            **COMMON_COOKIE_PARAMS,
        )

    if refresh_token and refresh_expires_at:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            expires=refresh_expires_at,
            **COMMON_COOKIE_PARAMS,
        )
