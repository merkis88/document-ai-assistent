import logging
from datetime import UTC, datetime, timedelta
from typing import Final
from uuid import UUID, uuid4

import jwt
from pydantic import ValidationError

from app.core import exceptions
from app.core.config import settings
from app.schemas.jwt import TokenPayload, TokenType

logger = logging.getLogger(__name__)

_REQUIRED_CLAIMS: Final = ("sub", "sid", "jti", "type", "iss", "aud", "iat", "exp")

# Tolerance for clock drift between instances (applies to exp, iat).
_CLOCK_SKEW_LEEWAY_SECONDS: Final = 10


def access_token_lifetime() -> timedelta:
    return timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def refresh_token_lifetime() -> timedelta:
    return timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


def _encode(payload: TokenPayload) -> str:
    claims = payload.model_dump(mode="json", exclude={"iat", "exp"})

    claims["iat"] = int(payload.iat.timestamp())
    claims["exp"] = int(payload.exp.timestamp())

    return jwt.encode(
        claims,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def _create_token(
    user_id: UUID,
    session_id: UUID,
    token_type: TokenType,
    lifetime: timedelta,
) -> str:
    now = datetime.now(UTC)

    payload = TokenPayload(
        sub=user_id,
        sid=session_id,
        jti=uuid4(),
        type=token_type,
        iss=settings.JWT_ISSUER,
        aud=settings.JWT_AUDIENCE,
        iat=now,
        exp=now + lifetime,
    )

    return _encode(payload)


def create_access_token(user_id: UUID, session_id: UUID) -> str:
    return _create_token(
        user_id,
        session_id,
        TokenType.ACCESS,
        access_token_lifetime(),
    )


def create_refresh_token(user_id: UUID, session_id: UUID) -> str:
    return _create_token(
        user_id,
        session_id,
        TokenType.REFRESH,
        refresh_token_lifetime(),
    )


def _decode(token: str, expected_type: TokenType) -> TokenPayload:
    try:
        raw_payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            leeway=_CLOCK_SKEW_LEEWAY_SECONDS,
            options={"require": list(_REQUIRED_CLAIMS)},
        )
        payload = TokenPayload.model_validate(raw_payload)

    except jwt.ExpiredSignatureError:
        raise exceptions.TokenExpiredError() from None

    except (jwt.InvalidTokenError, ValidationError) as exc:
        logger.debug("Token rejected: %s", type(exc).__name__)
        raise exceptions.InvalidTokenError() from None

    if payload.type != expected_type:
        logger.debug(
            "Token rejected: expected %s, got %s",
            expected_type,
            payload.type,
        )
        raise exceptions.InvalidTokenError()

    return payload


def decode_access_token(token: str) -> TokenPayload:
    return _decode(token, TokenType.ACCESS)


def decode_refresh_token(token: str) -> TokenPayload:
    return _decode(token, TokenType.REFRESH)
