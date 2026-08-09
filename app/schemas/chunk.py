from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class TextChunkDTO:
    index: int
    text: str
    start_char: int
    end_char: int

    # PDF:
    page_number: int | None = None

    # DOCX:
    paragraph_index: int | None = None

    # TXT
    start_byte: int | None = None
    end_byte: int | None = None

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("Chunk index cannot be negative")

        if not self.text:
            raise ValueError("Chunk content cannot be empty")

        if self.start_char < 0:
            raise ValueError("start_char cannot be negative")

        if self.end_char <= self.start_char:
            raise ValueError("end_char must be greater than start_char")

        if self.page_number is not None and self.page_number <= 0:
            raise ValueError("page_number must be greater than 0")

        if self.paragraph_index is not None and self.paragraph_index < 0:
            raise ValueError("paragraph_index cannot be negative")

        if self.start_byte is not None and self.start_byte < 0:
            raise ValueError("start_byte cannot be negative")

        if self.end_byte is not None and self.end_byte < 0:
            raise ValueError("end_byte cannot be negative")

        if self.start_byte is not None and self.end_byte is not None and self.end_byte <= self.start_byte:
            raise ValueError("end_byte must be greater than start_byte")

