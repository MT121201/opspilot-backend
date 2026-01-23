from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
	title: str = Field(min_length=1, max_length=255)
	description: str = Field(min_length=1)


class TicketRead(BaseModel):
	id: UUID
	title: str
	description: str
	status: str
	created_by: UUID
	created_at: datetime

	model_config = {"from_attributes": True}

