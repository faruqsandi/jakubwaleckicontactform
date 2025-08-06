from flask import Blueprint, render_template, request, redirect, url_for, session, flash

forms_bp = Blueprint('forms', __name__, url_prefix='/forms')

# Sample data
sample_missing_forms = ["missingform1.com", "noform.org"]
sample_domains = ["example.com", "testsite.org", "demo.net", "sample.io"]

@forms_bp.route("/missing")
def missing_forms():
    """Third page: Missing forms page"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))

    if not session.get("csv_uploaded"):
        flash("Please upload CSV file first.", "warning")
        return redirect(url_for("config.config_page"))

    return render_template(
        "missing_forms.html",
        missing_forms=sample_missing_forms,
        mission_name=session.get("current_mission_name"),
    )

@forms_bp.route("/get_forms", methods=["POST"])
def get_forms():
    """Get form information for missing domains"""
    # TODO: Implement form detection logic
    flash("Form information retrieved successfully!", "success")
    session["forms_retrieved"] = True
    return redirect(url_for("forms.missing_forms"))
