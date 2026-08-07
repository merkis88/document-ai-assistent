from pathlib import Path


class FileValidator:
    MAX_FILE_SIZE = 1024 * 1024 * 1024
    SUPPORTED_EXTENSIONS = {
        ".txt",
        ".md",
        ".csv",
        ".json",
        ".pdf",
        ".docx",
    }

    @classmethod
    def validate(cls, file_path) -> None:
        if not file_path.exists():
            raise FileNotFoundError(f"File: {file_path}, does not exist.")

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        file_size = file_path.stat().st_size

        if file_size < 0:
            raise ValueError(f"File size exceeds maximum allowed size of 1 GB")

        extension = file_path.suffix.lower()

        if extension not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")
