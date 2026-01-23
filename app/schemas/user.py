from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


####
class UserCreate(BaseModel):
	username: str = Field(max_length=50)
	email: EmailStr
	role: str = Field(default="user", max_length=50)


####
class UserRead(BaseModel):
	username: str
	id: UUID
	email: EmailStr
	role: str
	created_at: datetime

	model_config = {"from_attributes": True}