import jwt

from datetime import datetime, timedelta, timezone
from uuid import UUID
from pydantic import ValidationError
from app.core.config import settings
from app.schemas.jwt import TokenPayload, TokenType
from app.core.exceptions import InvalidTokenError, TokenExpiredError


def access_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "type": TokenType.ACCESS,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> TokenPayload:
    try:
        raw_payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        return TokenPayload.model_validate(raw_payload)

    except jwt.ExpiredSignatureError:
        raise TokenExpiredError() from None

    except (jwt.InvalidTokenError, ValidationError):
        raise InvalidTokenError() from None


def decode_access_token(token: str) -> TokenPayload:
    payload = decode_token(token)

    if payload.type != TokenType.ACCESS:
        raise InvalidTokenError()

    return payload

