# app/api/deps.py
from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
	"""
	Provide a database session to request handlers via dependency injection.
	RULE:
	- get_db() only opens/closes the session. It does not auto-commit.
	- Service layer decides when to commit()

	"""
	sessionmaker: async_sessionmaker[AsyncSession] = request.app.state.db_session_maker
	async with sessionmaker() as session:
		yield session