from enum import StrEnum
from typing import Annotated, Literal
from pydantic import BaseModel, Field


class DocumentBlockType(StrEnum):
    TITLE = "title"
    SECTION_HEADER = "section_header"
    TEXT = "text"
    LIST_ITEM = "list_item"
    TABLE = "table"


class TextBlockDTO(BaseModel):
    type: Literal[
        DocumentBlockType.TITLE,
        DocumentBlockType.SECTION_HEADER,
        DocumentBlockType.TEXT,
        DocumentBlockType.LIST_ITEM,
    ]
    text: str
    hierarchy_level: int
    page_number: int | None = None


class TableBlockDTO(BaseModel):
    type: Literal[DocumentBlockType.TABLE]
    rows: list[list[str]]
    hierarchy_level: int
    page_number: int | None = None


DocumentBlockDTO = Annotated[TextBlockDTO | TableBlockDTO, Field(discriminator="type")]


class NormalizedDocumentDTO(BaseModel):
    source_name: str
    source_format: str
    blocks: list[DocumentBlockDTO]