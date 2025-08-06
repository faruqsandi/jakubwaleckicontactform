import csv
import io
from urllib.parse import urlparse
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from contactform.mission.crud import get_db
from contactform.detection.crud import ContactFormDetectionCRUD

config_bp = Blueprint("config", __name__, url_prefix="/config")


def extract_fqdn(domain: str) -> tuple[str, bool]:
    """
    Extract FQDN from domain name by removing HTTP prefixes and directories.

    Args:
        domain: Domain name that may include HTTP prefix and directories

    Returns:
        Tuple of (Clean FQDN, is_valid_domain)
    """
    domain = domain.strip()

    # If no protocol, add one for urlparse to work properly
    if not domain.startswith(("http://", "https://")):
        domain = "http://" + domain

    parsed = urlparse(domain)
    hostname = parsed.hostname

    if not hostname:
        return "", False

    # Validate domain has extension (at least one dot with 2+ char extension)
    is_valid = "." in hostname and len(hostname.split(".")[-1]) >= 2

    return hostname, is_valid


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

    try:
        # Read the CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"))
        csv_reader = csv.reader(stream)

        uploaded_domains = []
        invalid_domains = []
        for row in csv_reader:
            if row and len(row) > 0:  # Skip empty rows
                domain = row[0]  # Take the first column
                if domain.strip():  # Skip empty values
                    fqdn, is_valid = extract_fqdn(domain)
                    if fqdn:  # Only add non-empty FQDNs
                        if is_valid:
                            uploaded_domains.append(fqdn)
                        else:
                            invalid_domains.append(fqdn)

        # Remove duplicates while preserving order
        unique_domains = []
        seen = set()
        for domain in uploaded_domains:
            if domain not in seen:
                unique_domains.append(domain)
                seen.add(domain)

        uploaded_domains = unique_domains

        # Sort domains alphabetically
        uploaded_domains.sort()
        invalid_domains.sort()

        # Store invalid domains for display
        session["invalid_domains"] = invalid_domains

        if not uploaded_domains and not invalid_domains:
            flash("No domains found in the CSV file!", "error")
            return redirect(url_for("config.config_page"))

        session["uploaded_domains"] = uploaded_domains
        session["csv_filename"] = file.filename

        # Create message about results
        messages = []
        if uploaded_domains:
            messages.append(f"{len(uploaded_domains)} valid domains")
        if invalid_domains:
            messages.append(f"{len(invalid_domains)} invalid domains (will be ignored)")

        flash(f"CSV uploaded successfully! Found {', '.join(messages)}.", "success")

        if invalid_domains:
            flash(
                f"Invalid domains found: {', '.join(invalid_domains[:5])}{'...' if len(invalid_domains) > 5 else ''}",
                "warning",
            )

        session["csv_uploaded"] = True
        return redirect(url_for("config.config_page"))

    except Exception as e:
        flash(f"Error processing CSV file: {str(e)}", "error")
        return redirect(url_for("config.config_page"))


@config_bp.route("/continue_to_forms")
def continue_to_forms():
    """Process uploaded domains and create ContactFormDetection instances if needed"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))

    if not session.get("csv_uploaded") or not session.get("uploaded_domains"):
        flash("Please upload CSV file first.", "warning")
        return redirect(url_for("config.config_page"))

    uploaded_domains = session.get("uploaded_domains", [])
    invalid_domains = session.get("invalid_domains", [])

    try:
        db = get_db()
        try:
            new_domains_count = 0
            existing_domains_count = 0

            # Only process valid domains
            for domain in uploaded_domains:
                # Check if domain already exists in ContactFormDetection
                existing_detections = ContactFormDetectionCRUD.get_by_domain(db, domain)

                if not existing_detections:
                    # Create new ContactFormDetection instance
                    ContactFormDetectionCRUD.create(
                        db=db,
                        domain_name=domain,
                        form_url=f"https://{domain}",  # Default form URL
                        contact_form_present=False,
                        website_antibot_detection=False,
                        form_antibot_detection=False,
                        detection_status="pending",
                    )
                    new_domains_count += 1
                else:
                    existing_domains_count += 1

            message_parts = []
            if new_domains_count > 0:
                message_parts.append(
                    f"{new_domains_count} new domains added for detection"
                )
            if existing_domains_count > 0:
                message_parts.append(
                    f"{existing_domains_count} domains already existed"
                )

            if message_parts:
                flash(f"Processing complete: {', '.join(message_parts)}.", "success")
            else:
                flash("No valid domains were processed.", "info")

            # Inform about invalid domains being skipped
            if invalid_domains:
                flash(f"{len(invalid_domains)} invalid domains were skipped.", "info")

        finally:
            db.close()

    except Exception as e:
        flash(f"Error processing domains: {str(e)}", "error")
        return redirect(url_for("config.config_page"))

    # Redirect to missing forms page
    return redirect(url_for("forms.missing_forms"))


@config_bp.route("/clear_csv")
def clear_csv():
    """Clear uploaded CSV data"""
    session.pop("uploaded_domains", None)
    session.pop("invalid_domains", None)
    session.pop("csv_filename", None)
    session.pop("csv_uploaded", None)
    flash("CSV data cleared.", "info")
    return redirect(url_for("config.config_page"))
