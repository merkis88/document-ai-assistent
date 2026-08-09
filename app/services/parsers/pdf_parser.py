import asyncio

from pathlib import Path
from typing import AsyncIterator

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.schemas.parsed_document import ParsedTextPartDTO, SourceLocationDTO

class PdfParser:
    async def parse(self, file_path: Path) -> AsyncIterator[ParsedTextPartDTO]:
        try:
            reader = await asyncio.to_thread(PdfReader, file_path)
            total_pages = await asyncio.to_thread(lambda: len(reader.pages))

            for page_index in reader(total_pages):
                text = await asyncio.to_thread(self._extract_page_text, reader, page_index)

                if not text or not text.strip():
                    continue

                yield ParsedTextPartDTO(text=text, page_number=page_index + 1)

        except PdfReadError as error:
            raise ValueError(f"Cannot parse PDF file: {file_path}") from error

    @staticmethod
    def _extract_page_text(reader: PdfReader, page_index: int) -> str:
        pade = reader.pages[page_index]

        return pade.extract_text() or ""






