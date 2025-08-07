"""
Huey configuration for background task processing.
"""

import os
from huey import SqliteHuey
from datetime import datetime

# Use SQLite database for Huey tasks
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
def background_form_detection(domain):
    """
    Background task for form detection.
    This could be used later for actual form detection work.

    Args:
        domain (str): Domain to detect forms for

    Returns:
        dict: Detection result
    """
    import time
    import random

    # Simulate form detection work
    time.sleep(random.randint(2, 8))

    result = {
        "domain": domain,
        "form_detected": random.choice([True, False]),
        "form_url": f"https://{domain}/contact"
        if random.choice([True, False])
        else None,
        "detection_time": datetime.now().isoformat(),
        "status": "completed",
    }

    return result
