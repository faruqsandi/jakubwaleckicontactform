"""
Unit tests for ContactFormDetection CRUD operations.

This file contains basic tests for the CRUD functionality.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contactform.database.models import Base
from contactform.detection import ContactFormDetectionCRUD, ContactFormDetection


@pytest.fixture
def db_session():
    """Create a test database session."""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


@pytest.fixture
def sample_detection_data():
    """Sample data for testing."""
    return {
        "domain_name": "testsite.com",
        "form_url": "https://testsite.com/contact",
        "contact_form_present": True,
        "website_antibot_detection": False,
        "form_antibot_detection": True,
        "form_antibot_type": "recaptcha",
        "form_fields": ["name", "email", "message"],
        "field_selectors": {
            "name": "#name",
            "email": "#email",
            "message": "#message"
        },
        "submit_button_selector": "#submit",
        "form_action": "https://testsite.com/submit",
        "detection_status": "completed"
    }


class TestContactFormDetectionCRUD:
    """Test cases for ContactFormDetection CRUD operations."""

    def test_create_detection(self, db_session, sample_detection_data):
        """Test creating a new detection record."""
        detection = ContactFormDetectionCRUD.create(db_session, **sample_detection_data)

        assert detection.id is not None
        assert detection.domain_name == sample_detection_data["domain_name"]
        assert detection.form_url == sample_detection_data["form_url"]
        assert detection.contact_form_present == sample_detection_data["contact_form_present"]
        assert detection.form_antibot_type == sample_detection_data["form_antibot_type"]
        assert detection.form_fields == sample_detection_data["form_fields"]
        assert detection.field_selectors == sample_detection_data["field_selectors"]
        assert detection.detection_status == sample_detection_data["detection_status"]
        assert isinstance(detection.detection_date, datetime)
        assert isinstance(detection.last_updated, datetime)

    def test_get_by_id(self, db_session, sample_detection_data):
        """Test retrieving a detection record by ID."""
        # Create a detection
        created_detection = ContactFormDetectionCRUD.create(db_session, **sample_detection_data)

        # Retrieve it
        retrieved_detection = ContactFormDetectionCRUD.get_by_id(db_session, created_detection.id)

        assert retrieved_detection is not None
        assert retrieved_detection.id == created_detection.id
        assert retrieved_detection.domain_name == created_detection.domain_name

    def test_get_by_id_not_found(self, db_session):
        """Test retrieving a detection record that doesn't exist."""
        detection = ContactFormDetectionCRUD.get_by_id(db_session, 999)
        assert detection is None

    def test_get_by_domain(self, db_session, sample_detection_data):
        """Test retrieving detection records by domain."""
        domain = "testdomain.com"

        # Create multiple detections for the same domain
        data1 = {**sample_detection_data, "domain_name": domain, "form_url": "https://testdomain.com/contact1"}
        data2 = {**sample_detection_data, "domain_name": domain, "form_url": "https://testdomain.com/contact2"}

        ContactFormDetectionCRUD.create(db_session, **data1)
        ContactFormDetectionCRUD.create(db_session, **data2)

        # Retrieve by domain
        detections = ContactFormDetectionCRUD.get_by_domain(db_session, domain)

        assert len(detections) == 2
        assert all(d.domain_name == domain for d in detections)

    def test_get_by_url(self, db_session, sample_detection_data):
        """Test retrieving a detection record by URL."""
        # Create a detection
        created_detection = ContactFormDetectionCRUD.create(db_session, **sample_detection_data)

        # Retrieve by URL
        retrieved_detection = ContactFormDetectionCRUD.get_by_url(
            db_session, sample_detection_data["form_url"]
        )

        assert retrieved_detection is not None
        assert retrieved_detection.id == created_detection.id
        assert retrieved_detection.form_url == sample_detection_data["form_url"]

    def test_update_detection(self, db_session, sample_detection_data):
        """Test updating a detection record."""
        # Create a detection
        detection = ContactFormDetectionCRUD.create(db_session, **sample_detection_data)
        original_updated_time = detection.last_updated

        # Update it
        new_status = "verified"
        new_antibot_type = "hcaptcha"

        updated_detection = ContactFormDetectionCRUD.update(
            db_session,
            detection.id,
            detection_status=new_status,
            form_antibot_type=new_antibot_type
        )

        assert updated_detection is not None
        assert updated_detection.detection_status == new_status
        assert updated_detection.form_antibot_type == new_antibot_type
        assert updated_detection.last_updated > original_updated_time

    def test_update_status(self, db_session, sample_detection_data):
        """Test updating detection status."""
        # Create a detection
        detection = ContactFormDetectionCRUD.create(db_session, **sample_detection_data)

        # Update status
        new_status = "failed"
        updated_detection = ContactFormDetectionCRUD.update_status(
            db_session, detection.id, new_status
        )

        assert updated_detection is not None
        assert updated_detection.detection_status == new_status

    def test_delete_detection(self, db_session, sample_detection_data):
        """Test deleting a detection record."""
        # Create a detection
        detection = ContactFormDetectionCRUD.create(db_session, **sample_detection_data)
        detection_id = detection.id

        # Delete it
        deleted = ContactFormDetectionCRUD.delete(db_session, detection_id)
        assert deleted is True

        # Verify it's gone
        retrieved = ContactFormDetectionCRUD.get_by_id(db_session, detection_id)
        assert retrieved is None

    def test_delete_nonexistent(self, db_session):
        """Test deleting a detection that doesn't exist."""
        deleted = ContactFormDetectionCRUD.delete(db_session, 999)
        assert deleted is False

    def test_count_all(self, db_session, sample_detection_data):
        """Test counting all detections."""
        initial_count = ContactFormDetectionCRUD.count_all(db_session)

        # Create some detections
        ContactFormDetectionCRUD.create(db_session, **sample_detection_data)
        ContactFormDetectionCRUD.create(
            db_session,
            **{**sample_detection_data, "form_url": "https://testsite.com/contact2"}
        )

        final_count = ContactFormDetectionCRUD.count_all(db_session)
        assert final_count == initial_count + 2

    def test_count_by_status(self, db_session, sample_detection_data):
        """Test counting detections by status."""
        status = "completed"
        initial_count = ContactFormDetectionCRUD.count_by_status(db_session, status)

        # Create a detection with the status
        ContactFormDetectionCRUD.create(
            db_session,
            **{**sample_detection_data, "detection_status": status}
        )

        final_count = ContactFormDetectionCRUD.count_by_status(db_session, status)
        assert final_count == initial_count + 1

    def test_get_with_contact_forms(self, db_session, sample_detection_data):
        """Test getting detections with contact forms present."""
        # Create detections with and without contact forms
        ContactFormDetectionCRUD.create(
            db_session,
            **{**sample_detection_data, "contact_form_present": True}
        )
        ContactFormDetectionCRUD.create(
            db_session,
            **{**sample_detection_data, "contact_form_present": False, "form_url": "https://testsite.com/no-form"}
        )

        detections_with_forms = ContactFormDetectionCRUD.get_with_contact_forms(db_session)

        assert len(detections_with_forms) >= 1
        assert all(d.contact_form_present for d in detections_with_forms)

    def test_get_with_antibot_protection(self, db_session, sample_detection_data):
        """Test getting detections with anti-bot protection."""
        # Create detections with different anti-bot configurations
        ContactFormDetectionCRUD.create(
            db_session,
            **{**sample_detection_data, "website_antibot_detection": True, "form_antibot_detection": False}
        )
        ContactFormDetectionCRUD.create(
            db_session,
            **{**sample_detection_data, "website_antibot_detection": False, "form_antibot_detection": True, "form_url": "https://testsite.com/form-antibot"}
        )

        # Test different levels
        website_antibot = ContactFormDetectionCRUD.get_with_antibot_protection(db_session, "website")
        form_antibot = ContactFormDetectionCRUD.get_with_antibot_protection(db_session, "form")
        any_antibot = ContactFormDetectionCRUD.get_with_antibot_protection(db_session, "any")

        assert len(website_antibot) >= 1
        assert len(form_antibot) >= 1
        assert len(any_antibot) >= 2

    def test_search(self, db_session, sample_detection_data):
        """Test searching detections."""
        # Create detections
        ContactFormDetectionCRUD.create(db_session, **sample_detection_data)
        ContactFormDetectionCRUD.create(
            db_session,
            **{**sample_detection_data, "domain_name": "searchtest.com", "form_url": "https://searchtest.com/contact"}
        )

        # Search by domain
        results = ContactFormDetectionCRUD.search(db_session, "testsite")
        assert len(results) >= 1

        # Search by URL
        results = ContactFormDetectionCRUD.search(db_session, "searchtest")
        assert len(results) >= 1

    def test_delete_by_domain(self, db_session, sample_detection_data):
        """Test deleting all detections for a domain."""
        domain = "bulkdelete.com"

        # Create multiple detections for the domain
        for i in range(3):
            ContactFormDetectionCRUD.create(
                db_session,
                **{**sample_detection_data, "domain_name": domain, "form_url": f"https://{domain}/contact{i}"}
            )

        # Verify they exist
        initial_count = ContactFormDetectionCRUD.count_by_domain(db_session, domain)
        assert initial_count == 3

        # Delete them all
        deleted_count = ContactFormDetectionCRUD.delete_by_domain(db_session, domain)
        assert deleted_count == 3

        # Verify they're gone
        final_count = ContactFormDetectionCRUD.count_by_domain(db_session, domain)
        assert final_count == 0


if __name__ == "__main__":
    # Run tests if this file is executed directly
    pytest.main([__file__, "-v"])
