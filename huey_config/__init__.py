from huey.api import Result, Task
import os
from huey import SqliteHuey
from datetime import datetime
from typing import Dict, Any

# Use SQLite database for Huey tasks - now in the same directory as this module
HUEY_DB_PATH = os.path.join(os.path.dirname(__file__), "huey_tasks.db")

# Initialize Huey with SQLite backend
huey = SqliteHuey(
    name="contactform_huey",
    filename=HUEY_DB_PATH,
    immediate=False,  # Set to True for testing to run tasks immediately
    # consumer_options={'workers': 4, 'periodic': True}
)


@huey.task()
def dummy_task(task_name="Default Task", delay_seconds=5):
    """
    A dummy task for testing Huey functionality.

    Args:
        task_name (str): Name of the task
        delay_seconds (int): How long the task should "run"

    Returns:
        dict: Task result with completion info
    """
    import time

    start_time = datetime.now()

    # Simulate some work
    time.sleep(delay_seconds)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    result = {
        "task_name": task_name,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration,
        "status": "completed",
    }

    return result


@huey.task()
def background_form_detection_task(domain):
    """
    Background task for form detection using the actual selenium handler.

    Args:
        domain (str): Domain to detect forms for

    Returns:
        dict: Detection result with status and data
    """
    try:
        from contactform.detection.selenium_handler import search_domain_form
        from contactform.mission.crud import get_db
        from contactform.detection.crud import ContactFormDetectionCRUD

        # Get database session
        db = get_db()

        try:
            # Perform actual form detection
            detection_result = search_domain_form(domain, db)

            if detection_result:
                # Update the detection record to mark as completed and clear task_id
                ContactFormDetectionCRUD.update(
                    db=db,
                    detection_id=detection_result.id,
                    detection_status="completed",
                    # task_id=None  # Clear task_id when completed
                )

                return {
                    "domain": domain,
                    "status": "completed",
                    "detection_id": detection_result.id,
                    "form_detected": detection_result.contact_form_present,
                    "form_url": detection_result.form_url,
                    "detection_time": datetime.now().isoformat(),
                    "success": True,
                }
            else:
                return {
                    "domain": domain,
                    "status": "failed",
                    "error": "No detection record found",
                    "detection_time": datetime.now().isoformat(),
                    "success": False,
                }

        finally:
            if db:
                db.close()

    except Exception as e:
        # Update detection status to failed if we can
        try:
            from contactform.mission.crud import get_db
            from contactform.detection.crud import ContactFormDetectionCRUD

            db = get_db()
            try:
                # Find detection record and mark as failed
                detections = ContactFormDetectionCRUD.get_by_domain(db, domain)
                for detection in detections:
                    if detection.detection_status == "pending":
                        ContactFormDetectionCRUD.update(
                            db=db,
                            detection_id=detection.id,
                            detection_status="failed",
                            task_id=None,  # Clear task_id when failed
                        )
                        break
            finally:
                if db:
                    db.close()
        except:
            pass  # Ignore errors in error handling

        return {
            "domain": domain,
            "status": "failed",
            "error": str(e),
            "detection_time": datetime.now().isoformat(),
            "success": False,
        }


