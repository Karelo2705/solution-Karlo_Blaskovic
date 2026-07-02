from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Ticket
from ..schemas import TicketCreate, TicketDetail, TicketRead, TicketUpdate


tickets_router = APIRouter(prefix="/tickets", tags=["tickets"])


@tickets_router.get("", response_model=list[TicketRead])
async def list_tickets(
    db: Annotated[AsyncSession, Depends(get_db)],
    status: str | None = None,
    priority: str | None = None,
):
    query = select(Ticket)

    if status is not None:
        query = query.where(Ticket.status == status)

    if priority is not None:
        query = query.where(Ticket.priority == priority)

    query = query.order_by(Ticket.id)

    result = await db.execute(query)
    tickets = result.scalars().all()

    return tickets


@tickets_router.get("/search", response_model=list[TicketRead])
async def search_tickets(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str = Query(min_length=1),
):
    query = select(Ticket).where(Ticket.title.ilike(f"%{q}%"))

    result = await db.execute(query)
    tickets = result.scalars().all()

    return tickets


@tickets_router.get("/{ticket_id}", response_model=TicketDetail)
async def get_ticket(
    ticket_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    ticket = await db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@tickets_router.post("", response_model=TicketDetail, status_code=201)
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


@tickets_router.patch("/{ticket_id}", response_model=TicketDetail)
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