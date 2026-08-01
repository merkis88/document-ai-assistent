from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class TextChunkDTO:
    index: int
    text: str
    start_char: int
    end_char: int
    page_number: int | None = None

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