@huey.task()
def background_form_submission_task(form_submission_id: int) -> dict[str, Any]:
    """
    Background task for form submission using selenium handler.

    Args:
        form_submission_id (int): FormSubmission ID to process

    Returns:
        dict: Submission result with status and data
    """
    try:
        from contactform.insertion.models import FormSubmission
        from contactform.detection.crud import ContactFormDetectionCRUD
        from contactform.mission.crud import get_db
        from contactform.detection.selenium_handler import setup_webdriver
        from contactform.insertion.form_check import (
            fill_and_submit_form,
            verify_form_elements,
        )
        from selenium.common.exceptions import WebDriverException

        # Get database session
        db = get_db()

        try:
            # Get FormSubmission record
            form_submission = (
                db.query(FormSubmission)
                .filter(FormSubmission.id == form_submission_id)
                .first()
            )

            if not form_submission:
                return {
                    "form_submission_id": form_submission_id,
                    "status": "failed",
                    "error": "FormSubmission record not found",
                    "submission_time": datetime.now().isoformat(),
                    "success": False,
                }

            domain = form_submission.domain

            # Get ContactFormDetection for this domain
            detections = ContactFormDetectionCRUD.get_by_domain(db, domain)
            completed_detections = [
                d for d in detections if d.detection_status == "completed"
            ]

            if not completed_detections:
                # Update FormSubmission status
                form_submission.status = "failed"
                form_submission.task_status = "failed"
                form_submission.error_message = (
                    "No completed form detection found for domain"
                )
                db.commit()

                return {
                    "form_submission_id": form_submission_id,
                    "domain": domain,
                    "status": "failed",
                    "error": "No completed form detection found for domain",
                    "submission_time": datetime.now().isoformat(),
                    "success": False,
                }

            # Use the first completed detection
            detection = completed_detections[0]

            if not detection.form_url:
                # Update FormSubmission status
                form_submission.status = "failed"
                form_submission.task_status = "failed"
                form_submission.error_message = "No form URL found in detection"
                db.commit()

                return {
                    "form_submission_id": form_submission_id,
                    "domain": domain,
                    "status": "failed",
                    "error": "No form URL found in detection",
                    "submission_time": datetime.now().isoformat(),
                    "success": False,
                }

            # Set up WebDriver
            driver = None
            try:
                driver = setup_webdriver(headless=False)

                # Navigate to form URL
                driver.get(detection.form_url)

                # Prepare form_info structure from detection data
                form_info: dict[str, Any] = {
                    "fields": [],
                    "submit_button": None,
                    "protection": [],
                }

                # Build fields array from detection data
                if detection.form_fields and detection.field_selectors:
                    for field_name in detection.form_fields:
                        if field_name in detection.field_selectors:
                            form_info["fields"].append(
                                {
                                    "label": field_name,
                                    "selector": detection.field_selectors[field_name],
                                    "type": field_name,  # Use field name as type
                                }
                            )

                # Add submit button info
                if detection.submit_button_selector:
                    form_info["submit_button"] = {
                        "label": "Submit",
                        "selector": detection.submit_button_selector,
                    }

                # Add protection info if available
                if detection.form_antibot_detection and detection.form_antibot_type:
                    form_info["protection"] = [
                        {"type": "captcha", "issuer": detection.form_antibot_type}
                    ]

                # Verify form elements
                verification_result = verify_form_elements(driver, form_info)

                if verification_result is not True:
                    # Update FormSubmission with verification failure
                    form_submission.status = "failed"
                    form_submission.task_status = "failed"
                    error_details = (
                        verification_result.get("errors", [])
                        if isinstance(verification_result, dict)
                        else ["Form verification failed"]
                    )
                    form_submission.error_message = (
                        f"Form verification failed: {'; '.join(error_details)}"
                    )
                    db.commit()

                    return {
                        "form_submission_id": form_submission_id,
                        "domain": domain,
                        "status": "failed",
                        "error": f"Form verification failed: {'; '.join(error_details)}",
                        "verification_details": verification_result,
                        "submission_time": datetime.now().isoformat(),
                        "success": False,
                    }

                # Get predefined values from mission
                mission_values = form_submission.mission.pre_defined_fields

                # Fill and submit the form
                submission_result = fill_and_submit_form(
                    driver, form_info, mission_values
                )

                if submission_result is True:
                    # Update FormSubmission with success
                    form_submission.status = "success"
                    form_submission.task_status = "completed"
                    form_submission.submitted_fields = mission_values
                    form_submission.response_data = (
                        f"Form submitted successfully to {detection.form_url}"
                    )
                    db.commit()

                    return {
                        "form_submission_id": form_submission_id,
                        "domain": domain,
                        "status": "success",
                        "form_url": detection.form_url,
                        "submitted_fields": mission_values,
                        "submission_time": datetime.now().isoformat(),
                        "success": True,
                    }
                else:
                    # Update FormSubmission with submission failure
                    form_submission.status = "failed"
                    form_submission.task_status = "failed"
                    error_details: list[str] = []
                    if isinstance(submission_result, dict):
                        for error_type in ["fill_errors", "submit_errors"]:
                            if error_type in submission_result:
                                error_details.extend(submission_result[error_type])

                    error_message = (
                        f"Form submission failed: {'; '.join(error_details)}"
                        if error_details
                        else "Form submission failed"
                    )
                    form_submission.error_message = error_message
                    db.commit()

                    return {
                        "form_submission_id": form_submission_id,
                        "domain": domain,
                        "status": "failed",
                        "error": error_message,
                        "submission_details": submission_result,
                        "submission_time": datetime.now().isoformat(),
                        "success": False,
                    }

            except WebDriverException as e:
                # Update FormSubmission with WebDriver error
                form_submission.status = "failed"
                form_submission.task_status = "failed"
                form_submission.error_message = f"WebDriver error: {str(e)}"
                db.commit()

                return {
                    "form_submission_id": form_submission_id,
                    "domain": domain,
                    "status": "failed",
                    "error": f"WebDriver error: {str(e)}",
                    "submission_time": datetime.now().isoformat(),
                    "success": False,
                }

            finally:
                if driver:
                    driver.quit()

        finally:
            if db:
                db.close()

    except Exception as e:
        # Handle any other unexpected errors
        try:
            from contactform.insertion.models import FormSubmission
            from contactform.mission.crud import get_db

            db = get_db()
            try:
                form_submission = (
                    db.query(FormSubmission)
                    .filter(FormSubmission.id == form_submission_id)
                    .first()
                )

                if form_submission:
                    form_submission.status = "failed"
                    form_submission.task_status = "failed"
                    form_submission.error_message = f"Unexpected error: {str(e)}"
                    db.commit()
            finally:
                if db:
                    db.close()
        except:
            pass  # Ignore errors in error handling

        return {
            "form_submission_id": form_submission_id,
            "status": "failed",
            "error": f"Unexpected error: {str(e)}",
            "submission_time": datetime.now().isoformat(),
            "success": False,
        }


