from datetime import datetime
from typing import Generic, TypeVar
from zoneinfo import ZoneInfo

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, model_validator


def datetime_to_gmt_str(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class CustomModel(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: datetime_to_gmt_str},
        populate_by_name=True,
    )

    def serializable_dict(self, **kwargs):
        """Return a dict which contains only serializable fields."""
        default_dict = self.model_dump()

        return jsonable_encoder(default_dict)


class Pagination(CustomModel):
    page: int
    page_size: int
    total: int


class CursorPagination(CustomModel):
    before: datetime | None = None
    after: datetime | None = None
    limit: int = 20


T = TypeVar("T")


class CustomResponse(CustomModel, Generic[T]):
    code: int
    message: str
    data: T | list[T] | None = None

    @model_validator(mode="after")
    def debug_usage(self):
        print("created pydantic model")

        return self
