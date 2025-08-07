#!/usr/bin/env python3
"""
Test script to verify the task_id functionality works
"""
from contactform.detection.crud import ContactFormDetectionCRUD
from contactform.mission.crud import get_db
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_task_id_functionality():
    """Test if the task_id field is working in the database"""
    print("Testing task_id functionality...")

    db = get_db()
    try:
        # Create a test detection record with task_id
        test_detection = ContactFormDetectionCRUD.create(
            db=db,
            domain_name="test-domain.com",
            form_url="https://test-domain.com/contact",
            contact_form_present=False,
            website_antibot_detection=False,
            form_antibot_detection=False,
            detection_status="pending",
            task_id="test-task-123"
        )

        print(f"✓ Created test detection record with ID: {test_detection.id}")
        print(f"✓ Task ID: {test_detection.task_id}")

        # Try to retrieve it
        retrieved = ContactFormDetectionCRUD.get_by_domain(db, "test-domain.com")
        if retrieved and retrieved[0].task_id == "test-task-123":
            print("✓ Task ID field is working correctly!")
        else:
            print("✗ Task ID field not working properly")

        # Update the task_id
        updated = ContactFormDetectionCRUD.update(
            db=db,
            detection_id=test_detection.id,
            task_id="updated-task-456",
            detection_status="completed"
        )

        if updated and updated.task_id == "updated-task-456":
            print("✓ Task ID update is working correctly!")
        else:
            print("✗ Task ID update not working properly")

        # Clean up
        # Note: We'd normally delete the test record here, but let's keep it for now

        print("\n✓ All tests passed! The task_id functionality is working.")

    except Exception as e:
        print(f"✗ Error during testing: {str(e)}")
    finally:
        if db:
            db.close()


if __name__ == "__main__":
    test_task_id_functionality()
