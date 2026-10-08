from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.security.hashing import hash_password
from app.core.security.jwt import (
    decode_access_token,
    decode_refresh_token,
)
from app.core.security.tokens import verify_refresh_token
from app.modules.auth.models import AuthSession, User
from app.modules.auth.service import login
from app.schemas.jwt import TokenType


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def db_session() -> AsyncSession:
    engine = create_async_engine(settings.DATABASE_URL)

    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.anyio
async def test_login_creates_auth_session_and_returns_valid_tokens(
    db_session: AsyncSession,
) -> None:
    password = "StrongPassword123!"

    user = User(
        username=f"user-{uuid4()}",
        email=f"{uuid4()}@example.com",
        password_hash=hash_password(password),
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    tokens = await login(
        db_session,
        email=user.email,
        password=password,
        ip="127.0.0.1",
        user_agent="pytest",
    )

    access_payload = decode_access_token(tokens.access_token)
    refresh_payload = decode_refresh_token(tokens.refresh_token)

    assert access_payload.sub == user.id
    assert access_payload.type == TokenType.ACCESS

    assert refresh_payload.sub == user.id
    assert refresh_payload.type == TokenType.REFRESH

    assert access_payload.sid == refresh_payload.sid

    auth_session = await db_session.scalar(
        select(AuthSession).where(
            AuthSession.id == access_payload.sid,
        )
    )

    assert auth_session is not None
    assert auth_session.user_id == user.id
    assert auth_session.revoked_at is None

    assert verify_refresh_token(
        tokens.refresh_token,
        auth_session.refresh_token_hash,
    )