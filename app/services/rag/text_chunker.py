from app.schemas.chunk import TextChunkDTO

class TextChunker:
    BREAKPOINTS = ("\n\n", ". ", "! ", "? ", "; ", "\n", " ")

    MIN_BOUNDARY_RATIO = 0.6

    def __init__(self, chunk_size: int = 500, overlap: int = 75) -> None:
        if not isinstance(chunk_size, int):
            raise TypeError("chunk_size must be an integer")

        if not isinstance(overlap, int):
            raise TypeError("overlap must be an integer")

        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text: str, *, page_number: int | None = None) -> list[TextChunkDTO]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if page_number is not None and page_number <= 0:
            raise ValueError("page_number must be greater than 0")

        if not text.strip():
            return []

        chunks: list[TextChunkDTO] = []
        start = 0
        text_length = len(text)

        while start < text_length:
            start = self._skip_whitespace(text=text, position=start)

            if start > text_length:
                break

            maximum_end = min(start + self.chunk_size, text_length)

            end = self._find_chunk_end(text=text, start=start, maximum_end=maximum_end)

            raw_chunk = text[start:end]
            left_spaces = len(raw_chunk) - len(raw_chunk.lstrip())
            chunk_text = raw_chunk.strip()

            actual_start = start + left_spaces
            actual_end = actual_start + len(chunk_text)

            if chunk_text:
                chunks.append(TextChunkDTO(index=len(chunks), text=chunk_text, start_char=actual_start, end_char=actual_end, page_number=page_number))

            if end >= text_length:
                break

            next_start = max(actual_end - self.overlap, start + 1)

            start = self._move_to_word_boundary(text=text, position=next_start, upper_bound=actual_end)

        return chunks

    def _find_chunk_end(self, text: str, start: int, maximum_end: int) -> int:
        if maximum_end >= len(text):
            return len(text)

        minimum_end = start + int((maximum_end - start) * self.MIN_BOUNDARY_RATIO)

        for breakpoint in self.BREAKPOINTS:
            position = text.rfind(
                breakpoint,
                minimum_end,
                maximum_end,
            )

            if position != -1:
                return position + len(breakpoint)

        return maximum_end

    @staticmethod
    def _skip_whitespace(text: str, position: int) -> int:
        while position < len(text) and text[position].isspace():
            position += 1

        return position

    @staticmethod
    def _move_to_word_boundary(text: str, position: int, upper_bound: int) -> int:

        while ( position < upper_bound and position > 0 and text[position - 1].isalnum() and text[position].isalnum()):
            position += 1

        return position