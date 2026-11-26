from dataclasses import dataclass, field


@dataclass
class TextFragment:
    text_parts: str
    block_start_index: int
    block_end_index: int
    pages: set[int] = field(default_factory=set)