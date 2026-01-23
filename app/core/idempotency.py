# app/core/idempotency.py
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.idempotency import IdempotencyKey


class IdempotencyConflictError(Exception):
	"""Same key reused with different payload."""
	pass


class IdempotencyInProcessError(Exception):
	"""Key exists but request is still running."""
	pass


def compute_request_hash(*, user_id: str, method: str, path: str, body: dict) -> str:
	payload = {
		"user_id": user_id,
		"method": method,
		"path": path,
		"body": body,
	}
	raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
	return hashlib.sha256(raw).hexdigest()


async def claim_key(
		db: AsyncSession,
		*,
		user_id,
		key: str,
		request_hash: str,
)-> IdempotencyKey:
	record = IdempotencyKey(key=key, user_id=user_id, request_hash=request_hash, status="in_progress")
	db.add(record)
	try:
		await db.commit()
		await db.refresh(record)
		return record
	except IntegrityError:
		await db.rollback()
		existing_record = await db.scalar(
			select(IdempotencyKey).where(IdempotencyKey.user_id == user_id,
			                             IdempotencyKey.key == key)
		)
		if not existing_record:
			raise

		if existing_record.request_hash != request_hash:
			raise IdempotencyConflictError
		if existing_record.status == "completed":
			return existing_record

		# InProgress or Failed
		raise IdempotencyInProcessError


async def finalize_key_success(
		db: AsyncSession,
		*,
		record_id,
		status_code: int,
		response_body: dict
) -> None:
	record = await db.get(IdempotencyKey, record_id)
	if not record:
		return
	record.status = "completed"
	record.response_status_code = status_code
	record.response_body = jsonable_encoder(response_body)
	record.updated_at = datetime.now(UTC)
	await db.commit()


async def finalize_key_failure(db: AsyncSession,
                               *,
                               record_id) -> None:
	record = await db.get(IdempotencyKey, record_id)
	if not record:
		return
	record.status = "failed"
	record.updated_at = datetime.now(UTC)
	await db.commit()