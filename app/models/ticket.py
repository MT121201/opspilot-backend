# app/models/ticket.py
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Ticket(Base):
	__tablename__ = "tickets"

	id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
	                                      primary_key=True,
	                                      default=uuid.uuid4)

	title: Mapped[str] = mapped_column(String(255),
	                                   nullable=False)

	description: Mapped[str] = mapped_column(Text,
	                                         nullable=False)

	status: Mapped[str] = mapped_column(String(50),
	                                    nullable=False,
	                                    default="open")

	created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
	                                              ForeignKey("users.id",
	                                                         ondelete="RESTRICT"),
	                                              nullable=False,
	                                              index=True)

	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
	                                             default=datetime.utcnow,
	                                             nullable=False)

	# ORM relationships
	user = relationship("User", back_populates="tickets")