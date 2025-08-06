from flask import Blueprint, render_template, request, redirect, url_for, session, flash

config_bp = Blueprint("config", __name__, url_prefix="/config")


@config_bp.route("/")
def config_page():
    """Second page: Config page with CSV upload"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))
    return render_template(
        "config.html", mission_name=session.get("current_mission_name")
    )


@config_bp.route("/upload_csv", methods=["POST"])
def upload_csv():
    """Handle CSV upload"""
    if "csv_file" not in request.files:
        flash("No file selected!", "error")
        return redirect(url_for("config.config_page"))

    file = request.files["csv_file"]
    if file.filename == "":
        flash("No file selected!", "error")
        return redirect(url_for("config.config_page"))

    # TODO: Process CSV file and extract URLs
    # For now, simulate processing with sample domains
    uploaded_domains = [
        "example.com",
        "testsite.org",
        "demo.net",
        "sample.io",
        "contact-form.com",
        "business-site.net",
    ]

    session["uploaded_domains"] = uploaded_domains
    session["csv_filename"] = file.filename
    flash(
        f"CSV uploaded successfully! Found {len(uploaded_domains)} domains.", "success"
    )
    session["csv_uploaded"] = True
    return redirect(url_for("config.config_page"))


@config_bp.route("/clear_csv")
def clear_csv():
    """Clear uploaded CSV data"""
    session.pop("uploaded_domains", None)
    session.pop("csv_filename", None)
    session.pop("csv_uploaded", None)
    flash("CSV data cleared.", "info")
    return redirect(url_for("config.config_page"))
