from pydantic import BaseModel


class ParsedPageDTO(BaseModel):
    page_number: int | None = None
    text: str


class ParsedDocumentDTO(BaseModel):
    pages: list[ParsedPageDTO]
    total_chars: int
    total_pages: int | None = None
