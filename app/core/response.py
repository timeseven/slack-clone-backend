from uuid import UUID

from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from starlette import status


def make_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(v) for v in obj]
    elif isinstance(obj, UUID):
        return str(obj)
    elif hasattr(obj, "model_dump"):
        return make_serializable(obj.model_dump())
    return obj


def success_response(
    response: ORJSONResponse | None = None,
    *,
    status_code: int = status.HTTP_200_OK,
    data: BaseModel | list[BaseModel] | dict | None = None,
    message: str | None = None,
) -> ORJSONResponse:
    raw_data = data.model_dump() if isinstance(data, BaseModel) else data
    serializable_data = make_serializable(raw_data)

    payload = {
        "code": status_code,
        "message": message,
        "data": serializable_data,
    }

    if response:
        response.status_code = status_code
        response.headers["content-type"] = "application/json"
        response.body = ORJSONResponse(content=payload, status_code=status_code).body
        return response

    return ORJSONResponse(content=payload, status_code=status_code)


def error_response(
    response: ORJSONResponse | None = None,
    *,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    message: str | list[dict[str, str]] | None = None,
) -> ORJSONResponse:
    if response:
        response.status_code = status_code
        response.headers["content-type"] = "application/json"
        response.body = ORJSONResponse(content={"code": status_code, "message": message}, status_code=status_code).body
        return response

    return ORJSONResponse(content={"code": status_code, "message": message}, status_code=status_code)
