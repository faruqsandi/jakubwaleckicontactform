"""
Huey blueprint for testing background tasks.
This is a hidden route not linked from anywhere for testing purposes.
"""
from datetime import datetime
import json
from huey.storage import SqliteStorage
from huey_config import huey, dummy_task, background_form_detection
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import sys
import os

# Add the parent directory to the path so we can import huey_config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


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

        # Get task keys (this is a simplified approach)
        # Note: Huey's API doesn't expose task history directly,
        # so we'll work with what's available
        tasks = []

        # Try to get completed tasks from storage
        # This is a workaround since Huey doesn't have a direct API for task history
        try:
            # Get all task keys from storage
            task_keys = []
            if hasattr(storage, '_conn'):
                cursor = storage._conn.cursor()
                cursor.execute("""
                    SELECT key, value FROM kv 
                    WHERE key LIKE 'huey.result.%' 
                    ORDER BY key DESC 
                    LIMIT ?
                """, (limit,))

                rows = cursor.fetchall()

                for row in rows:
                    key, result_data = row
                    try:
                        # Try to decode the result
                        if result_data:
                            # Extract task ID from key
                            task_id = key.replace('huey.result.', '')
                            task_info = {
                                'task_id': task_id,
                                'timestamp': datetime.now().isoformat(),  # We don't have timestamp in this table
                                'status': 'completed',
                                'result': 'Task completed (result data stored)'
                            }
                            tasks.append(task_info)
                    except Exception as e:
                        # If we can't decode, just show basic info
                        task_info = {
                            'task_id': key.replace('huey.result.', ''),
                            'timestamp': datetime.now().isoformat(),
                            'status': 'completed',
                            'result': f'Could not decode result: {str(e)[:50]}'
                        }
                        tasks.append(task_info)

                # Also check the task table for more detailed info
                try:
                    cursor.execute("""
                        SELECT id, task_name, executed_time, revoked_time 
                        FROM task 
                        ORDER BY executed_time DESC 
                        LIMIT ?
                    """, (limit,))

                    task_rows = cursor.fetchall()
                    for task_row in task_rows:
                        task_id, task_name, executed_time, revoked_time = task_row
                        status = 'completed' if executed_time else 'pending'
                        if revoked_time:
                            status = 'revoked'

                        task_info = {
                            'task_id': task_id,
                            'timestamp': datetime.fromtimestamp(executed_time).isoformat() if executed_time else None,
                            'status': status,
                            'result': f'Task: {task_name}' if task_name else 'Unknown task'
                        }
                        # Only add if not already present
                        if not any(t['task_id'] == task_id for t in tasks):
                            tasks.append(task_info)

                except Exception:
                    pass  # Ignore errors from task table query

        except Exception as e:
            # Fallback: show a message about storage access
            tasks.append({
                'task_id': 'storage_error',
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'result': f'Could not access task storage: {str(e)}'
            })

        return tasks

    except Exception as e:
        return [{
            'task_id': 'error',
            'timestamp': datetime.now().isoformat(),
            'status': 'error',
            'result': f'Error retrieving tasks: {str(e)}'
        }]


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

        flash(f"Dummy task '{task_name}' has been queued! Task ID: {result.id}", "success")

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

        flash(f"Form detection task for '{domain}' has been queued! Task ID: {result.id}", "success")

    except Exception as e:
        flash(f"Error queuing form detection task: {str(e)}", "error")

    return redirect(url_for("huey.huey_test_page"))


@huey_bp.route("/task_status/<task_id>")
def task_status(task_id):
    """
    Get the status of a specific task.
    """
    try:
        # Try to get task result
        # Note: This is a simplified approach since Huey's task tracking is limited
        return jsonify({
            "task_id": task_id,
            "status": "Task status checking not fully implemented",
            "message": "Check the recent tasks list for completed tasks"
        })

    except Exception as e:
        return jsonify({
            "task_id": task_id,
            "status": "error",
            "error": str(e)
        }), 500


@huey_bp.route("/clear_completed_tasks", methods=["POST"])
def clear_completed_tasks():
    """
    Clear completed tasks from storage (if possible).
    """
    try:
        # This would depend on Huey's storage implementation
        flash("Task clearing functionality would need to be implemented based on storage backend", "info")

    except Exception as e:
        flash(f"Error clearing tasks: {str(e)}", "error")

    return redirect(url_for("huey.huey_test_page"))
