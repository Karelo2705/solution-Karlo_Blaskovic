# src/app/services/dummyjson.py

from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Ticket


DUMMYJSON_TODOS_URL = "https://dummyjson.com/todos?limit=0"
DUMMYJSON_USERS_URL = "https://dummyjson.com/users?limit=0"


def calculate_priority(ticket_id: int) -> str:
    remainder = ticket_id % 3

    if remainder == 0:
        return "low"

    if remainder == 1:
        return "medium"

    return "high"


def calculate_status(completed: bool) -> str:
    if completed:
        return "closed"

    return "open"


async def fetch_dummyjson_data() -> tuple[list[dict[str, Any]], dict[int, str]]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        todos_response = await client.get(DUMMYJSON_TODOS_URL)
        users_response = await client.get(DUMMYJSON_USERS_URL)

        todos_response.raise_for_status()
        users_response.raise_for_status()

        todos_data = todos_response.json()
        users_data = users_response.json()

    todos = todos_data["todos"]
    users = users_data["users"]

    users_by_id = {
        user["id"]: user["username"]
        for user in users
    }

    return todos, users_by_id


async def sync_tickets_from_dummyjson(db: AsyncSession) -> dict[str, int]:
    todos, users_by_id = await fetch_dummyjson_data()

    created_count = 0
    updated_count = 0
    skipped_count = 0
    missing_assignee_count = 0

    for todo in todos:
        ticket_id = todo["id"]
        assignee = users_by_id.get(todo["userId"])

        if assignee is None:
            missing_assignee_count += 1

        existing_ticket = await db.get(Ticket, ticket_id)

        if existing_ticket is not None:
            changed = False

            if existing_ticket.assignee is None and assignee is not None:
                existing_ticket.assignee = assignee
                changed = True

            if existing_ticket.source_json is None:
                existing_ticket.source_json = todo
                changed = True

            if changed:
                updated_count += 1
            else:
                skipped_count += 1

            continue

        ticket = Ticket(
            id=ticket_id,
            title=todo["todo"],
            status=calculate_status(todo["completed"]),
            priority=calculate_priority(ticket_id),
            assignee=assignee,
            source_json=todo,
        )

        db.add(ticket)
        created_count += 1

    await db.commit()

    return {
        "created": created_count,
        "updated": updated_count,
        "skipped": skipped_count,
        "missing_assignee": missing_assignee_count,
        "total_from_source": len(todos),
    }