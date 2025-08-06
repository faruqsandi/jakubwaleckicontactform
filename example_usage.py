"""
Example usage of the search_domain_form function.

This script demonstrates how to use the selenium-based form detection
to search for contact forms on a domain and update the database.
"""

from contactform.detection.selenium_handler import (
    search_domain_form,
    batch_search_domain_forms,
)
from contactform.detection.models import ContactFormDetection
from contactform.mission.crud import get_db
import logging

# Set up logging to see what happens
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_single_domain() -> ContactFormDetection | None:
    """Example of searching for forms on a single domain."""
    domain = "50safe.pl"

    try:
        # Search for contact form on the domain
        # This will automatically create or update a ContactFormDetection record
        detection_result = search_domain_form(domain)

        print(f"Detection completed for {domain}")
        print(f"Form found: {detection_result.contact_form_present}")
        print(f"Form URL: {detection_result.form_url}")
        print(f"Form fields: {detection_result.form_fields}")
        print(f"Anti-bot protection: {detection_result.form_antibot_detection}")
        print(f"Protection type: {detection_result.form_antibot_type}")

        return detection_result

    except Exception as e:
        logger.error(f"Failed to detect forms for {domain}: {str(e)}")
        return None


def example_multiple_domains() -> list[ContactFormDetection]:
    """Example of searching for forms on multiple domains."""
    domains = ["50safe.pl", "example.com", "google.com"]

    try:
        # Search for contact forms on multiple domains
        detection_results = batch_search_domain_forms(domains)

        print(f"Processed {len(detection_results)} domains")

        for result in detection_results:
            print(f"\nDomain: {result.domain_name}")
            print(f"Form found: {result.contact_form_present}")
            print(f"Form URL: {result.form_url}")
            print(f"Status: {result.detection_status}")

        return detection_results

    except Exception as e:
        logger.error(f"Failed to process domains: {str(e)}")
        return []


def example_with_existing_db_session() -> ContactFormDetection | None:
    """Example using an existing database session."""
    domain = "50safe.pl"

    # Get database session
    db = get_db()

    try:
        # Search for contact form using existing session
        detection_result = search_domain_form(domain, db)

        print(f"Detection completed for {domain}")
        print(f"Form found: {detection_result.contact_form_present}")

        return detection_result

    except Exception as e:
        logger.error(f"Failed to detect forms for {domain}: {str(e)}")
        return None
    finally:
        # Make sure to close the session
        db.close()


if __name__ == "__main__":
    print("=== Single Domain Example ===")
    example_single_domain()

    print("\n=== Multiple Domains Example ===")
    example_multiple_domains()

    print("\n=== Example with Existing DB Session ===")
    example_with_existing_db_session()
