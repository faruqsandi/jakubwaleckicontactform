from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, JSON, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from contactform.database.models import Base
from contactform.mission.models import Mission


class FormSubmission(Base):
    """
    SQLAlchemy model for storing form submission results.

    This model captures information about form submissions to websites,
    including the domain, submitted field data, and submission status.
    """

    __tablename__ = "form_submissions"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to Mission
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"), nullable=False, index=True)

    # Domain information
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Submitted field data (stored as JSON object)
    # e.g., {"name": "John Doe", "email": "john@example.com", "message": "Hello"}
    submitted_fields: Mapped[dict[str, str]] = mapped_column(JSON, nullable=False)

    # Submission status
    status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # "pending", "success", "failed", "blocked"

    # Additional metadata
    submission_date: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Optional fields for additional context
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_data: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationship to mission
    mission: Mapped[Mission] = relationship("Mission", back_populates="form_submissions")

    def __repr__(self) -> str:
        return f"<FormSubmission(id={self.id}, mission_id={self.mission_id}, domain='{self.domain}', status='{self.status}')>"
