from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.dummyjson import sync_tickets_from_dummyjson


router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/tickets")
async def sync_tickets(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await sync_tickets_from_dummyjson(db)
    return {
        "message": "Tickets synchronized successfully",
        "result": result,
    }