from flask import Blueprint, render_template, request, redirect, url_for, session, flash

submission_bp = Blueprint("submission", __name__, url_prefix="/submission")

# Sample data
sample_fields = [
    {"name": "name", "type": "text", "required": True},
    {"name": "email", "type": "email", "required": True},
    {"name": "phone", "type": "tel", "required": False},
    {"name": "message", "type": "textarea", "required": True},
    {"name": "company", "type": "text", "required": False},
]
sample_domains = ["example.com", "testsite.org", "demo.net", "sample.io"]


@submission_bp.route("/config")
def submission_config():
    """Fourth page: Submission config page"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))

    return render_template(
        "submission_config.html",
        fields=sample_fields,
        mission_name=session.get("current_mission_name"),
    )


@submission_bp.route("/save_config", methods=["POST"])
def save_submission_config():
    """Save submission configuration"""
    # TODO: Save field values to session or database
    for field in sample_fields:
        field_value = request.form.get(field["name"])
        session[f"field_{field['name']}"] = field_value

    flash("Submission configuration saved!", "success")
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
