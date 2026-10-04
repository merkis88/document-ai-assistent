import codecs

from pathlib import Path
from zipfile import BadZipFile, ZipFile

class FileValidator:
    MAX_FILE_SIZE = 1024 * 1024 * 1024
    SAMPLE_SIZE = 8 * 1024
    MAX_DOCX_UNCOMPRESSED_SIZE = 512 * 1024 * 1024
    MAX_DOCX_ENTRIES = 10_000
    MAX_COMPRESSION_RATIO = 100
    TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json"}
    SUPPORTED_EXTENSIONS = TEXT_EXTENSIONS | {".pdf", ".docx"}

    @classmethod
    def validate(cls, file_path: Path) -> None:
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        file_size = file_path.stat().st_size

        if file_size == 0:
            raise ValueError("File cannot be empty")

        if file_size > cls.MAX_FILE_SIZE:
            raise ValueError("File size exceeds maximum allowed size of 1 GB")

        extension = file_path.suffix.lower()

        if extension not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")

        if extension in cls.TEXT_EXTENSIONS:
            cls._validate_text(file_path)
        if extension == ".pdf":
            cls._validate_text(file_path)
        if extension == ".docx":
            cls._validate_text(file_path)

    @classmethod
    def _validate_text(cls, file_path: Path) -> None:
        with file_path.open("rb") as file:
            sample = file.read(cls.SAMPLE_SIZE)

        if b"\x00" in sample:
            raise ValueError("Binary data detected in text file")

        decoder = codecs.getincrementaldecoder("utf-8")(errors="strict")

        try:
            decoder.decode(sample, final=False)
        except UnicodeDecodeError as error:
            raise ValueError("File is not valid UTF-8 text") from error

    @staticmethod
    def _validate_pdf(file_path: Path) -> None:
        with file_path.open("rb") as file:
            header = file.read(1024)

        if b"%PDF" not in header:
            raise ValueError("File has .pdf extension but is not a valid PDF")

    @classmethod
    def _validate_docx(cls, file_path: Path) -> None:
        try:
            with ZipFile(file_path) as archive:
                try:
                    archive.getinfo("[Content_Types].xml")
                    archive.getinfo("word/document.xml")
                except KeyError as error:
                    raise ValueError("File has .docx extension but is not a valid DOCX document") from error

                entries = archive.infolist()

                if len(entries) > cls.MAX_DOCX_ENTRIES:
                    raise ValueError("DOCX archive contains too many entries")

                total_uncompressed_size = 0

                for entry in entries:
                    total_uncompressed_size += entry.file_size

                    if total_uncompressed_size > cls.MAX_DOCX_UNCOMPRESSED_SIZE:
                        raise ValueError("DOCX archive contains too many uncompressed entries")
                    elif entry.file_size == 0:
                        raise ValueError("File has no data")
                    elif compression_ratio > cls.MAX_DOCX_UNCOMPRESSED_SIZE:
                        raise ValueError("Suspicious DOCX compression ratio")

                    compression_ratio = entry.file_size / entry.compress_size

        except BadZipFile as error:
            raise ValueError("File has .docx extension but is not a valid ZIP archive") from error








