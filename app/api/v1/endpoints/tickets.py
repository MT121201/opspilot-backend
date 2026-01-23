# app/api/v1/endpoints/tickets.py
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_deps import get_current_user
from app.api.deps import get_db
from app.core.idempotency import (
	IdempotencyConflictError,
	IdempotencyInProcessError,
	claim_key,
	compute_request_hash,
	finalize_key_failure,
	finalize_key_success,
)
from app.schemas.ticket import TicketCreate, TicketRead
from app.services.ticket_service import (
	TicketNotFoundError,
	create_ticket,
	get_ticket_by_id,
	list_ticket,
)

router = APIRouter()

@router.post("/tickets", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
async def create_ticket_endpoint(payload: TicketCreate,
                                 db: AsyncSession = Depends(get_db),
                                 current_user=Depends(get_current_user),
                                 idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):

	if not idempotency_key:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing idempotency key header")

	req_hash = compute_request_hash(
		user_id= str(current_user.id),
		method="POST",
		path="/v1/tickets",
		body=payload.model_dump()
	)

	try:
		logger.info("A: about to claim_key key=%s user=%s", idempotency_key, current_user.id)
		rec = await claim_key(db, user_id=current_user.id, key=idempotency_key, request_hash=req_hash)
		logger.info("B: claim_key done rec_id=%s status=%s", rec.id, rec.status)
		# If claim_key returns an existing completed record, it will have response saved.
		if rec.status == "completed" and rec.response_body is not None and rec.response_status_code is not None:
			return JSONResponse(rec.response_body, status_code=rec.response_status_code)

	except IdempotencyConflictError:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Idempotency key reused with different payload")
	except IdempotencyInProcessError:
		raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Request with this Idempotency-Key is already in progress")

	try:
		logger.info("C: about to create_ticket")
		ticket = await create_ticket(db, payload, created_by=current_user.id)
		logger.info("D: create_ticket done ticket_id=%s", ticket.id)

		logger.info("E: about to finalize_key_success rec_id=%s", rec.id)
		response_body = TicketRead.model_validate(ticket).model_dump()
		await finalize_key_success(db, record_id=rec.id, response_body=response_body, status_code=status.HTTP_201_CREATED)
		logger.info("F: finalize_key_success done rec_id=%s", rec.id)

		logger.info("G: returning response")
		return response_body

	except Exception:
		logger.exception("ERROR: failed during ticket create flow rec_id=%s", rec.id)
		await finalize_key_failure(db, record_id=rec.id)
		raise


@router.get("/tickets/{ticket_id}", response_model=TicketRead)
async def get_ticket_by_id_endpoint(ticket_id: int, db: AsyncSession = Depends(get_db)):
	try:
		return await get_ticket_by_id(db, ticket_id)
	except TicketNotFoundError:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")


@router.get("/tickets", response_model=list[TicketRead])
async def list_ticket_endpoint(limit: int = 20 ,db: AsyncSession = Depends(get_db)):
	if limit > 100 or limit < 1:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Limit must be between 1 and 100")
	return await list_ticket(db, limit)

