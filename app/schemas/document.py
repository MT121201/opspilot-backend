from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
	filename: str = Field(min_length=1, max_length=255)
	content_type: str = Field(min_length=1, max_length=100)
	storage_path: str = Field(min_length=1, max_length=512)
	size_bytes: int = Field(gt=0)


class DocumentRead(BaseModel):
	id: UUID
	filename: str
	content_type: str
	storage_path: str
	size_bytes: int
	owner_id: UUID | None
	created_at: datetime

	model_config = {"from_attributes": True}