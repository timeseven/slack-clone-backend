from typing import Any

from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError


class UserDetailedHTTPException(HTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Server error"

    def __init__(self, status_code: int = None, detail: str = None, **kwargs: dict[str, Any]) -> None:
        super().__init__(
            status_code=status_code or self.STATUS_CODE,
            detail=detail or self.DETAIL,
            **kwargs,
        )


class UserInvalidCredentials(UserDetailedHTTPException):
    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    DETAIL = "Invalid credentials"


class UserNotFound(UserDetailedHTTPException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DETAIL = "User not found"


class UserBadRequest(UserDetailedHTTPException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL = "User created failed"


class UserPermissionDenied(UserDetailedHTTPException):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DETAIL = "Permission denied"


# ValidationError
class UserValidationError(RequestValidationError):
    STATUS_CODE: int = status.HTTP_422_UNPROCESSABLE_ENTITY
    DETAIL: str = "Validation error"

    def __init__(self, field: str, detail: str | None = None):
        msg = detail or self.__class__.DETAIL
        err_type = f"value_error.{field}_invalid"
        errors = [{"loc": ("body", field), "msg": msg, "type": err_type}]
        super().__init__(errors)
        self.status_code = self.__class__.STATUS_CODE
        self.detail = msg


class UserEmailValidationError(UserValidationError):
    DETAIL = "Invalid email"

    def __init__(self, detail: str | None = None):
        super().__init__(field="email", detail=detail or self.DETAIL)


class UserPasswordValidationError(UserValidationError):
    DETAIL = "Invalid password"

    def __init__(self, detail: str | None = None):
        super().__init__(field="password", detail=detail or self.DETAIL)
