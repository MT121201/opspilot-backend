# app/services/ticket_service.py
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate


class TicketNotFoundError(Exception):
	pass


class InvalidOwnerError(Exception):
	pass


async def create_ticket(db_session: AsyncSession, data: TicketCreate, *, created_by) -> Ticket:
	# If ticket created by invalid, DB FK will fail on commit -> We translate it later
	ticket = Ticket(title=data.title,
	                description=data.description,
	                status="open",
	                created_by=created_by)
	db_session.add(ticket)
	try:
		await db_session.commit()
	except IntegrityError:
		await db_session.rollback()
		# Mostly like FK validation error (created_by not found user)
		raise InvalidOwnerError
	await db_session.refresh(ticket)
	return ticket


async def get_ticket_by_id(db_session: AsyncSession, ticket_id) -> Ticket:
	result = await db_session.execute(select(Ticket).where(Ticket.id == ticket_id))
	ticket = result.scalar_one_or_none()
	if ticket is None:
		raise TicketNotFoundError
	return ticket


async def list_ticket(db_session: AsyncSession, limit: int = 20):
	# Offset pagination is simpler but not ideal long-term.
	# We'll upgrade to cursor pagination later; for Week 1, keep it straightforward.
	result =  await db_session.execute(select(Ticket).order_by(Ticket.id.desc()).limit(limit))
	return result.scalars().all()