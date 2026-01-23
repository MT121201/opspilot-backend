from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate


class UserAlreadyExistsError(Exception):
	pass


class UserNotFoundError(Exception):
	pass


async def create_user(db_session: AsyncSession, data: UserCreate) -> User:
	user = User(username=str(data.username), email=str(data.email), role=data.role)
	db_session.add(user)
	try:
		await db_session.commit()
	except IntegrityError:
		await db_session.rollback()
		raise UserAlreadyExistsError
	await db_session.refresh(user)
	return user


async def get_user_by_username(db_session: AsyncSession, username) -> User:
	result = await db_session.execute(select(User).where(User.username == username))
	user =  result.scalar_one_or_none()
	if user is None:
		raise UserNotFoundError
	return user


async def get_user_by_id(db_session: AsyncSession, user_id) -> User:
	result = await db_session.execute(select(User).where(User.id == user_id))
	user = result.scalar_one_or_none()
	if user is None:
		raise UserNotFoundError
	return user


async def get_user_by_email(db_session: AsyncSession, email) -> User:
	result = await db_session.execute(select(User).where(User.email == email))
	user = result.scalar_one_or_none()
	if not user:
		raise UserNotFoundError
	return user

###


