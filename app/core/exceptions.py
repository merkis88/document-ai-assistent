from fastapi import HTTPException, status


class AppError(HTTPException):
    """Base domain error mapped to an HTTP response."""

    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail: str | None = None, **kwargs):
        super().__init__(status_code=self.status_code, detail=detail or self.__doc__, **kwargs)


class InvalidTokenError(AppError):
    """Invalid authentication token."""
    status_code = status.HTTP_401_UNAUTHORIZED


class TokenExpiredError(AppError):
    """Authentication token has expired."""
    status_code = status.HTTP_401_UNAUTHORIZED