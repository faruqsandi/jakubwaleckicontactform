from huey.api import Result, Task
from huey_config import huey
from huey_config import get_task_status
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from contactform.mission.crud import get_db, MissionCRUD
from contactform.detection.crud import ContactFormDetectionCRUD
from typing import List

forms_bp = Blueprint("forms", __name__, url_prefix="/forms")


def _check_mission_submitted():
    """
    Check if current mission is already submitted and redirect if needed.
    Returns redirect response if mission is submitted, None otherwise.
    """
    if "current_mission_id" not in session:
        return None

    db = get_db()
    try:
        mission_id = session["current_mission_id"]
        mission = MissionCRUD.get_mission(mission_id, db)

        if mission and mission.submitted_date is not None:
            flash(
                "This mission has already been submitted. Redirecting to submission process.",
                "info",
            )
            return redirect(url_for("submission.submission_process"))
    finally:
        db.close()

    return None


@forms_bp.route("/missing")
def missing_forms():
    """Third page: Missing forms page"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))

    # Check if mission is already submitted
    submitted_redirect = _check_mission_submitted()
    if submitted_redirect:
        return submitted_redirect

    if not session.get("csv_uploaded"):
        flash("Please upload CSV file first.", "warning")
        return redirect(url_for("config.config_page"))

    # Don't load table data initially - it will be loaded via HTMX
    return render_template(
        "missing_forms.html",
        mission_name=session.get("current_mission_name"),
    )


@forms_bp.route("/table_content")
def table_content():
    """Return table content for the missing forms page (for HTMX)"""
    if "current_mission_id" not in session:
        return '<tr><td colspan="8" class="text-center text-danger">Please select a mission first.</td></tr>'

    if not session.get("csv_uploaded"):
        return '<tr><td colspan="8" class="text-center text-warning">Please upload CSV file first.</td></tr>'

    # Get domains from uploaded CSV that are in ContactFormDetection with all statuses
    uploaded_domains = session.get("uploaded_domains", [])
    missing_forms_data = []

    if uploaded_domains:
        try:
            db = get_db()
            try:
                for domain in uploaded_domains:
                    # Get ContactFormDetection records for this domain
                    detections = ContactFormDetectionCRUD.get_by_domain(db, domain)

                    if detections:
                        # Add the latest detection record for this domain
                        latest_detection = detections[
                            0
                        ]  # Assuming they are ordered by date
                        task_status = None
                        if latest_detection.task_id:
                            task_status = get_task_status(latest_detection.task_id)[
                                "status"
                            ]

                        missing_forms_data.append(
                            {
                                "domain": domain,
                                "status": latest_detection.detection_status,
                                "form_present": latest_detection.contact_form_present,
                                "form_url": latest_detection.form_url,
                                "last_updated": latest_detection.last_updated,
                                "task_id": latest_detection.task_id,
                                "task_status": task_status,
                            }
                        )
                    else:
                        # No detection record found, this shouldn't happen if config worked properly
                        missing_forms_data.append(
                            {
                                "domain": domain,
                                "status": "not_found",
                                "form_present": False,
                                "form_url": None,
                                "last_updated": None,
                                "task_id": None,
                                "task_status": None,
                            }
                        )

                # Sort the data so completed records appear at the bottom
                missing_forms_data.sort(
                    key=lambda x: (x["status"] == "completed", x["domain"])
                )

            finally:
                db.close()

        except Exception as e:
            return f'<tr><td colspan="8" class="text-center text-danger">Error retrieving form data: {str(e)}</td></tr>'

    has_pending_tasks = any(
        detection["task_status"] == "pending" for detection in missing_forms_data
    )
    has_no_form_present = any(
        not detection["form_present"] for detection in missing_forms_data
    )
    # Return just the table rows
    return render_template("table_content.html", missing_forms=missing_forms_data, has_pending_tasks=has_pending_tasks, has_no_form_present=has_no_form_present)


@forms_bp.route("/get_forms", methods=["POST"])
def get_forms():
    """Trigger form detection for all domains by calling search_domain_form"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))

    # Get domains that need form detection
    uploaded_domains = session.get("uploaded_domains", [])

    if not uploaded_domains:
        flash("No domains to process.", "warning")
        return redirect(url_for("forms.missing_forms"))

    # Call search_domain_form with all domains
    return search_domain_form_bulk(uploaded_domains)


