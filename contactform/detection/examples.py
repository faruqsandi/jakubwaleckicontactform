"""
Example usage of ContactFormDetection CRUD operations.

This file demonstrates how to use the CRUD functionality
for the ContactFormDetection model.
"""

from sqlalchemy.orm import Session
from contactform.detection import ContactFormDetectionCRUD, create_detection, get_detection


def example_crud_operations(db: Session):
    """
    Example demonstrating various CRUD operations.

    Args:
        db: SQLAlchemy database session
    """

    # Create a new detection record
    print("Creating a new contact form detection...")
    detection = create_detection(
        db=db,
        domain_name="example.com",
        form_url="https://example.com/contact",
        contact_form_present=True,
        website_antibot_detection=False,
        form_antibot_detection=True,
        form_antibot_type="recaptcha",
        form_fields=["name", "email", "message", "phone"],
        field_selectors={
            "name": "#contact-name",
            "email": "#contact-email",
            "message": "#contact-message",
            "phone": "#contact-phone"
        },
        submit_button_selector="#submit-btn",
        form_action="https://example.com/submit-contact",
        detection_status="completed"
    )
    print(f"Created detection with ID: {detection.id}")

    # Read the detection record
    print(f"\nRetrieving detection by ID {detection.id}...")
    retrieved_detection = get_detection(db, detection.id)
    if retrieved_detection:
        print(f"Retrieved: {retrieved_detection}")

    # Update the detection record
    print(f"\nUpdating detection {detection.id}...")
    updated_detection = ContactFormDetectionCRUD.update(
        db=db,
        detection_id=detection.id,
        form_antibot_type="hcaptcha",
        detection_status="updated"
    )
    if updated_detection:
        print(f"Updated anti-bot type to: {updated_detection.form_antibot_type}")

    # Get detections by domain
    print(f"\nGetting all detections for domain 'example.com'...")
    domain_detections = ContactFormDetectionCRUD.get_by_domain(db, "example.com")
    print(f"Found {len(domain_detections)} detections for this domain")

    # Get detections with contact forms
    print(f"\nGetting detections with contact forms present...")
    form_detections = ContactFormDetectionCRUD.get_with_contact_forms(db, limit=5)
    print(f"Found {len(form_detections)} detections with contact forms")

    # Get detections with anti-bot protection
    print(f"\nGetting detections with any anti-bot protection...")
    antibot_detections = ContactFormDetectionCRUD.get_with_antibot_protection(
        db, level="any", limit=5
    )
    print(f"Found {len(antibot_detections)} detections with anti-bot protection")

    # Search detections
    print(f"\nSearching for detections containing 'example'...")
    search_results = ContactFormDetectionCRUD.search(
        db, "example", search_fields=["domain_name", "form_url"], limit=5
    )
    print(f"Found {len(search_results)} detections matching search")

    # Count operations
    print(f"\nCounting detections...")
    total_count = ContactFormDetectionCRUD.count_all(db)
    completed_count = ContactFormDetectionCRUD.count_by_status(db, "completed")
    domain_count = ContactFormDetectionCRUD.count_by_domain(db, "example.com")

    print(f"Total detections: {total_count}")
    print(f"Completed detections: {completed_count}")
    print(f"Detections for example.com: {domain_count}")

    # Get all detections with pagination
    print(f"\nGetting first 10 detections ordered by date...")
    all_detections = ContactFormDetectionCRUD.get_all(
        db, skip=0, limit=10, order_by="detection_date", order_direction="desc"
    )
    print(f"Retrieved {len(all_detections)} detections")

    # Update status
    print(f"\nUpdating status of detection {detection.id}...")
    status_updated = ContactFormDetectionCRUD.update_status(
        db, detection.id, "verified"
    )
    if status_updated:
        print(f"Status updated to: {status_updated.detection_status}")

    print(f"\nCRUD operations example completed!")

    return detection.id


def cleanup_example_data(db: Session, detection_id: int):
    """
    Clean up the example data created.

    Args:
        db: SQLAlchemy database session
        detection_id: ID of the detection to delete
    """
    print(f"\nCleaning up example data...")
    deleted = ContactFormDetectionCRUD.delete(db, detection_id)
    if deleted:
        print(f"Successfully deleted detection {detection_id}")
    else:
        print(f"Detection {detection_id} not found for deletion")


# Example of bulk operations
def example_bulk_operations(db: Session):
    """
    Example of bulk operations.

    Args:
        db: SQLAlchemy database session
    """
    print("\n" + "="*50)
    print("BULK OPERATIONS EXAMPLE")
    print("="*50)

    # Create multiple detections for the same domain
    test_domain = "testbulk.com"
    detection_ids = []

    print(f"Creating multiple detections for {test_domain}...")
    for i in range(3):
        detection = create_detection(
            db=db,
            domain_name=test_domain,
            form_url=f"https://{test_domain}/contact-{i}",
            contact_form_present=True,
            detection_status="pending"
        )
        detection_ids.append(detection.id)
        print(f"Created detection {detection.id}")

    # Count detections for this domain
    domain_count = ContactFormDetectionCRUD.count_by_domain(db, test_domain)
    print(f"Total detections for {test_domain}: {domain_count}")

    # Delete all detections for this domain
    print(f"Deleting all detections for {test_domain}...")
    deleted_count = ContactFormDetectionCRUD.delete_by_domain(db, test_domain)
    print(f"Deleted {deleted_count} detections")

    print("Bulk operations example completed!")


if __name__ == "__main__":
    # This would require a database session setup
    # The actual usage would depend on your database configuration
    print("This is an example file. To use it, you need to:")
    print("1. Set up a database session")
    print("2. Import this module and call the example functions")
    print("3. Pass the database session to the functions")

    print("\nExample usage:")
    print("""
    from sqlalchemy.orm import sessionmaker
    from your_database_config import engine
    from contactform.detection.examples import example_crud_operations
    
    Session = sessionmaker(bind=engine)
    with Session() as db:
        detection_id = example_crud_operations(db)
        cleanup_example_data(db, detection_id)
    """)
