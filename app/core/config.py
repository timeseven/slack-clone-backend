from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BeforeValidator, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    PROJECT_NAME: str
    FRONTEND_HOST: str
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [self.FRONTEND_HOST]

    # JWT settings
    ALGORITHM: str = "HS256"
    ACCESS_SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 2  # 15 mins
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 2  # 2 days

    # Database settings
    DATABASE_URL: PostgresDsn
    MIN_CONNECTIONS: int = 10
    MAX_CONNECTIONS: int = 20
    POOL_RECYCLE: int = 3600
    POOL_PRE_PING: bool = True
    POOL_TIMEOUT: int = 30
    ECHO: bool = False

    # Redis settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DEFAULT_DB: int = 0
    REDIS_ARQ_DB: int = 1
    REDIS_SOCKET_IO_DB: int = 2

    # SMTP settings
    SMTP_ENABLED: bool = True
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_SSL: bool = True
    SMTP_TLS: bool = True
    SMTP_USER: str
    SMTP_PASSWORD: str

    # AWS settings
    AWS_S3_BUCKET_NAME: str
    AWS_S3_ACCESS_KEY_ID: str
    AWS_S3_SECRET_KEY_ID: str
    AWS_REGION: str


settings = Config()
