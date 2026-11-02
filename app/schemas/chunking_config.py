from pydantic import BaseModel, Field, model_validator
from typing import Self


class ChunkingConfig(BaseModel):
    min_tokens: int = Field(default=100, gt=0)
    target_tokens: int = Field(default=400, gt=0)
    max_tokens: int = Field(default=512, gt=0)
    overlap_tokens: int = Field(default=64, ge=0)

    @model_validator(mode="after")
    def validate_limits(self) -> Self:
        if not self.min_tokens <= self.target_tokens <= self.max_tokens:
            raise ValueError(
                "Expected min_tokens <= target_tokens <= max_tokens"
            )

        if self.overlap_tokens >= self.target_tokens:
            raise ValueError(
                "overlap_tokens must be less than target_tokens"
            )

        return self