from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    field_serializer,
)


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    sub: UUID  # user id
    sid: UUID  # session id
    jti: UUID  # unique token id
    type: TokenType
    iss: str
    aud: str
    iat: AwareDatetime
    exp: AwareDatetime

    @field_serializer("iat", "exp")
    def _serialize_timestamp(self, value: datetime) -> int:
        return int(value.timestamp())