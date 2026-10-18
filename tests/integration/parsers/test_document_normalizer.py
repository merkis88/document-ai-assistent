from pathlib import Path

from app.schemas.normalized_document import (
    DocumentBlockType,
    ListItemBlock,
    NormalizedDocument,
    SectionHeaderBlock,
    TableBlock,
    TextBlock,
)
from app.services.rag.parsers.document_normalizer import DocumentNormalizer
from app.services.rag.parsers.docling_parser import DoclingParser

FIXTURES_DIR = Path(__file__).parents[2] / "fixtures" / "documents"
DOCX_PATH = FIXTURES_DIR / "docling_sample.docx"


def test_normalize_docx() -> None:
    parser = DoclingParser()
    normalizer = DocumentNormalizer()

    parsed_document = parser.parse(DOCX_PATH)
    document = normalizer.normalize(parsed_document)

    assert isinstance(document, NormalizedDocument)
    assert document.blocks

    assert any(
        isinstance(block, TextBlock)
        and block.type == DocumentBlockType.TITLE
        for block in document.blocks
    )

    assert any(
        isinstance(block, SectionHeaderBlock)
        for block in document.blocks
    )

    assert any(
        isinstance(block, ListItemBlock)
        for block in document.blocks
    )

    tables = [
        block
        for block in document.blocks
        if isinstance(block, TableBlock)
    ]

    assert tables

    table = tables[0]

    assert table.num_rows > 0
    assert table.num_cols > 0
    assert table.cells

    assert all(cell.row_start >= 0 for cell in table.cells)
    assert all(cell.col_start >= 0 for cell in table.cells)