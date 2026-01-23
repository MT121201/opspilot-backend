from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserContext(BaseModel):
	id: UUID
	email: EmailStr
	role: str


class LoginRequest(BaseModel):
	email: EmailStr


class TokenResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"