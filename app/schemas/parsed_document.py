from pydantic import BaseModel


class ParsedTextPartDTO(BaseModel):
    index: int
    text: str
    page_number: int | None = None


class ParsedDocumentStatsDTO(BaseModel):
    total_chars: int
    total_parts: int
    total_pages: int | None = None