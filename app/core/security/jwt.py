from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
from pydantic import ValidationError

from app.core import exceptions
from app.core.config import settings
from app.schemas.jwt import TokenPayload, TokenType

_REQUIRED_CLAIMS = ["sub", "sid", "jti", "type", "iss", "aud", "iat", "exp"]


def _encode(payload: TokenPayload) -> str:
    return jwt.encode(
        payload.model_dump(mode="json"),
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(user_id: UUID, session_id: UUID) -> str:
    now = datetime.now(UTC)

    payload = TokenPayload(
        sub=user_id,
        sid=session_id,
        jti=uuid4(),
        type=TokenType.ACCESS,
        iss=settings.JWT_ISSUER,
        aud=settings.JWT_AUDIENCE,
        iat=now,
        exp=now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return _encode(payload)


def decode_token(token: str) -> TokenPayload:
    try:
        raw_payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            options={"require": _REQUIRED_CLAIMS},
        )
        return TokenPayload.model_validate(raw_payload)

    except jwt.ExpiredSignatureError:
        raise exceptions.TokenExpiredError() from None

    except (jwt.InvalidTokenError, ValidationError):
        raise exceptions.InvalidTokenError() from None


def decode_access_token(token: str) -> TokenPayload:
    payload = decode_token(token)

    if payload.type is not TokenType.ACCESS:
        raise exceptions.InvalidTokenError()

    return payload