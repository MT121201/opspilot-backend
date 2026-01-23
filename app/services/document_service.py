from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.schemas.document import DocumentCreate


class DocumentNotFoundError(Exception):
	pass


class ForbiddenError(Exception):
	pass


class DocumentConflictError(Exception):
	"""e.g., storage_path already exists (unique constraint)."""


async def create_document(db_session: AsyncSession, data: DocumentCreate, *, owner_id) -> Document:
	doc = Document(
		filename=data.filename,
		content_type=data.content_type,
		storage_path=data.storage_path,
		size_bytes=data.size_bytes,
		owner_id=owner_id
	)

	db_session.add(doc)
	try:
		await db_session.commit()
	except IntegrityError:
		await db_session.rollback()
		raise DocumentConflictError
	await db_session.refresh(doc)
	return doc


async def get_document_owned(db_session: AsyncSession, document_id, *, owner_id) -> Document:
	result = await db_session.execute(select(Document).where(Document.id == document_id))
	doc = result.scalar_one_or_none()
	if not doc:
		raise DocumentNotFoundError
	if doc.owner_id != owner_id:
		raise ForbiddenError
	return doc


async def list_documents_owned(db_session: AsyncSession, *, owner_id, limit: int = 20) -> list[Document]:
	result = await db_session.execute(
		select(Document)
		.where(Document.owner_id == owner_id)
		.order_by(Document.id.desc())
		.limit(limit))
	return list(result.scalars().all())