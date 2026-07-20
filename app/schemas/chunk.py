from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class TextChunkDTO:
    index: int
    text: str
    start_char: int
    end_char: int