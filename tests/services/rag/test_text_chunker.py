import pytest

from app.services.rag.text_chunker import TextChunker


def test_split_returns_empty_list_for_empty_text() -> None:
    chunker = TextChunker()

    result = chunker.split("   \n\n   ")

    assert result == []


def test_split_short_text_into_single_chunk() -> None:
    chunker = TextChunker(chunk_size=500, overlap=75)

    text = "   Привет, мир.   "

    chunks = chunker.split(text)

    assert len(chunks) == 1

    chunk = chunks[0]

    assert chunk.index == 0
    assert chunk.text == "Привет, мир."
    assert chunk.start_char == 3
    assert chunk.end_char == 15
    assert chunk.page_number is None


def test_split_preserves_page_number() -> None:
    chunker = TextChunker()

    chunks = chunker.split("Текст первой страницы.", page_number=1)

    assert len(chunks) == 1
    assert chunks[0].page_number == 1


def test_split_creates_multiple_chunks() -> None:
    chunker = TextChunker(chunk_size=60, overlap=10)

    text = (
        "Первое предложение содержит некоторый текст. "
        "Второе предложение продолжает общую мысль. "
        "Третье предложение завершает пример."
    )

    chunks = chunker.split(text)

    assert len(chunks) > 1

    for index, chunk in enumerate(chunks):
        assert chunk.index == index
        assert chunk.text
        assert chunk.start_char < chunk.end_char


def test_overlap_repeats_part_of_previous_chunk() -> None:
    chunker = TextChunker(chunk_size=50, overlap=10)

    text = (
        "Один длинный текст нужен для проверки перекрытия между чанками. "
        "Следующее предложение продолжает предыдущую мысль."
    )

    chunks = chunker.split(text)

    assert len(chunks) > 1

    first_chunk = chunks[0]
    second_chunk = chunks[1]

    assert second_chunk.start_char < first_chunk.end_char


def test_invalid_chunk_size_type() -> None:
    with pytest.raises(TypeError):
        TextChunker(chunk_size="500")  # type: ignore[arg-type]


def test_invalid_overlap_type() -> None:
    with pytest.raises(TypeError):
        TextChunker(overlap="75")  # type: ignore[arg-type]


def test_chunk_size_must_be_positive() -> None:
    with pytest.raises(ValueError):
        TextChunker(chunk_size=0)


def test_overlap_cannot_be_negative() -> None:
    with pytest.raises(ValueError):
        TextChunker(overlap=-1)


def test_overlap_must_be_smaller_than_chunk_size() -> None:
    with pytest.raises(ValueError):
        TextChunker(chunk_size=100, overlap=100)


def test_page_number_must_be_positive() -> None:
    chunker = TextChunker()

    with pytest.raises(ValueError):
        chunker.split("Некоторый текст", page_number=0,)