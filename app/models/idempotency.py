import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class IdempotencyKey(Base):
	__tablename__ = "idempotency_keys"
	__table_args__ = (UniqueConstraint("key", "user_id", name="unique_key_per_user"),)
	id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
	                                      primary_key=True,
	                                      default=uuid.uuid4)

	key: Mapped[str] = mapped_column(String(255),
	                                 nullable=False)

	user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
	                                           ForeignKey("users.id",
	                                                      ondelete="CASCADE"),
	                                           nullable=False,
	                                           index=True)

	request_hash: Mapped[str] = mapped_column(String(64), #sha256 hex
	                                          nullable=False)

	status: Mapped[str] = mapped_column(String(20), # in_progress | completed | failed
	                                    nullable=False,
	                                    default="in_progress")

	response_status_code: Mapped[int | None] = mapped_column(nullable=True)
	response_body: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
	                                             default=datetime.utcnow,
	                                             nullable=False)

	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
	                                             default=datetime.utcnow,
	                                             nullable=False)
