# TicketHub API

TicketHub is a middleware REST API service built with **FastAPI**. The application collects support ticket data from the external DummyJSON API, stores the transformed data in a local database, and exposes REST endpoints for reading, searching, creating, updating, and synchronizing tickets.

External data source:

- Todos: `https://dummyjson.com/todos`
- Users: `https://dummyjson.com/users`

The external API is used only as a source for synchronization. All read and write operations are performed against the local database.

---

## Tech Stack

- Python 3.11
- FastAPI
- httpx
- Pydantic v2
- SQLAlchemy 2.x async
- SQLite with aiosqlite
- Alembic
- Uvicorn
- pytest

---

## Features

- Async FastAPI application
- Async SQLAlchemy database access
- Local SQLite database persistence
- Alembic database migrations
- DummyJSON synchronization
- Startup synchronization from DummyJSON
- Periodic background synchronization every 30 seconds
- Manual synchronization endpoint
- Ticket listing with pagination
- Filtering by status and priority
- Search by ticket title
- Ticket details with original source JSON
- Create new tickets
- Update existing tickets
- Health check endpoint
- Swagger/OpenAPI documentation

---

## Project Structure

tickethub/
│
├── alembic/
│ ├── versions/
│ │ └── <migration_id>\_create_tickets_table.py
│ ├── env.py
│ ├── README
│ └── script.py.mako
│
├── src/
│ └── app/
│ ├── main.py
│ ├── database.py
│ ├── models.py
│ ├── schemas.py
│ │
│ ├── routers/
│ │ ├── tickets_read.py
│ │ ├── tickets_write.py
│ │ └── synchronize.py
│ │
│ └── services/
│ ├── dummyjson.py
│ └── background_sync.py
│
├── tests/
│ ├── conftest.py
│ ├── test_tickets.py
│ └── test_dummyjson_service.py
│
├── .dockerignore
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pytest.ini
├── README.md
└── requirements.txt

---

## Ticket Data Mapping

DummyJSON todo objects are transformed into local Ticket records.

| Local Ticket field | Source / Logic                                    |
| ------------------ | ------------------------------------------------- |
| `id`               | DummyJSON `todo.id`                               |
| `title`            | DummyJSON `todo.todo`                             |
| `status`           | `closed` if `completed == true`, otherwise `open` |
| `priority`         | calculated from ticket id                         |
| `assignee`         | username from DummyJSON users using `userId`      |
| `source_json`      | original DummyJSON todo JSON                      |

Priority is calculated from the ticket ID:

```text
id % 3 == 0 -> low
id % 3 == 1 -> medium
id % 3 == 2 -> high
```

---

## Setup

Create and activate a virtual environment.

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available yet, install the required packages manually:

```bash
pip install fastapi uvicorn httpx pydantic sqlalchemy aiosqlite alembic pytest pytest-asyncio
```

Then generate `requirements.txt`:

```bash
pip freeze > requirements.txt
```

---

## Configuration

The application uses SQLite by default.

Database URL:

```text
sqlite+aiosqlite:///./tickethub.db
```

The database URL is configured in:

```text
src/app/database.py
alembic.ini
```

The background synchronization interval is configured in:

```text
src/app/main.py
```

Default value:

```text
30 seconds
```

No external API keys are required.

---

## Database Setup

This project uses Alembic for database migrations.

Run migrations before starting the application:

```bash
python -m alembic upgrade head
```

This creates the local SQLite database file:

```text
tickethub.db
```

The database file is local runtime data and should not be committed to Git.

Recommended `.gitignore` entries:

```gitignore
.venv/
__pycache__/
.pytest_cache/
tickethub.db
*.db
.env
```

---

## Running the Application

Start the development server:

