# tests/test_tickets.py

import pytest


@pytest.mark.asyncio
async def test_create_ticket(client):
    response = await client.post(
        "/tickets",
        json={
            "title": "Test ticket",
            "status": "open",
            "priority": "high",
            "assignee": "karlo",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Test ticket"
    assert data["status"] == "open"
    assert data["priority"] == "high"
    assert data["assignee"] == "karlo"


@pytest.mark.asyncio
async def test_get_ticket_by_id(client):
    create_response = await client.post(
        "/tickets",
        json={
            "title": "Engine alarm",
            "status": "open",
            "priority": "medium",
            "assignee": "ivan",
        },
    )

    ticket_id = create_response.json()["id"]

    response = await client.get(f"/tickets/{ticket_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == ticket_id
    assert data["title"] == "Engine alarm"
    assert data["assignee"] == "ivan"


@pytest.mark.asyncio
async def test_list_tickets_with_pagination(client):
    for index in range(3):
        await client.post(
            "/tickets",
            json={
                "title": f"Ticket {index}",
                "status": "open",
                "priority": "low",
                "assignee": "tester",
            },
        )

    response = await client.get("/tickets?limit=2&offset=0")

    assert response.status_code == 200
    assert len(response.json()) == 2

    response = await client.get("/tickets?limit=2&offset=2")

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_filter_tickets_by_status_and_priority(client):
    await client.post(
        "/tickets",
        json={
            "title": "Open high ticket",
            "status": "open",
            "priority": "high",
            "assignee": "karlo",
        },
    )

    await client.post(
        "/tickets",
        json={
            "title": "Closed low ticket",
            "status": "closed",
            "priority": "low",
            "assignee": "ivan",
        },
    )

    response = await client.get("/tickets?status=open&priority=high")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Open high ticket"
    assert data[0]["status"] == "open"
    assert data[0]["priority"] == "high"


@pytest.mark.asyncio
async def test_search_tickets_by_title(client):
    await client.post(
        "/tickets",
        json={
            "title": "Generator does not start",
            "status": "open",
            "priority": "high",
            "assignee": "mate",
        },
    )

    await client.post(
        "/tickets",
        json={
            "title": "Cabin light issue",
            "status": "open",
            "priority": "low",
            "assignee": "bruno",
        },
    )

    response = await client.get("/tickets/search?q=generator")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Generator does not start"


@pytest.mark.asyncio
async def test_update_ticket(client):
    create_response = await client.post(
        "/tickets",
        json={
            "title": "Ticket to update",
            "status": "open",
            "priority": "low",
            "assignee": "old_assignee",
        },
    )

    ticket_id = create_response.json()["id"]

    response = await client.patch(
        f"/tickets/{ticket_id}",
        json={
            "status": "closed",
            "priority": "high",
            "assignee": "new_assignee",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "closed"
    assert data["priority"] == "high"
    assert data["assignee"] == "new_assignee"


@pytest.mark.asyncio
async def test_create_ticket_rejects_invalid_priority(client):
    response = await client.post(
        "/tickets",
        json={
            "title": "Invalid priority ticket",
            "status": "open",
            "priority": "urgent",
            "assignee": "karlo",
        },
    )

    assert response.status_code == 422