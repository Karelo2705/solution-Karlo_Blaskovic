from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Ticket
from ..schemas import TicketCreate, TicketDetail, TicketRead, TicketUpdate


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketDetail, status_code=201)
async def create_ticket(
    ticket_data: TicketCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    ticket = Ticket(
        title=ticket_data.title,
        status=ticket_data.status,
        priority=ticket_data.priority,
        assignee=ticket_data.assignee,
        source_json=None,
    )

    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    return ticket


@router.patch("/{ticket_id}", response_model=TicketDetail)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    ticket = await db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    update_data = ticket_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(ticket, field, value)

    await db.commit()
    await db.refresh(ticket)

    return ticket