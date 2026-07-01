from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import create_db_and_tables
from .routers.tickets import router as tickets_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


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


app.include_router(tickets_router)