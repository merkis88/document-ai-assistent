from datetime import UTC, datetime
from typing import Annotated, Self
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    IPvAnyAddress,
    StringConstraints,
    model_validator,
)

Sha256Hex = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class AuthSessionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID
    user_id: UUID
    refresh_token_hash: Sha256Hex
    ip: IPvAnyAddress | None = None
    user_agent: str | None = Field(default=None, max_length=512)
    expires_at: AwareDatetime

    @model_validator(mode="after")
    def _validate_expiration(self) -> Self:
        if self.expires_at <= datetime.now(UTC):
            raise ValueError("Session expiration must be in the future")
        return self