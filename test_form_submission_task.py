#!/usr/bin/env python3
"""
Test script for the background_form_submission_task.

This script demonstrates how to use the new Huey task for form submission.
"""

from huey_config import background_form_submission_task, get_task_status
from contactform.insertion.models import FormSubmission
from contactform.mission.crud import get_db


def test_form_submission_task():
    """
    Test the background form submission task.

    This function demonstrates how to:
    1. Create a FormSubmission record (or use an existing one)
    2. Queue the background task
    3. Check task status
    """

    # Get database session
    db = get_db()

    try:
        # Example: Get an existing FormSubmission record
        # In practice, you would create this when setting up the mission
        form_submission = db.query(FormSubmission).first()

        if not form_submission:
            print("No FormSubmission records found. Please create one first.")
            print(
                "You can create FormSubmission records through the web interface or programmatically."
            )
            return

        print(f"Testing with FormSubmission ID: {form_submission.id}")
        print(f"Domain: {form_submission.domain}")
        print(f"Mission ID: {form_submission.mission_id}")
        print(f"Current Status: {form_submission.status}")

        # Queue the background task
        print("\nQueueing background form submission task...")
        task = background_form_submission_task(form_submission.id)
        task_id = task.id

        print(f"Task queued with ID: {task_id}")

        # Check initial task status
        status = get_task_status(task_id)
        print(f"Initial task status: {status}")

        print("\nTo check task progress, run:")
        print(
            f"  python -c \"from huey_config import get_task_status; print(get_task_status('{task_id}'))\""
        )

        print("\nTo get the task result when completed, run:")
        print(
            f"  python -c \"from huey_config import huey; from huey.api import Result, Task; result = Result(huey=huey, task=Task(id='{task_id}')); print(result.get(blocking=False))\""
        )

    finally:
        db.close()


def create_example_form_submission():
    """
    Create an example FormSubmission record for testing.

    Note: This requires an existing Mission and ContactFormDetection record.
    """
    from contactform.mission.models import Mission

    db = get_db()

    try:
        # Get the first available mission
        mission = db.query(Mission).first()

        if not mission:
            print(
                "No Mission records found. Please create a mission first through the web interface."
            )
            return

        # Create a test FormSubmission
        form_submission = FormSubmission(
            mission_id=mission.id,
            domain="example.com",  # Replace with actual domain
            submitted_fields={},
            status="pending",
        )

        db.add(form_submission)
        db.commit()

        print(f"Created FormSubmission with ID: {form_submission.id}")
        print(f"Domain: {form_submission.domain}")
        print(f"Mission ID: {form_submission.mission_id}")

        return form_submission.id

    except Exception as e:
        db.rollback()
        print(f"Error creating FormSubmission: {e}")
        return None
    finally:
        db.close()


if __name__ == "__main__":
    print("Background Form Submission Task Test")
    print("=" * 40)

    # Uncomment the following line to create a test FormSubmission first
    # create_example_form_submission()

    test_form_submission_task()