```bash
python -m uvicorn src.app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## Synchronization

The application synchronizes tickets from DummyJSON in three ways:

1. Automatically on application startup
2. Automatically in the background every 30 seconds
3. Manually through the API endpoint

Manual sync endpoint:

```http
POST /sync/tickets
```

Example response:

```json
{
  "message": "Tickets synchronized successfully",
  "result": {
    "created": 10,
    "updated": 0,
    "skipped": 90,
    "missing_assignee": 0,
    "total_from_source": 100
  }
}
```

Existing tickets are not overwritten aggressively during synchronization. This prevents local changes, such as manually changed assignees, from being overwritten every 30 seconds.

---

## API Endpoints

### Health Check

```http
GET /health
```

Returns application health status.

Example response:

```json
{
  "status": "ok"
}
```

---

### List Tickets

```http
GET /tickets
```

Returns a paginated list of tickets from the local database.

Query parameters:

| Parameter  | Type   | Description                                 |
| ---------- | ------ | ------------------------------------------- |
| `limit`    | int    | Number of tickets to return                 |
| `offset`   | int    | Number of tickets to skip                   |
| `status`   | string | Optional filter: `open` or `closed`         |
| `priority` | string | Optional filter: `low`, `medium`, or `high` |

Examples:

```http
GET /tickets?limit=10&offset=0
GET /tickets?status=open&limit=10&offset=0
GET /tickets?priority=high&limit=10&offset=0
GET /tickets?status=open&priority=high&limit=10&offset=0
```

Example response:

```json
[
  {
    "id": 1,
    "title": "Do something nice for someone you care about",
    "status": "open",
    "priority": "medium",
    "assignee": "emilys"
  }
]
```

---

### Search Tickets

```http
GET /tickets/search?q=text
```

Searches tickets by title.

Example:

```http
GET /tickets/search?q=movie
```

---

### Get Ticket Details

```http
GET /tickets/{ticket_id}
```

Returns one ticket with the original source JSON.

Example response:

```json
{
  "id": 1,
  "title": "Do something nice for someone you care about",
  "status": "open",
  "priority": "medium",
  "assignee": "emilys",
  "source_json": {
    "id": 1,
    "todo": "Do something nice for someone you care about",
    "completed": false,
    "userId": 152
  }
}
```

---

### Create Ticket

```http
POST /tickets
```

Request body:

```json
{
  "title": "New support ticket",
  "status": "open",
  "priority": "high",
  "assignee": "karlo"
}
```

Allowed status values:

```text
open
closed
```

Allowed priority values:

```text
low
medium
high
```

---

### Update Ticket

```http
PATCH /tickets/{ticket_id}
```

Request body example:

```json
{
  "status": "closed",
  "priority": "medium",
  "assignee": "ivan"
}
```

The change is stored in the local database and survives application restart.

---

## Alembic Commands

Create a new migration after changing SQLAlchemy models:

```bash
python -m alembic revision --autogenerate -m "describe change"
```

Apply migrations:

```bash
python -m alembic upgrade head
```

Rollback one migration:

```bash
python -m alembic downgrade -1
```

Show current migration:

```bash
python -m alembic current
```

Show migration history:

```bash
python -m alembic history
```

---

## Testing

Run tests with:

Implemented tests:

- Health-independent API test setup using an in-memory SQLite database
- Creating a new ticket with `POST /tickets`
- Getting a ticket by ID with `GET /tickets/{ticket_id}`
- Listing tickets with pagination using `GET /tickets?limit=&offset=`
- Filtering tickets by `status` and `priority`
- Searching tickets by title using `GET /tickets/search?q=`
- Updating a ticket with `PATCH /tickets/{ticket_id}`
- Validating that invalid ticket input returns `422 Unprocessable Entity`
- Testing DummyJSON helper functions:
  - `calculate_status()`
  - `calculate_priority()`

Run tests with:

````bash
pytest
---

## Makefile Commands

If using a Makefile, recommended commands are:

```makefile
run:
	python -m uvicorn src.app.main:app --reload

migrate:
	python -m alembic upgrade head

revision:
	python -m alembic revision --autogenerate -m "migration"

test:
	pytest

docker-build:
	docker build -t tickethub-api .
````

Usage examples:

```bash
make run
make migrate
make test
make docker-build
```

---

## Docker

Build the image with:

```bash
docker build -t tickethub-api .
```

Run the container:

```bash
docker run -p 8000:8000 tickethub-api
```

If Docker Compose is included:

```bash
docker compose up --build
```

---

## Development Notes

This project uses async programming for both external API calls and database access.

External API calls are handled with:

```text
httpx.AsyncClient
```

Database access is handled with:

```text
SQLAlchemy AsyncSession
```

This allows the FastAPI application to handle other requests while waiting for network or database operations.

---

## Use of AI Tools

ChatGPT was used during development for:

- Explaining the assignment requirements
- Explaining FastAPI
- Explaining async SQLAlchemy usage
- Explaining Alembic migrations
- Creating Makefile and Dockerfile and configuring them
- Creating the Readme file

The generated code and explanations were reviewed and adapted during implementation.

---
