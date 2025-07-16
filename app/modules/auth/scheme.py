from typing import Annotated, Any, cast

from fastapi import Cookie
from fastapi.openapi.models import OAuthFlows
from fastapi.security import OAuth2

from app.core.config import settings
from app.modules.auth.exceptions import InvalidCredentials


class CookieJWTAuth(OAuth2):
    def __init__(
        self,
        tokenUrl: str = "",
        scopes: dict[str, str] = {},
    ):
        super().__init__(
            flows=OAuthFlows(password=cast(Any, {"tokenUrl": tokenUrl, "scopes": scopes})),
            scheme_name="Cookie",
            auto_error=True,
        )

    async def __call__(
        self,
        access_token: Annotated[
            str | None,
            Cookie(alias="access_token"),
        ] = None,
    ):
        if access_token is None:
            raise InvalidCredentials
        return access_token


oauth2_scheme = CookieJWTAuth(tokenUrl=f"{settings.API_V1_STR}/auth/login")
