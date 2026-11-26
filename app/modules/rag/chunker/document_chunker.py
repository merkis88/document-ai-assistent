import re

from app.modules.rag.chunker.token_counting import TokenCounter
from app.schemas.normalized_document import (
    NormalizedDocument,
    SectionHeaderBlock,
    TextBlock,
    ListItemBlock,
    TableBlock,
)
from app.schemas.chunk import ParentChunk, ChildChunk
from app.schemas.chunking_config import ChunkingConfig
from app.modules.rag.chunker.fragment_schema import TextFragment
from app.core.errors.exceptions import AppError
from app.core.errors.codes import ErrorCode


class DocumentChunker:
    def __init__(
        self,
        token_counter: TokenCounter,
        last_token:TokenCounter,
        chunking_conf: ChunkingConfig
    ) -> None:
        self._token_counter = token_counter
        self._config = chunking_conf
        self._last_token = last_token

    def chunk(self, document: NormalizedDocument) -> list[ParentChunk]:
        headings: list[tuple[int, str]] = []
        chunks: list[Chunk] = []
        fragments: list[TextFragment] = []

        for index, block in enumerate(document.blocks):
            if isinstance(block, SectionHeaderBlock):
                if fragments:
                    chunks.append(
                        self._build_chunk(
                            index=len(chunks),
                            headings=headings,
                            fragments=fragments,
                        )
                    )
                    fragments.clear()

                while headings and headings[-1][0] >= block.heading_level:
                    headings.pop()

                headings.append((block.heading_level, block.text))
                continue

            text = ""

            if isinstance(block, (TextBlock, ListItemBlock)):
                text = block.text.strip()

            elif isinstance(block, TableBlock):
                if not block.cells:
                    continue

                rows: dict[int, list[tuple[int, str]]] = {}
                for cell in block.cells:
                    rows.setdefault(cell.row_start, []).append((cell.col_start, cell.text.strip()))

                table_rows: list[str] = []
                for row_index in sorted(rows):
                    cells = sorted(rows[row_index], key=lambda item: item[0])
                    row_text = " | ".join(cell_text for _, cell_text in cells)
                    if row_text.strip(" |"):
                        table_rows.append(row_text)

                if table_rows:
                    text = "\n".join(table_rows)

            if text:
                fragments.append(
                    TextFragment(
                        text=text,
                        block_start_index=index,
                        block_end_index=index,
                        pages=set(block.pages),
                    )
                )

        if fragments:
            chunks.append(
                self._build_chunk(
                    index=len(chunks),
                    headings=headings,
                    fragments=fragments,
                )
            )

        return chunks

    def _split_text(self, text: str) -> list[str]:
        combined_text: list[str] = []
        current_text: str = ""
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())

        for sentence in sentences:
            if not sentence:
                raise ValueError("Empty sentence")
            if self._token_counter.count(sentence) > self._config.max_tokens:
                raise AppError(code=ErrorCode.TOO_MANY_TOKENS)

            candidate = f"{current_text} {sentence}".strip()

            quantity_tokens = self._token_counter.count(candidate)

            if quantity_tokens > self._config.max_tokens:
                if current_text:
                    overlap_text = self._last_token.last_token_count(current_text, self._config.overlap_tokens)
                    combined_text.append(current_text)

                    new_overlap_text = f"{overlap_text} {sentence}".strip()

                    if self._token_counter.count(new_overlap_text) > self._config.max_tokens:
                        # TODO: Continue parent chunk splitting logic                    else:
                        current_text = new_overlap_text
                else:
                    current_text = candidate
        return combined_text

    def _build_chunk(
        self,
        *,
        index: int,
        headings: list[tuple[int, str]],
        fragments: list[TextFragment],
    ) -> ParentChunk:
        if not fragments:
            raise ValueError("Cannot build chunk from empty fragments")

        text = "\n".join(fragment.text for fragment in fragments)
        pages = {page for fragment in fragments for page in fragment.pages}

        return ParentChunk(
            index=index,
            text=text,
            token_count=self._token_counter.count(text),
            pages=sorted(pages),
            section_path=[title for _, title in headings],
            block_start_index=fragments[0].block_start_index,
            block_end_index=fragments[-1].block_end_index,
        )
