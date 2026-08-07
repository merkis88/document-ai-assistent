import aiofiles

from pathlib import Path


class UnsupportedBinaryFileError(ValueError):
    pass


class TextParser:
    READ_BUFFER_SIZE = 64 * 1024
    BINARY_CHECK_SIZE = 8 * 1024

    async def iter_text(self, file_path: Path):
        if not file_path.exists():
            raise FileNotFoundError(f"File: {file_path}, does not exist")

        if not file_path.is_file():
            raise ValueError(f"File: {file_path}, is not a file")

        await self._ensure_text_file(file_path)

        async with aiofiles.open(file_path, mode='r', encoding="utf-8", errors="strict" ) as file:
            while True:
                text_part = await file.read(self.READ_BUFFER_SIZE)

                if not text_part:
                    break

                yield text_part

    async def _ensure_text_file(self, file_path: Path) -> None:
        async with aiofiles.open(file_path, mode="rb") as file:
            sample = await file.read(self.BINARY_CHECK_SIZE)

            if b"\x00" in sample:
                raise UnsupportedBinaryFileError(f"Binary file is not supported: {file_path}")

            try:
                sample.decode("utf-8")

            except UnicodeDecodeError as error:
                raise UnsupportedBinaryFileError(f"File: {file_path}, is not valid utf-8 text") from error


