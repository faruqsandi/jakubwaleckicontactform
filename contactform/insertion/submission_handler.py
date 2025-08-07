"""
Form submission handler.

This module provides functionality to submit forms on websites using Selenium
and update the FormSubmission database with the results.
"""

from typing import Any
from datetime import datetime
import logging

from selenium.common.exceptions import WebDriverException
from sqlalchemy.orm import Session

from contactform.insertion.models import FormSubmission
from contactform.detection.crud import ContactFormDetectionCRUD
from contactform.mission.crud import get_db
from contactform.utils.webdriver import setup_webdriver
from contactform.insertion.form_check import (
    fill_and_submit_form,
    verify_form_elements,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def submit_contact_form(
    form_submission_id: int, db_session: Session | None = None
) -> dict[str, Any]:
    """
    Submit a contact form using selenium handler.

    This function will:
    1. Get FormSubmission record and associated detection data
    2. Set up WebDriver and navigate to form URL
    3. Verify form elements are present
    4. Fill and submit the form
    5. Update FormSubmission record with results

    Args:
        form_submission_id: FormSubmission ID to process
        db_session: Optional database session. If not provided, will create a new one.

    Returns:
        dict: Submission result with status and data

    Raises:
        ValueError: If form submission record is not found
        WebDriverException: If selenium operations fail
        Exception: For other unexpected errors
    """
    # Set up database session
    db_provided = db_session is not None
    if not db_provided:
        db_session = get_db()

    driver = None

    try:
        logger.info(f"Starting form submission for ID: {form_submission_id}")

        # Get FormSubmission record
        form_submission = (
            db_session.query(FormSubmission)
            .filter(FormSubmission.id == form_submission_id)
            .first()
        )

        if not form_submission:
            raise ValueError(f"FormSubmission record not found for ID: {form_submission_id}")

        domain = form_submission.domain

        # Get ContactFormDetection for this domain
        detections = ContactFormDetectionCRUD.get_by_domain(db_session, domain)
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
            db_session.commit()

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
            db_session.commit()

            return {
                "form_submission_id": form_submission_id,
                "domain": domain,
                "status": "failed",
                "error": "No form URL found in detection",
                "submission_time": datetime.now().isoformat(),
                "success": False,
            }

        # Set up WebDriver
        try:
            driver = setup_webdriver(headless=False)

            # Navigate to form URL
            logger.info(f"Navigating to form URL: {detection.form_url}")
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
            logger.info("Verifying form elements")
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
                db_session.commit()

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
            logger.info("Filling and submitting form")
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
                db_session.commit()

                logger.info(f"Form submission successful for ID: {form_submission_id}")
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
                db_session.commit()

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
            db_session.commit()

            logger.error(f"WebDriver error for submission ID {form_submission_id}: {str(e)}")
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

    except Exception as e:
        # Handle any other unexpected errors
        logger.error(f"Unexpected error for submission ID {form_submission_id}: {str(e)}")

        try:
            form_submission = (
                db_session.query(FormSubmission)
                .filter(FormSubmission.id == form_submission_id)
                .first()
            )

            if form_submission:
                form_submission.status = "failed"
                form_submission.task_status = "failed"
                form_submission.error_message = f"Unexpected error: {str(e)}"
                db_session.commit()
        except:
            pass  # Ignore errors in error handling

        return {
            "form_submission_id": form_submission_id,
            "status": "failed",
            "error": f"Unexpected error: {str(e)}",
            "submission_time": datetime.now().isoformat(),
            "success": False,
        }

    finally:
        # Close database session if we created it
        if not db_provided and db_session:
            db_session.close()
