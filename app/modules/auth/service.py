import asyncio
import logging
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import cache
from typing import Final
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.core.security.hashing import hash_password, verify_password
from app.core.security.jwt import (
    create_access_token,
    create_refresh_token,
    refresh_token_lifetime,
)
from app.core.security.tokens import hash_refresh_token
from app.modules.auth.models import AuthSession, User

logger = logging.getLogger(__name__)

# Must not exceed the AuthSession.user_agent column length.
_USER_AGENT_MAX_LENGTH: Final[int] = 255


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    refresh_token: str


@cache
def _dummy_password_hash() -> str:
    return hash_password(secrets.token_urlsafe(16))


def _check_password(password: str, password_hash: str | None) -> bool:
    if password_hash is None:
        verify_password(password, _dummy_password_hash())
        return False

    return verify_password(password, password_hash)


async def login(
        db: AsyncSession,
        *,
        email: str,
        password: str,
        ip: str | None = None,
        user_agent: str | None = None,
) -> TokenPair:
    user = await db.scalar(select(User).where(User.email == email))

    # Password hashing is deliberately slow
    password_ok = await asyncio.to_thread(
        _check_password,
        password,
        user.password_hash if user else None,
    )

    if user is None or not password_ok:
        logger.warning("Failed login attempt", extra={"ip": ip})
        raise exceptions.InvalidCredentialsError()

    session_id = uuid4()

    access_token = create_access_token(user.id, session_id)
    refresh_token = create_refresh_token(user.id, session_id)

    db.add(
        AuthSession(
            id=session_id,
            user_id=user.id,
            refresh_token_hash=hash_refresh_token(refresh_token),
            ip=ip,
            user_agent=user_agent[:_USER_AGENT_MAX_LENGTH] if user_agent else None,
            expires_at=datetime.now(UTC) + refresh_token_lifetime(),
        )
    )
    await db.commit()

    logger.info(
        "User logged in",
        extra={"user_id": str(user.id), "session_id": str(session_id)},
    )

    return TokenPair(access_token=access_token, refresh_token=refresh_token)

