from pathlib import Path
from typing import Final

from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter
from docling_core.types.doc import DoclingDocument

from app.core.errors.codes import ErrorCode
from app.core.errors.exceptions import ApplicationError


class DoclingParser:
    DOCLING_EXTENSIONS: Final[frozenset[str]] = frozenset(
        {
            ".pdf",
            ".docx",
            ".doc",
            ".rtf",
            ".pptx",
            ".ppt",
            ".xlsx",
            ".xls",
            ".html",
            ".htm",
            ".md",
            ".markdown",
            ".csv",
            ".epub",
            ".odt",
            ".ods",
            ".odp",
            ".png",
            ".jpg",
            ".jpeg",
            ".tif",
            ".tiff",
            ".bmp",
            ".webp",
        }
    )

    TEXT_EXTENSIONS: Final[frozenset[str]] = frozenset(
        {
            ".txt",
        }
    )

    SUPPORTED_EXTENSIONS: Final[frozenset[str]] = (DOCLING_EXTENSIONS | TEXT_EXTENSIONS)

    def __init__(self) -> None:
        self._converter = DocumentConverter()

    def parse(self, path_name: str | Path) -> DoclingDocument:
        path = Path(path_name)

        if not path.is_file():
            raise ApplicationError(code=ErrorCode.DOCUMENT_NOT_FOUND, message=f"Document not found: {path}")

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ApplicationError(code=ErrorCode.UNSUPPORTED_DOCUMENT_FORMAT, message="Unsupported document format")

        try:
            if extension in self.TEXT_EXTENSIONS:
                return self._parse_text(path)

            result = self._converter.convert(path)

            return result.document

        except ApplicationError:
            raise
        except Exception as exc:
            raise ApplicationError(code=ErrorCode.DOCUMENT_PARSE_FAILED, message=f"Failed to parse document: {path.name}") from exc

    def _parse_text(self, path: Path) -> DoclingDocument:
        content = path.read_text(encoding="utf-8")

        result = self._converter.convert_string(content=content, format=InputFormat.MD, name=path.name)

        return result.document





