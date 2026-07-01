from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


Status = Literal["open", "closed"]
Priority = Literal["low", "medium", "high"]


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    status: Status = "open"
    priority: Priority = "medium"
    assignee: str | None = None


class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    status: Status | None = None
    priority: Priority | None = None
    assignee: str | None = None


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: Status
    priority: Priority
    assignee: str | None = None


class TicketDetail(TicketRead):
    source_json: dict[str, Any] | None = None