def get_task_status(task_id: str) -> dict[str, Any]:
    """
    Retrieves the status of a Huey task: pending, completed, or failed.

    Args:
        huey_instance (Huey): The active Huey instance.
        task_id (str): The Huey task ID to check.

    Returns:
        Dict[str, str]: A dictionary containing the task_id and its status.
                        Possible statuses are 'completed', 'pending', or 'failed'.
    """
    # # Get the Result handle for the given task ID.
    # result_handle: Result | None = huey.result(id=task_id, preserve=True)
    result_handle: Result | None = Result(huey=huey, task=Task(id=task_id))

    # # A revoked task is considered a form of failure.

    # if result_handle is None:
    #     return {"task_id": task_id, "status": "not_found"}
    if result_handle.is_revoked():
        return {"task_id": task_id, "status": "failed"}

    try:
        # Use get(blocking=False) to check for a result without waiting.
        # This is the key to differentiating states.
        result = result_handle.get(blocking=False, preserve=True)

        if result is not None:
            # If get() returns a value, the task is complete.
            return {"task_id": task_id, "status": "completed"}
        else:
            # If get() returns None, the task is not yet finished.
            # Huey's API doesn't distinguish between "pending" (in queue)
            # and "in progress" (being executed), so we group them.
            return {"task_id": task_id, "status": "pending"}

    except Exception:
        # If result_handle.get() raises an exception, the task itself has failed.
        return {"task_id": task_id, "status": "failed"}
