from pydantic import BaseModel


class SourceLocationDTO(BaseModel):
    # PDF:
    # Image of the source document page
    page_number: int | None = None

    # DOCX:
    # paragraph number in the document structure
    paragraph_index: int | None = None

    # TXT:
    # physical position in the source file.
    start_byte: int | None = None
    end_byte: int | None = None


class ParsedTextPartDTO(BaseModel):
    # A small part of the text that the parser passes on.
    text: str

    # Information about where this part was extracted from.
    location: SourceLocationDTO