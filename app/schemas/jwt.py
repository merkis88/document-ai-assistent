from datetime import datetime
from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenPayload(BaseModel):
    sub: UUID
    type: TokenType
    exp: datetime