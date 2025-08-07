"""
Huey blueprint for testing background tasks.
This is a hidden route not linked from anywhere for testing purposes.
"""

from datetime import datetime
import pickle
from huey_config import huey, dummy_task, background_form_detection
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify


huey_bp = Blueprint("huey", __name__, url_prefix="/huey")


def get_recent_tasks(limit=100):
    """
    Get recent Huey tasks from the SQLite storage.

    Args:
        limit (int): Maximum number of tasks to retrieve

    Returns:
        list: List of task information dictionaries
    """
    try:
        # Get the storage instance from huey
        storage = huey.storage
        tasks = []

        # Try to get task information from storage
        try:
            if hasattr(storage, "conn") and storage.conn:
                cursor = storage.conn.cursor()

                # Get pending tasks from task table
                cursor.execute(
                    """
                    SELECT id, queue, data, priority 
                    FROM task 
                    ORDER BY id DESC 
                    LIMIT ?
                """,
                    (limit // 2,),
                )

                pending_rows = cursor.fetchall()
                for row in pending_rows:
                    task_id, queue, data, priority = row
                    # Try to decode task data to get more info
                    try:
                        task_data = pickle.loads(data)
                        task_name = getattr(task_data, "name", "Unknown")
                        task_args = getattr(task_data, "args", ())
                        result_text = f"Pending task: {task_name}"
                        if task_args:
                            result_text += f" with args: {task_args}"
                    except:
                        result_text = f"Pending task (ID: {task_id})"

                    task_info = {
                        "task_id": str(task_id),
                        "timestamp": None,
                        "status": "pending",
                        "result": result_text,
                    }
                    tasks.append(task_info)

                # Get completed/result tasks from kv table
                cursor.execute(
                    """
                    SELECT queue, key, value 
                    FROM kv 
                    ORDER BY rowid DESC 
                    LIMIT ?
                """,
                    (limit // 2,),
                )

                kv_rows = cursor.fetchall()
                for row in kv_rows:
                    queue, key, value = row
                    try:
                        # Try to decode the result value
                        result_data = pickle.loads(value)
                        if isinstance(result_data, dict):
                            result_text = f"Result: {str(result_data)[:100]}"
                        else:
                            result_text = f"Result: {str(result_data)[:100]}"
                    except:
                        result_text = "Completed task (result stored)"

                    task_info = {
                        "task_id": key[:20] + "..." if len(key) > 20 else key,
                        "timestamp": datetime.now().isoformat(),  # We don't have actual timestamp
                        "status": "completed",
                        "result": result_text,
                    }
                    tasks.append(task_info)

        except Exception as e:
            # Fallback: show a message about storage access
            tasks.append(
                {
                    "task_id": "storage_error",
                    "timestamp": datetime.now().isoformat(),
                    "status": "error",
                    "result": f"Could not access task storage: {str(e)}",
                }
            )

        return tasks

    except Exception as e:
        return [
            {
                "task_id": "error",
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "result": f"Error retrieving tasks: {str(e)}",
            }
        ]


@huey_bp.route("/")
def huey_test_page():
    """
    Hidden Huey testing page.
    Shows recent tasks and provides buttons to trigger test tasks.
    """
    recent_tasks = get_recent_tasks(100)
    return render_template("huey_test.html", recent_tasks=recent_tasks)


@huey_bp.route("/trigger_dummy_task", methods=["POST"])
def trigger_dummy_task():
    """
    Trigger a dummy background task.
    """
    task_name = request.form.get("task_name", "Test Task")
    delay_seconds = int(request.form.get("delay_seconds", 5))

    try:
        # Enqueue the task
        result = dummy_task(task_name=task_name, delay_seconds=delay_seconds)
        flash(
            f"Dummy task '{task_name}' has been queued! Task ID: {result.id}", "success"
        )
    except Exception as e:
        flash(f"Error queuing task: {str(e)}", "error")

    return redirect(url_for("huey.huey_test_page"))


@huey_bp.route("/trigger_form_detection", methods=["POST"])
def trigger_form_detection():
    """
    Trigger a background form detection task.
    """
    domain = request.form.get("domain", "example.com")

    try:
        # Enqueue the task
        result = background_form_detection(domain=domain)
        flash(
            f"Form detection task for '{domain}' has been queued! Task ID: {result.id}",
            "success",
        )
    except Exception as e:
        flash(f"Error queuing form detection task: {str(e)}", "error")

    return redirect(url_for("huey.huey_test_page"))


@huey_bp.route("/task_status/<task_id>")
def task_status(task_id):
    """
    Get the status of a specific task.
    """
    try:
        return jsonify(
            {
                "task_id": task_id,
                "status": "Task status checking not fully implemented",
                "message": "Check the recent tasks list for completed tasks",
            }
        )
    except Exception as e:
        return jsonify({"task_id": task_id, "status": "error", "error": str(e)}), 500


@huey_bp.route("/clear_completed_tasks", methods=["POST"])
def clear_completed_tasks():
    """
    Clear completed tasks from storage (if possible).
    """
    try:
        flash(
            "Task clearing functionality would need to be implemented based on storage backend",
            "info",
        )
    except Exception as e:
        flash(f"Error clearing tasks: {str(e)}", "error")

    return redirect(url_for("huey.huey_test_page"))
