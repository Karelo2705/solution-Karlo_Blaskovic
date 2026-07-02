import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from .database import AsyncSessionLocal, create_db_and_tables
from .routers.tickets_read import router as tickets_read_router
from .routers.tickets_write import router as tickets_write_router
from .routers.tickets_sync import router as tickets_sync_router

from .services.background_sync import (
    run_dummyjson_sync_once,
    run_periodic_dummyjson_sync,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYNC_INTERVAL_SECONDS = 30


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()

    await run_dummyjson_sync_once(
        session_factory = AsyncSessionLocal,
        reason="startup",
    )

    sync_task = asyncio.create_task(
        run_periodic_dummyjson_sync(
            session_factory = AsyncSessionLocal,
            interval_seconds = SYNC_INTERVAL_SECONDS,
        )
    )

    logger.info("Background DummyJSON sync started every %s seconds", SYNC_INTERVAL_SECONDS)

    try:
        yield

    finally:
        sync_task.cancel()

        with suppress(asyncio.CancelledError):
            await sync_task

        logger.info("Background DummyJSON sync stopped")


app = FastAPI(
    title="TicketHub",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "TicketHub API is running"}

app.include_router(tickets_read_router)
app.include_router(tickets_write_router)
app.include_router(tickets_sync_router)