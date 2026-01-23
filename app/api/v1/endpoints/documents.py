from __future__ import annotations

from uuid import UUID

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
from app.schemas.auth import UserContext
from app.schemas.document import DocumentCreate, DocumentRead
from app.services.document_service import (
	DocumentConflictError,
	DocumentNotFoundError,
	ForbiddenError,
	create_document,
	get_document_owned,
	list_documents_owned,
)

router = APIRouter()


@router.post("/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def create_document_endpoint(
		payload: DocumentCreate,
		db: AsyncSession = Depends(get_db),
		current_user: UserContext = Depends(get_current_user),
		idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")
):
	if not idempotency_key:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing idempotency key header")

	req_hash = compute_request_hash(
		user_id= str(current_user.id),
		method="POST",
		path="/v1/documents",
		body=payload.model_dump()
	)

	try:
		rec = await claim_key(db, user_id=current_user.id, key=idempotency_key, request_hash=req_hash)
		if rec.status == "completed" and rec.response_body is not None and rec.response_status_code is not None:
			return JSONResponse(rec.response_body, status_code=rec.response_status_code)
	except IdempotencyConflictError:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Idempotency key reused with different payload")
	except IdempotencyInProcessError:
		raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Request with this Idempotency-Key is already in progress")

	try:
		doc = await create_document(db, payload, owner_id=current_user.id)
		response_body = DocumentRead.model_validate(doc).model_dump()
		await finalize_key_success(db, record_id=rec.id, response_body=response_body, status_code=status.HTTP_201_CREATED)
		return response_body
	except DocumentConflictError:
		await finalize_key_failure(db, record_id=rec.id)
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document with this path already exists")
	except Exception:
		await finalize_key_failure(db, record_id=rec.id)
		raise


@router.get("/documents/{document_id}", response_model=DocumentRead)
async def get_document_endpoint(
		document_id: UUID,
		db: AsyncSession = Depends(get_db),
		current_user: UserContext = Depends(get_current_user)
):
	try:
		return await get_document_owned(db, document_id, owner_id=current_user.id)
	except DocumentNotFoundError:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
	except ForbiddenError:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.get("/documents", response_model=list[DocumentRead])
async def list_documents_endpoint(
		limit: int = 20,
		db: AsyncSession = Depends(get_db),
		current_user: UserContext = Depends(get_current_user)
):
	if limit > 100 or limit < 1:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Limit must be between 1 and 100")
	return await list_documents_owned(
		db, owner_id=current_user.id, limit=limit
	)