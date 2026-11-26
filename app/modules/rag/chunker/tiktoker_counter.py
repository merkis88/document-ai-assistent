import tiktoken


class TiktokCounter:
    def __init__(self, encoding_name: str) -> None:
        self._encoding = tiktoken.get_encoding(encoding_name)

    def count(self, text: str) -> int:
        if not isinstance(text, str):
            raise TypeError("Text must be a string")

        return len(self._encoding.encode_ordinary(text))

    def last_token_count(self, text: str, limit: int) -> str:
        if not isinstance(text, str):
            raise TypeError("Text must be a string")
        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise ValueError("Limit must be a positive integer")

        tokens = self._encoding.encode_ordinary(text)

        return self._encoding.decode(tokens[-limit:])









