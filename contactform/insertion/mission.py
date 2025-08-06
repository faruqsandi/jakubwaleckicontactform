from datetime import datetime, timezone
from sqlalchemy import DateTime, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from contactform.database.models import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import FormSubmission


class Mission(Base):
    """
    SQLAlchemy model for storing form submission missions.

    This model represents a mission configuration that defines the fields
    to be filled for multiple form submissions across different domains.
    """

    __tablename__ = "missions"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Pre-defined fields to fill for each submission in this mission
    # e.g., {"name": "John Doe", "email": "john@example.com", "message": "Test message"}
    pre_defined_fields: Mapped[dict[str, str]] = mapped_column(JSON, nullable=False)

    # Metadata
    created_date: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship to form submissions
    form_submissions: Mapped[list["FormSubmission"]] = relationship(
        "FormSubmission", back_populates="mission"
    )

    def __repr__(self) -> str:
        return f"<Mission(id={self.id}, fields={list(self.pre_defined_fields.keys())})>"
