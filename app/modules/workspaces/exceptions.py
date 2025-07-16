from typing import Any

from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError


class WSDetailedHTTPException(HTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Server error"

    def __init__(self, status_code: int = None, detail: str = None, **kwargs: dict[str, Any]) -> None:
        super().__init__(
            status_code=status_code or self.STATUS_CODE,
            detail=detail or self.DETAIL,
            **kwargs,
        )


class WSNotFound(WSDetailedHTTPException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DETAIL = "Workspace not found"


class WSMembershipNotFound(WSDetailedHTTPException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DETAIL = "Workspace membership not found"


class WSMembershipPermissionDenied(WSDetailedHTTPException):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DETAIL = "Permission denied"


class WSBadRequest(WSDetailedHTTPException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL = "Bad request"


class WSInvitationBadRequest(WSDetailedHTTPException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL = "Bad request"


# ValidationError
class WSValidationError(RequestValidationError):
    STATUS_CODE: int = status.HTTP_422_UNPROCESSABLE_ENTITY
    DETAIL: str = "Validation error"

    def __init__(self, field: str, detail: str | None = None):
        msg = detail or self.__class__.DETAIL
        err_type = f"value_error.{field}_invalid"
        errors = [{"loc": ("body", field), "msg": msg, "type": err_type}]
        super().__init__(errors)
        self.status_code = self.__class__.STATUS_CODE
        self.detail = msg


class WSNameValidationError(WSValidationError):
    DETAIL = "Invalid name"

    def __init__(self, detail: str | None = None):
        super().__init__(field="name", detail=detail or self.DETAIL)
