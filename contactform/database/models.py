from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Text, DateTime, JSON, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ContactFormDetection(Base):
    """
    SQLAlchemy model for storing contact form detection results from websites.

    This model captures information about contact forms found on websites,
    including anti-bot detection mechanisms and form field details.
    """

    __tablename__ = "contact_form_detections"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Domain information
    domain_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Anti-bot detection on website level
    website_antibot_detection: Mapped[bool] = mapped_column(Boolean, default=False)
    website_antibot_details: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Form URL and presence
    form_url: Mapped[str] = mapped_column(Text, nullable=False)
    contact_form_present: Mapped[bool] = mapped_column(Boolean, default=False)

    # Anti-bot detection on form level
    form_antibot_detection: Mapped[bool] = mapped_column(Boolean, default=False)
    form_antibot_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # e.g., "recaptcha", "hcaptcha", "cloudflare"
    form_antibot_details: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Form fields information
    form_fields: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )  # e.g., ["name", "email", "message", "phone"]

    # CSS selectors for each field (stored as JSON object)
    # e.g., {"name": "#name", "email": "#email", "message": "#message"}
    field_selectors: Mapped[dict[str, str] | None] = mapped_column(JSON, nullable=True)

    # Submit button selector
    submit_button_selector: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    # Additional metadata
    detection_date: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    form_method: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )  # "GET" or "POST"
    form_action: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Form action URL

    # Detection confidence and status
    detection_confidence: Mapped[float | None] = mapped_column(
        nullable=True
    )  # 0.0 to 1.0
    detection_status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # "pending", "completed", "failed"

    # Error information
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<ContactFormDetection(id={self.id}, domain='{self.domain_name}', form_present={self.contact_form_present})>"
