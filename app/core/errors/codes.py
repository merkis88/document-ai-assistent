from enum import StrEnum


class ErrorCode(StrEnum):
    DOCUMENT_NOT_FOUND = "document_not_found"
    UNSUPPORTED_DOCUMENT_FORMAT = "unsupported_document_format"
    DOCUMENT_PARSE_FAILED = "document_parse_failed"