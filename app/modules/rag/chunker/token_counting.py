from typing import Protocol


class TokenCounter(Protocol):
    def count(self, text: str) -> int:
        ...

    def last_token_count(self, text: str, limit: int) -> str:
        ...

