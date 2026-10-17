from app.core.errors.codes import ErrorCode


class ApplicationError(Exception):
    def __init__(self, code: ErrorCode, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)