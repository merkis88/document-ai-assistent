from pathlib import Path

import pytest
from docling_core.types.doc import DoclingDocument

from app.core.errors.codes import ErrorCode
from app.core.errors.exceptions import ApplicationError
from app.services.rag.parsers.docling_parser import DoclingParser


FIXTURES_DIR = Path("tests/fixtures/documents")
DOCX_FILE = FIXTURES_DIR / "docling_sample.docx"
TXT_FILE = FIXTURES_DIR / "docling_sample.txt"


def test_parse_docx_returns_docling_document() -> None:
    parser = DoclingParser()

    document = parser.parse(DOCX_FILE)

    assert isinstance(document, DoclingDocument)
    assert list(document.iterate_items())


def test_parse_txt_returns_docling_document() -> None:
    parser = DoclingParser()

    document = parser.parse(TXT_FILE)

    assert isinstance(document, DoclingDocument)
    assert list(document.iterate_items())


def test_inspect_docx_structure() -> None:
    """Run with pytest -s to inspect the real Docling output."""
    parser = DoclingParser()
    document = parser.parse(DOCX_FILE)

    items = list(document.iterate_items())
    assert items

    for item, level in items:
        print("\n---")
        print("TYPE:", type(item).__name__)
        print("LEVEL:", level)
        print("LABEL:", getattr(item, "label", None))
        print("TEXT:", getattr(item, "text", None))
        print("PROV:", getattr(item, "prov", None))


def test_unsupported_extension() -> None:
    parser = DoclingParser()
    unsupported_file = FIXTURES_DIR / "unsupported.exe"
    unsupported_file.write_text("not a supported document", encoding="utf-8")

    try:
        with pytest.raises(ApplicationError) as exc_info:
            parser.parse(unsupported_file)

        assert exc_info.value.code == ErrorCode.UNSUPPORTED_DOCUMENT_FORMAT
    finally:
        unsupported_file.unlink(missing_ok=True)
