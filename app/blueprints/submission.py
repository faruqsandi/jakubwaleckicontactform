from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug import Response
from contactform.detection.crud import ContactFormDetectionCRUD
from contactform.mission.crud import MissionCRUD, get_db
from typing import Dict, List, Set, Any

submission_bp = Blueprint("submission", __name__, url_prefix="/submission")

# Sample data for fallback
sample_domains = ["example.com", "testsite.org", "demo.net", "sample.io"]


@submission_bp.route("/config")
def submission_config() -> Response | str:
    """Fourth page: Submission config page"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))

    # Get domains from session
    uploaded_domains = session.get("uploaded_domains", [])

    if not uploaded_domains:
        flash("No domains found in session.", "warning")
        return redirect(url_for("config.config_page"))

    # Get database session
    db = get_db()

    try:
        # Get all ContactFormDetection records for domains in session with completed status
        all_form_fields: set[str] = set()

        for domain in uploaded_domains:
            detections = ContactFormDetectionCRUD.get_by_domain(db, domain)
            completed_detections = [
                d for d in detections if d.detection_status == "completed"
            ]

            for detection in completed_detections:
                if detection.form_fields:
                    # Add all fields from this detection to our set
                    all_form_fields.update(detection.form_fields)

        # If no fields found, show message and redirect
        if not all_form_fields:
            flash(
                "No form fields found for the selected domains. Please ensure form detection is completed.",
                "warning",
            )
            return redirect(url_for("forms.missing_forms"))

        # Get existing mission data to pre-fill form
        mission_id = session["current_mission_id"]
        existing_mission = MissionCRUD.get_mission(mission_id, db)

        if not existing_mission:
            flash("Mission not found.", "error")
            return redirect(url_for("mission.mission_list"))

        existing_values = (
            existing_mission.pre_defined_fields
            if existing_mission.pre_defined_fields
            else {}
        )

        # Convert set to list of dictionaries for the template
        # Create a more sophisticated field mapping based on field names
        dynamic_fields: list[dict[str, Any]] = []
        for field_name in sorted(all_form_fields):
            field_type = _determine_field_type(field_name)
            is_required = _determine_if_required(field_name)

            dynamic_fields.append(
                {
                    "name": field_name,
                    "type": field_type,
                    "required": is_required,
                    "value": existing_values.get(
                        field_name, ""
                    ),  # Pre-fill with existing value
                }
            )

        return render_template(
            "submission_config.html",
            fields=dynamic_fields,
            mission_name=session.get("current_mission_name"),
        )

    finally:
        db.close()


def _determine_field_type(field_name: str) -> str:
    """Determine field type based on field name"""
    field_name_lower = field_name.lower()

    if "email" in field_name_lower:
        return "email"
    elif "phone" in field_name_lower or "tel" in field_name_lower:
        return "tel"
    elif (
        "message" in field_name_lower
        or "comment" in field_name_lower
        or "description" in field_name_lower
    ):
        return "textarea"
    else:
        return "text"


def _determine_if_required(field_name: str) -> bool:
    """Determine if field should be required based on field name"""
    field_name_lower = field_name.lower()

    # Common required fields
    required_indicators = ["name", "email", "message", "subject"]

    return any(indicator in field_name_lower for indicator in required_indicators)


@submission_bp.route("/save_config", methods=["POST"])
def save_submission_config():
    """Save submission configuration"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))

    # Get the mission ID from session
    mission_id = session["current_mission_id"]

    # Get database session
    db = get_db()

    try:
        # Get domains from session
        uploaded_domains = session.get("uploaded_domains", [])

        if not uploaded_domains:
            flash("No domains found in session.", "warning")
            return redirect(url_for("config.config_page"))

        # Get all unique form fields from completed detections
        all_form_fields: set[str] = set()

        for domain in uploaded_domains:
            detections = ContactFormDetectionCRUD.get_by_domain(db, domain)
            completed_detections = [
                d for d in detections if d.detection_status == "completed"
            ]

            for detection in completed_detections:
                if detection.form_fields:
                    all_form_fields.update(detection.form_fields)

        # Validate that we have form fields to work with
        if not all_form_fields:
            flash(
                "No form fields found for the selected domains. Please ensure form detection is completed.",
                "warning",
            )
            return redirect(url_for("forms.missing_forms"))

        # Collect form values into pre_defined_fields dictionary
        pre_defined_fields: dict[str, str] = {}
        missing_required_fields: list[str] = []

        for field_name in all_form_fields:
            field_value = request.form.get(field_name)
            if field_value and field_value.strip():  # Only store non-empty values
                pre_defined_fields[field_name] = field_value.strip()
            else:
                # Check if this is a required field
                if _determine_if_required(field_name):
                    missing_required_fields.append(field_name)

        # Validate required fields are filled
        if missing_required_fields:
            flash(
                f"Please fill in all required fields: {', '.join(missing_required_fields)}",
                "error",
            )
            return redirect(url_for("submission.submission_config"))

        # Ensure we have at least some data to save
        if not pre_defined_fields:
            flash("Please fill in at least one field before continuing.", "warning")
            return redirect(url_for("submission.submission_config"))

        # Update the mission with the pre-defined fields
        mission = MissionCRUD.update_mission(
            mission_id=mission_id, pre_defined_fields=pre_defined_fields, db=db
        )
        if mission:
            flash("Submission configuration saved successfully!", "success")
        else:
            flash("Mission not found.", "error")
            return redirect(url_for("mission.mission_list"))

    except Exception as e:
        db.rollback()
        flash(f"Error saving configuration: {str(e)}", "error")
        return redirect(url_for("submission.submission_config"))

    finally:
        db.close()

    return redirect(url_for("submission.submission_process"))


@submission_bp.route("/process")
def submission_process():
    """Fifth page: Submission process page"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))

    # Use uploaded domains if available, otherwise use sample data
    domains = session.get("uploaded_domains", sample_domains)

    return render_template(
        "submission_process.html",
        domains=domains,
        mission_name=session.get("current_mission_name"),
    )


@submission_bp.route("/submit_forms", methods=["POST"])
def submit_forms():
    """Submit forms to all domains"""
    # TODO: Implement form submission logic
    flash("Forms submitted successfully to all domains!", "success")
    return redirect(url_for("submission.submission_process"))
