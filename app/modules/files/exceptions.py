from typing import Any

from fastapi import HTTPException, status


class FileDetailedHTTPException(HTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Server error"

    def __init__(self, status_code: int = None, detail: str = None, **kwargs: dict[str, Any]) -> None:
        super().__init__(
            status_code=status_code or self.STATUS_CODE,
            detail=detail or self.DETAIL,
            **kwargs,
        )


class FileBadRequest(FileDetailedHTTPException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL = "Failed to upload file"


class FilePermissionDenied(FileDetailedHTTPException):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DETAIL = "Permission denied"
