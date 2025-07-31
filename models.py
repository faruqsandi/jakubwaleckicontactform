from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
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
    website_antibot_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Form URL and presence
    form_url: Mapped[str] = mapped_column(Text, nullable=False)
    contact_form_present: Mapped[bool] = mapped_column(Boolean, default=False)

    # Anti-bot detection on form level
    form_antibot_detection: Mapped[bool] = mapped_column(Boolean, default=False)
    form_antibot_type: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True)  # e.g., "recaptcha", "hcaptcha", "cloudflare"
    form_antibot_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Form fields information
    form_fields: Mapped[Optional[List[str]]] = mapped_column(
        JSON, nullable=True)  # e.g., ["name", "email", "message", "phone"]

    # CSS selectors for each field (stored as JSON object)
    # e.g., {"name": "#name", "email": "#email", "message": "#message"}
    field_selectors: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)

    # Submit button selector
    submit_button_selector: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Additional metadata
    detection_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(
        timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    form_method: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # "GET" or "POST"
    form_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Form action URL

    # Detection confidence and status
    detection_confidence: Mapped[Optional[float]] = mapped_column(nullable=True)  # 0.0 to 1.0
    detection_status: Mapped[str] = mapped_column(String(50), default="pending")  # "pending", "completed", "failed"

    # Error information
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<ContactFormDetection(id={self.id}, domain='{self.domain_name}', form_present={self.contact_form_present})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model instance to a dictionary for easy serialization."""
        return {
            "id": self.id,
            "domain_name": self.domain_name,
            "website_antibot_detection": self.website_antibot_detection,
            "website_antibot_details": self.website_antibot_details,
            "form_url": self.form_url,
            "contact_form_present": self.contact_form_present,
            "form_antibot_detection": self.form_antibot_detection,
            "form_antibot_type": self.form_antibot_type,
            "form_antibot_details": self.form_antibot_details,
            "form_fields": self.form_fields,
            "field_selectors": self.field_selectors,
            "submit_button_selector": self.submit_button_selector,
            "detection_date": self.detection_date.isoformat() if self.detection_date else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "form_method": self.form_method,
            "form_action": self.form_action,
            "detection_confidence": self.detection_confidence,
            "detection_status": self.detection_status,
            "error_message": self.error_message
        }