@forms_bp.route("/search_domain_form", methods=["POST"])
def search_domain_form():
    """Search form information for a specific domain using background task"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))

    domain = request.form.get("domain")
    if not domain:
        flash("No domain specified for form search.", "error")
        return redirect(url_for("forms.missing_forms"))

    return search_domain_form_bulk([domain])


def search_domain_form_bulk(domains: list[str]):
    """Search form information for multiple domains using background tasks"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))

    if not domains:
        flash("No domains specified for form search.", "error")
        return redirect(url_for("forms.missing_forms"))

    try:
        from huey_config import background_form_detection_task

        db = get_db()
        try:
            started_count = 0
            for domain in domains:
                # Get the detection record for this domain
                detections = ContactFormDetectionCRUD.get_by_domain(db, domain)
                if not detections:
                    flash(
                        f"No detection record found for domain '{domain}'.", "warning"
                    )
                    continue

                detection = detections[0]  # Get the first detection record

                # Skip if already pending to avoid duplicate tasks
                if detection.detection_status == "pending" and detection.task_id:
                    continue

                # Start background task for form detection
                task_result = background_form_detection_task(domain)
                task_id = (
                    str(task_result.id)
                    if hasattr(task_result, "id")
                    else str(task_result)
                )

                # Update the detection record with the task ID and set status to pending
                ContactFormDetectionCRUD.update(
                    db=db,
                    detection_id=detection.id,
                    detection_status="pending",
                    task_id=task_id,
                )
                started_count += 1

            if started_count > 0:
                if len(domains) == 1:
                    flash(
                        f"Form detection started for domain '{domains[0]}'. Task started.",
                        "info",
                    )
                else:
                    flash(
                        f"Form detection started for {started_count} domains out of {len(domains)} total domains.",
                        "info",
                    )
            else:
                if len(domains) == 1:
                    flash(
                        f"Form detection already in progress for domain '{domains[0]}'.",
                        "info",
                    )
                else:
                    flash(
                        "All domains are already being processed or have no detection records.",
                        "info",
                    )

        finally:
            db.close()

    except Exception as e:
        if len(domains) == 1:
            flash(
                f"Error starting form detection for '{domains[0]}': {str(e)}", "error"
            )
        else:
            flash(f"Error starting form detection for domains: {str(e)}", "error")

    return redirect(url_for("forms.missing_forms"))


@forms_bp.route("/remove_domain", methods=["POST"])
def remove_domain():
    """Remove a domain from the current mission's uploaded domains"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))

    domain_to_remove = request.form.get("domain")
    if not domain_to_remove:
        flash("No domain specified for removal.", "error")
        return redirect(url_for("forms.missing_forms"))

    # Get current uploaded domains from session
    uploaded_domains = session.get("uploaded_domains", [])

    if domain_to_remove in uploaded_domains:
        # Remove the domain from the session list
        uploaded_domains.remove(domain_to_remove)
        session["uploaded_domains"] = uploaded_domains
        flash(
            f"Domain '{domain_to_remove}' has been removed from this mission.",
            "success",
        )
    else:
        flash(
            f"Domain '{domain_to_remove}' was not found in the current mission.",
            "warning",
        )

    return redirect(url_for("forms.missing_forms"))


@forms_bp.route("/cancel_all_tasks", methods=["POST"])
def cancel_all_tasks():
    """Cancel all Huey tasks and clear task IDs from all domains in session"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))

    try:
        db = get_db()
        try:
            canceled_count = 0
            cleared_count = 0

            # Get all domains from session
            uploaded_domains = session.get("uploaded_domains", [])

            if uploaded_domains:
                for domain in uploaded_domains:
                    # Get detection records for this domain
                    detections = ContactFormDetectionCRUD.get_by_domain(db, domain)

                    for detection in detections:
                        # If there's a task_id, try to cancel it
                        if detection.task_id:
                            try:
                                # Create Result object and revoke the task
                                result = Result(
                                    huey=huey, task=Task(id=detection.task_id)
                                )
                                result.revoke()
                                canceled_count += 1
                            except Exception as e:
                                # Log error but continue with other tasks
                                print(
                                    f"Error canceling task {detection.task_id}: {str(e)}"
                                )

                        # Clear task_id and reset status if it was pending
                        if detection.detection_status == "pending" or detection.task_id:
                            ContactFormDetectionCRUD.update(
                                db=db,
                                detection_id=detection.id,
                                detection_status="not_found",  # Reset to initial state
                                task_id=None,  # Clear task_id
                            )
                            cleared_count += 1

            if canceled_count > 0 or cleared_count > 0:
                flash(
                    f"Successfully canceled {canceled_count} tasks and cleared {cleared_count} detection records.",
                    "success",
                )
            else:
                flash("No active tasks found to cancel.", "info")

        finally:
            db.close()

    except Exception as e:
        flash(f"Error canceling tasks: {str(e)}", "error")

    return redirect(url_for("forms.missing_forms"))
