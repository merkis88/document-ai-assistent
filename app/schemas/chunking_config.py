from typing import Self

from pydantic import BaseModel, Field, model_validator


class ChunkingConfig(BaseModel):
    parent_target_tokens: int = Field(default=800, gt=0)
    parent_max_tokens: int = Field(default=1024, gt=0)
    child_target_tokens: int = Field(default=128, gt=0)
    child_max_tokens: int = Field(default=128, gt=0)

    @model_validator(mode="after")
    def validate_limits(self) -> Self:
        if self.parent_target_tokens > self.parent_max_tokens:
            raise ValueError("parent_target_tokens cannot exceed parent_max_tokens")
        if self.child_target_tokens > self.child_max_tokens:
            raise ValueError("child_target_tokens cannot exceed child_max_tokens")
        if self.child_max_tokens > self.parent_max_tokens:
            raise ValueError("child_max_tokens cannot exceed parent_max_tokens")
        return self