# app/models/user.py
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
	__tablename__ = "users"

	id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
	                                      primary_key=True,
	                                      default=uuid.uuid4)

	username: Mapped[str] = mapped_column(String(255),
	                                      unique=True,
	                                      index=True,
	                                      nullable=False)

	email: Mapped[str] = mapped_column(String(255),
	                                   unique=True,
	                                   index=True,
	                                   nullable=False)

	role: Mapped[str] = mapped_column(String(50),
	                                  nullable=False,
	                                  default="user")

	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
	                                             default=datetime.utcnow,
	                                             nullable=False)

	tickets = relationship("Ticket", back_populates="user")
	documents = relationship("Document", back_populates="owner")



