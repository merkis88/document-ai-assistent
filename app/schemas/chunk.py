from pydantic import BaseModel, Field


class Chunk(BaseModel):
    index: int = Field(ge=0)
    text: str = Field(min_length=1)
    token_count: int = Field(gt=0)
    pages: list[int] = Field(default_factory=list)
    section_path: list[str] = Field(default_factory=list)
    block_start_index: int = Field(ge=0)
    block_end_index: int = Field(ge=0)