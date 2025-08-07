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
