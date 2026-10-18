from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class DocumentBlockType(StrEnum):
    TITLE = "title"
    TEXT = "text"
    SECTION_HEADER = "section_header"
    LIST_ITEM = "list_item"
    TABLE = "table"


class BlockBase(BaseModel):
    hierarchy_level: int = Field(ge=0)
    pages: list[int] = Field(default_factory=list)


class TextBlock(BlockBase):
    type: Literal[
        DocumentBlockType.TITLE,
        DocumentBlockType.TEXT,
    ]
    text: str
    semantic_role: str | None = None


class SectionHeaderBlock(BlockBase):
    type: Literal[DocumentBlockType.SECTION_HEADER]
    text: str
    heading_level: int = Field(ge=1)


class ListItemBlock(BlockBase):
    type: Literal[DocumentBlockType.LIST_ITEM]
    text: str
    enumerated: bool
    marker: str


class TableCell(BaseModel):
    text: str

    row_start: int = Field(ge=0)
    row_end: int = Field(ge=0)

    col_start: int = Field(ge=0)
    col_end: int = Field(ge=0)

    row_span: int = Field(ge=1)
    col_span: int = Field(ge=1)

    column_header: bool = False
    row_header: bool = False
    row_section: bool = False


class TableBlock(BlockBase):
    type: Literal[DocumentBlockType.TABLE]

    num_rows: int = Field(ge=0)
    num_cols: int = Field(ge=0)

    cells: list[TableCell]


DocumentBlock = Annotated[TextBlock | SectionHeaderBlock | ListItemBlock | TableBlock, Field(discriminator="type")]


class NormalizedDocument(BaseModel):
    source_name: str
    mime_type: str | None = None
    blocks: list[DocumentBlock]