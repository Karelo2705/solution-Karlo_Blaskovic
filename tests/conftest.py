from collections.abc import AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.app.database import Base, get_db
from src.app.routers.tickets_read import router as tickets_read_router
from src.app.routers.tickets_write import router as tickets_write_router


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            yield session

    test_app = FastAPI(title="TicketHub Test App")
    test_app.dependency_overrides[get_db] = override_get_db

    test_app.include_router(tickets_read_router)
    test_app.include_router(tickets_write_router)

    transport = ASGITransport(app=test_app)

    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client

    await engine.dispose()