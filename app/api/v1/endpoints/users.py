from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import (
	UserAlreadyExistsError,
	UserNotFoundError,
	create_user,
	get_user_by_username,
)

router = APIRouter()


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
		payload: UserCreate,
		db: AsyncSession = Depends(get_db)
):
	try:
		user = await create_user(db, payload)
		return user
	except UserAlreadyExistsError:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")


@router.get("/users/{user_name}", response_model=UserRead)
async def get_user_by_username_endpoint(user_name: str, db: AsyncSession = Depends(get_db)):
	try:
		user = await get_user_by_username(db, user_name)
		return user
	except UserNotFoundError:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
