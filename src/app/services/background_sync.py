# src/app/services/background_sync.py

import asyncio
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .dummyjson import sync_tickets_from_dummyjson


logger = logging.getLogger(__name__)


async def run_dummyjson_sync_once(
    session_factory: async_sessionmaker[AsyncSession],
    reason: str,
) -> dict[str, Any] | None:
    try:
        async with session_factory() as db:
            result = await sync_tickets_from_dummyjson(db)

        logger.info("DummyJSON sync completed. Reason=%s Result=%s", reason, result)
        return result

    except Exception:
        logger.exception("DummyJSON sync failed. Reason=%s", reason)
        return None


async def run_periodic_dummyjson_sync(
    session_factory: async_sessionmaker[AsyncSession],
    interval_seconds: int,
) -> None:
    while True:
        await asyncio.sleep(interval_seconds)

        await run_dummyjson_sync_once(
            session_factory=session_factory,
            reason="periodic",
        )