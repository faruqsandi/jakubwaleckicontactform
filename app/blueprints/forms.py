from contactform.detection.selenium_handler import (
    search_domain_form as helper_search_domain_form,
)
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from contactform.mission.crud import get_db
from contactform.detection.crud import ContactFormDetectionCRUD

forms_bp = Blueprint("forms", __name__, url_prefix="/forms")


@forms_bp.route("/missing")
def missing_forms():
    """Third page: Missing forms page"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))

    if not session.get("csv_uploaded"):
        flash("Please upload CSV file first.", "warning")
        return redirect(url_for("config.config_page"))

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
                        missing_forms_data.append(
                            {
                                "domain": domain,
                                "status": latest_detection.detection_status,
                                "form_present": latest_detection.contact_form_present,
                                "form_url": latest_detection.form_url,
                                "last_updated": latest_detection.last_updated,
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
                            }
                        )

                # Sort the data so completed records appear at the bottom
                missing_forms_data.sort(
                    key=lambda x: (x["status"] == "completed", x["domain"])
                )

            finally:
                db.close()

        except Exception as e:
            flash(f"Error retrieving form data: {str(e)}", "error")
            missing_forms_data = []

    return render_template(
        "missing_forms.html",
        missing_forms=missing_forms_data,
        mission_name=session.get("current_mission_name"),
    )


@forms_bp.route("/get_forms", methods=["POST"])
def get_forms():
    """Trigger form detection for pending domains"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))

    # Get domains that need form detection
    uploaded_domains = session.get("uploaded_domains", [])

    if not uploaded_domains:
        flash("No domains to process.", "warning")
        return redirect(url_for("forms.missing_forms"))

    try:
        db = get_db()
        try:
            updated_count = 0
            for domain in uploaded_domains:
                detections = ContactFormDetectionCRUD.get_by_domain(db, domain)

                # For now, just update status from pending to completed
                # In the future, this would trigger actual form detection logic
                for detection in detections:
                    if detection.detection_status == "pending":
                        ContactFormDetectionCRUD.update(
                            db=db,
                            detection_id=detection.id,
                            detection_status="completed",
                            contact_form_present=True,  # Simulated detection
                            form_url=f"https://{domain}/contact",  # Default form URL
                        )
                        updated_count += 1

            if updated_count > 0:
                flash(
                    f"Form detection completed for {updated_count} domains!", "success"
                )
            else:
                flash("No pending domains found to process.", "info")

        finally:
            db.close()

    except Exception as e:
        flash(f"Error during form detection: {str(e)}", "error")

    return redirect(url_for("forms.missing_forms"))


@forms_bp.route("/search_domain_form", methods=["POST"])
def search_domain_form():
    """Search form information for a specific domain"""
    if "current_mission_id" not in session:
        flash("Please select a mission first.", "warning")
        return redirect(url_for("mission.mission_list"))

    domain = request.form.get("domain")
    if not domain:
        flash("No domain specified for form search.", "error")
        return redirect(url_for("forms.missing_forms"))

    try:
        db = get_db()
        try:
            detections = helper_search_domain_form(domain, db)
            # raise Exception(
            #     "Simulated error for testing"
            # )  # Simulated error for testing
            if detections:
                flash(f"Form detection completed for domain '{domain}'!", "success")
            else:
                flash(f"No detection record found for domain '{domain}'.", "warning")

        finally:
            db.close()

    except Exception as e:
        flash(f"Error during form detection for '{domain}': {str(e)}", "error")

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
