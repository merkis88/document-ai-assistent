import hashlib
import hmac


def hash_refresh_token(toke: str) -> str:
    return hashlib.sha256(toke.encode()).hexdigest()


def verify_refresh_token(toke: str, token_hash: str) -> bool:
    return hmac.compare_digest(hash_refresh_token(toke), token_hash)