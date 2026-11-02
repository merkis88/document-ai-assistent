import tiktoken

from typing import Protocol

class TokenCounter(Protocol):
    def count(self, text: str) -> int:
        if text is None:
            raise TypeError('text cannot be None')

        if not isinstance(text, str):
            raise TypeError('text must be a string')


