"""
CRUD operations for ContactFormDetection model.

This module provides Create, Read, Update, and Delete operations
for the ContactFormDetection model.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from .models import ContactFormDetection


class ContactFormDetectionCRUD:
    """CRUD operations for ContactFormDetection model."""

    @staticmethod
    def create(
        db: Session,
        domain_name: str,
        form_url: str,
        contact_form_present: bool = False,
        website_antibot_detection: bool = False,
        form_antibot_detection: bool = False,
        form_antibot_type: Optional[str] = None,
        form_fields: Optional[List[str]] = None,
        field_selectors: Optional[Dict[str, str]] = None,
        submit_button_selector: Optional[str] = None,
        form_action: Optional[str] = None,
        detection_status: str = "pending",
        **kwargs: Any
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
            **kwargs
        )

        db.add(db_detection)
        db.commit()
        db.refresh(db_detection)
        return db_detection

    @staticmethod
    def get_by_id(db: Session, detection_id: int) -> Optional[ContactFormDetection]:
        """
        Get a ContactFormDetection record by ID.

        Args:
            db: Database session
            detection_id: ID of the detection record

        Returns:
            ContactFormDetection instance or None if not found
        """
        return db.query(ContactFormDetection).filter(
            ContactFormDetection.id == detection_id
        ).first()

    @staticmethod
    def get_by_domain(
        db: Session,
        domain_name: str,
        limit: Optional[int] = None
    ) -> List[ContactFormDetection]:
        """
        Get ContactFormDetection records by domain name.

        Args:
            db: Database session
            domain_name: Domain name to search for
            limit: Maximum number of records to return

        Returns:
            List of ContactFormDetection instances
        """
        query = db.query(ContactFormDetection).filter(
            ContactFormDetection.domain_name == domain_name
        ).order_by(desc(ContactFormDetection.detection_date))

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get_by_url(db: Session, form_url: str) -> Optional[ContactFormDetection]:
        """
        Get a ContactFormDetection record by form URL.

        Args:
            db: Database session
            form_url: Form URL to search for

        Returns:
            ContactFormDetection instance or None if not found
        """
        return db.query(ContactFormDetection).filter(
            ContactFormDetection.form_url == form_url
        ).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "detection_date",
        order_direction: str = "desc"
    ) -> List[ContactFormDetection]:
        """
        Get all ContactFormDetection records with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            order_direction: "asc" or "desc"

        Returns:
            List of ContactFormDetection instances
        """
        order_field = getattr(ContactFormDetection, order_by, ContactFormDetection.detection_date)
        order_func = desc if order_direction.lower() == "desc" else asc

        return db.query(ContactFormDetection).order_by(
            order_func(order_field)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_status(
        db: Session,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ContactFormDetection]:
        """
        Get ContactFormDetection records by detection status.

        Args:
            db: Database session
            status: Detection status to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ContactFormDetection instances
        """
        return db.query(ContactFormDetection).filter(
            ContactFormDetection.detection_status == status
        ).order_by(desc(ContactFormDetection.detection_date)).offset(skip).limit(limit).all()

    @staticmethod
    def get_with_contact_forms(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[ContactFormDetection]:
        """
        Get ContactFormDetection records where contact forms are present.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ContactFormDetection instances with contact forms
        """
        return db.query(ContactFormDetection).filter(
            ContactFormDetection.contact_form_present == True
        ).order_by(desc(ContactFormDetection.detection_date)).offset(skip).limit(limit).all()

    @staticmethod
    def get_with_antibot_protection(
        db: Session,
        level: str = "both",  # "website", "form", "both", "any"
        skip: int = 0,
        limit: int = 100
    ) -> List[ContactFormDetection]:
        """
        Get ContactFormDetection records with anti-bot protection.

        Args:
            db: Database session
            level: Level of anti-bot protection ("website", "form", "both", "any")
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ContactFormDetection instances with anti-bot protection
        """
        if level == "website":
            filter_condition = ContactFormDetection.website_antibot_detection == True
        elif level == "form":
            filter_condition = ContactFormDetection.form_antibot_detection == True
        elif level == "both":
            filter_condition = and_(
                ContactFormDetection.website_antibot_detection == True,
                ContactFormDetection.form_antibot_detection == True
            )
        else:  # "any"
            filter_condition = or_(
                ContactFormDetection.website_antibot_detection == True,
                ContactFormDetection.form_antibot_detection == True
            )

        return db.query(ContactFormDetection).filter(
            filter_condition
        ).order_by(desc(ContactFormDetection.detection_date)).offset(skip).limit(limit).all()

    @staticmethod
    def update(
        db: Session,
        detection_id: int,
        **update_data: Any
    ) -> Optional[ContactFormDetection]:
        """
        Update a ContactFormDetection record.

        Args:
            db: Database session
            detection_id: ID of the detection record to update
            **update_data: Fields to update

        Returns:
            Updated ContactFormDetection instance or None if not found
        """
        db_detection = db.query(ContactFormDetection).filter(
            ContactFormDetection.id == detection_id
        ).first()

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

    @staticmethod
    def update_status(
        db: Session,
        detection_id: int,
        status: str
    ) -> Optional[ContactFormDetection]:
        """
        Update the detection status of a record.

        Args:
            db: Database session
            detection_id: ID of the detection record
            status: New status value

        Returns:
            Updated ContactFormDetection instance or None if not found
        """
        return ContactFormDetectionCRUD.update(
            db, detection_id, detection_status=status
        )

    @staticmethod
    def delete(db: Session, detection_id: int) -> bool:
        """
        Delete a ContactFormDetection record.

        Args:
            db: Database session
            detection_id: ID of the detection record to delete

        Returns:
            True if deleted successfully, False if not found
        """
        db_detection = db.query(ContactFormDetection).filter(
            ContactFormDetection.id == detection_id
        ).first()

        if not db_detection:
            return False

        db.delete(db_detection)
        db.commit()
        return True

    @staticmethod
    def delete_by_domain(db: Session, domain_name: str) -> int:
        """
        Delete all ContactFormDetection records for a specific domain.

        Args:
            db: Database session
            domain_name: Domain name to delete records for

        Returns:
            Number of deleted records
        """
        deleted_count = db.query(ContactFormDetection).filter(
            ContactFormDetection.domain_name == domain_name
        ).delete()

        db.commit()
        return deleted_count

    @staticmethod
    def count_all(db: Session) -> int:
        """
        Count all ContactFormDetection records.

        Args:
            db: Database session

        Returns:
            Total number of records
        """
        return db.query(ContactFormDetection).count()

    @staticmethod
    def count_by_status(db: Session, status: str) -> int:
        """
        Count ContactFormDetection records by status.

        Args:
            db: Database session
            status: Detection status to count

        Returns:
            Number of records with the specified status
        """
        return db.query(ContactFormDetection).filter(
            ContactFormDetection.detection_status == status
        ).count()

    @staticmethod
    def count_by_domain(db: Session, domain_name: str) -> int:
        """
        Count ContactFormDetection records for a specific domain.

        Args:
            db: Database session
            domain_name: Domain name to count records for

        Returns:
            Number of records for the domain
        """
        return db.query(ContactFormDetection).filter(
            ContactFormDetection.domain_name == domain_name
        ).count()

    @staticmethod
    def search(
        db: Session,
        search_term: str,
        search_fields: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ContactFormDetection]:
        """
        Search ContactFormDetection records by term in specified fields.

        Args:
            db: Database session
            search_term: Term to search for
            search_fields: List of fields to search in (default: domain_name, form_url)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching ContactFormDetection instances
        """
        if search_fields is None:
            search_fields = ["domain_name", "form_url"]

        conditions = []
        for field in search_fields:
            if hasattr(ContactFormDetection, field):
                field_attr = getattr(ContactFormDetection, field)
                conditions.append(field_attr.ilike(f"%{search_term}%"))

        if not conditions:
            return []

        return db.query(ContactFormDetection).filter(
            or_(*conditions)
        ).order_by(desc(ContactFormDetection.detection_date)).offset(skip).limit(limit).all()


# Convenience functions for direct usage
def create_detection(db: Session, **kwargs: Any) -> ContactFormDetection:
    """Convenience function to create a detection record."""
    return ContactFormDetectionCRUD.create(db, **kwargs)


def get_detection(db: Session, detection_id: int) -> Optional[ContactFormDetection]:
    """Convenience function to get a detection record by ID."""
    return ContactFormDetectionCRUD.get_by_id(db, detection_id)


def update_detection(db: Session, detection_id: int, **kwargs: Any) -> Optional[ContactFormDetection]:
    """Convenience function to update a detection record."""
    return ContactFormDetectionCRUD.update(db, detection_id, **kwargs)


def delete_detection(db: Session, detection_id: int) -> bool:
    """Convenience function to delete a detection record."""
    return ContactFormDetectionCRUD.delete(db, detection_id)
