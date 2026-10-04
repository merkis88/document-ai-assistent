import asyncio

import pytest

from pypdf.errors import PdfReadError

import app.services.rag.parsers.pdf_parser as pdf_parser_module
from app.services.rag.parsers.pdf_parser import PdfParser


class FakePage:
    def __init__(self, text: str | None) -> None:
        self.text = text
        self.extract_calls = 0

    def extract_text(self) -> str | None:
        self.extract_calls += 1
        return self.text


class FakeReader:
    def __init__(self, pages: list[FakePage]) -> None:
        self.pages = pages


async def _collect_parts(parser: PdfParser, file_path):
    return [part async for part in parser.parse(file_path)]


def test_parse_returns_text_with_correct_page_numbers(monkeypatch, tmp_path) -> None:
    file_path = tmp_path / "document.pdf"
    file_path.write_bytes(b"%PDF-1.4")

    pages = [
        FakePage("First page"),
        FakePage("Second page"),
    ]

    monkeypatch.setattr(
        pdf_parser_module,
        "PdfReader",
        lambda _: FakeReader(pages),
    )

    parser = PdfParser()
    parts = asyncio.run(_collect_parts(parser, file_path))

    assert len(parts) == 2

    assert parts[0].text == "First page"
    assert parts[0].location.page_number == 1

    assert parts[1].text == "Second page"
    assert parts[1].location.page_number == 2


def test_parse_skips_pages_without_text(monkeypatch, tmp_path) -> None:
    file_path = tmp_path / "document.pdf"
    file_path.write_bytes(b"%PDF-1.4")

    pages = [
        FakePage("First page"),
        FakePage(None),
        FakePage("   "),
        FakePage("Fourth page"),
    ]

    monkeypatch.setattr(
        pdf_parser_module,
        "PdfReader",
        lambda _: FakeReader(pages),
    )

    parser = PdfParser()
    parts = asyncio.run(_collect_parts(parser, file_path))

    assert len(parts) == 2

    assert parts[0].text == "First page"
    assert parts[0].location.page_number == 1

    assert parts[1].text == "Fourth page"
    assert parts[1].location.page_number == 4


def test_parse_does_not_extract_all_pages_before_first_yield(monkeypatch, tmp_path) -> None:
    file_path = tmp_path / "document.pdf"
    file_path.write_bytes(b"%PDF-1.4")

    first_page = FakePage("First page")
    second_page = FakePage("Second page")

    monkeypatch.setattr(
        pdf_parser_module,
        "PdfReader",
        lambda _: FakeReader([first_page, second_page]),
    )

    parser = PdfParser()

    async def get_first_part():
        generator = parser.parse(file_path)

        try:
            return await anext(generator)
        finally:
            await generator.aclose()

    part = asyncio.run(get_first_part())

    assert part.text == "First page"

    assert first_page.extract_calls == 1
    assert second_page.extract_calls == 0


def test_parse_converts_pdf_read_error_to_value_error(monkeypatch, tmp_path) -> None:
    file_path = tmp_path / "broken.pdf"
    file_path.write_bytes(b"%PDF-broken")

    def broken_reader(_):
        raise PdfReadError("Broken PDF")

    monkeypatch.setattr(
        pdf_parser_module,
        "PdfReader",
        broken_reader,
    )

    parser = PdfParser()

    with pytest.raises(ValueError, match="Cannot parse PDF file"):
        asyncio.run(_collect_parts(parser, file_path))


def test_extract_page_text_returns_empty_string_for_none() -> None:
    reader = FakeReader([
        FakePage(None),
    ])

    text = PdfParser._extract_page_text(reader, 0)

    assert text == ""