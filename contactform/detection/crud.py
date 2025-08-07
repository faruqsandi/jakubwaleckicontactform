"""
CRUD operations for ContactFormDetection model.

This module provides Create, Read, Update, and Delete operations
for the ContactFormDetection model.
"""

from datetime import datetime, timezone
from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .models import ContactFormDetection


class ContactFormDetectionCRUD:
    """CRUD operations for ContactFormDetection model."""

    @staticmethod
    def create(
        db: Session,
        domain_name: str,
        form_url: str | None = None,
        contact_form_present: bool = False,
        website_antibot_detection: bool = False,
        form_antibot_detection: bool = False,
        form_antibot_type: str | None = None,
        form_fields: list[str] | None = None,
        field_selectors: dict[str, str] | None = None,
        submit_button_selector: str | None = None,
        form_action: str | None = None,
        detection_status: str = "pending",
        **kwargs: Any,
    ) -> ContactFormDetection:
        """
        Create a new ContactFormDetection record.

        Args:
            db: Database session
            domain_name: Domain name of the website
            form_url: URL where the form was found
            contact_form_present: Whether a contact form is present
            website_antibot_detection: Whether anti-bot detection exists on website level
            form_antibot_detection: Whether anti-bot detection exists on form level
            form_antibot_type: Type of anti-bot protection (e.g., "recaptcha", "hcaptcha")
            form_fields: List of form field names
            field_selectors: CSS selectors for form fields
            submit_button_selector: CSS selector for submit button
            form_action: Form action URL
            detection_status: Status of detection ("pending", "completed", "failed")
            **kwargs: Additional keyword arguments

        Returns:
            Created ContactFormDetection instance
        """
        db_detection = ContactFormDetection(
            domain_name=domain_name,
            form_url=form_url,
            contact_form_present=contact_form_present,
            website_antibot_detection=website_antibot_detection,
            form_antibot_detection=form_antibot_detection,
            form_antibot_type=form_antibot_type,
            form_fields=form_fields,
            field_selectors=field_selectors,
            submit_button_selector=submit_button_selector,
            form_action=form_action,
            detection_status=detection_status,
            **kwargs,
        )

        db.add(db_detection)
        db.commit()
        db.refresh(db_detection)
        return db_detection

    @staticmethod
    def get_by_id(db: Session, detection_id: int) -> ContactFormDetection | None:
        """
        Get a ContactFormDetection record by ID.

        Args:
            db: Database session
            detection_id: ID of the detection record

        Returns:
            ContactFormDetection instance or None if not found
        """
        return (
            db.query(ContactFormDetection)
            .filter(ContactFormDetection.id == detection_id)
            .first()
        )

    @staticmethod
    def get_by_domain(
        db: Session, domain_name: str, limit: int | None = None
    ) -> list[ContactFormDetection]:
        """
        Get ContactFormDetection records by domain name.

        Args:
            db: Database session
            domain_name: Domain name to search for
            limit: Maximum number of records to return

        Returns:
            List of ContactFormDetection instances
        """
        query = (
            db.query(ContactFormDetection)
            .filter(ContactFormDetection.domain_name == domain_name)
            .order_by(desc(ContactFormDetection.detection_date))
        )

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def update(
        db: Session, detection_id: int, **update_data: Any
    ) -> ContactFormDetection | None:
        """
        Update a ContactFormDetection record.

        Args:
            db: Database session
            detection_id: ID of the detection record to update
            **update_data: Fields to update

        Returns:
            Updated ContactFormDetection instance or None if not found
        """
        db_detection = (
            db.query(ContactFormDetection)
            .filter(ContactFormDetection.id == detection_id)
            .first()
        )

        if not db_detection:
            return None

        # Update last_updated timestamp
        update_data["last_updated"] = datetime.now(timezone.utc)

        for field, value in update_data.items():
            if hasattr(db_detection, field):
                setattr(db_detection, field, value)

        db.commit()
        db.refresh(db_detection)
        return db_detection
