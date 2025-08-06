"""
Selenium-based form detection handler.

This module provides functionality to detect contact forms on websites using Selenium
and update the ContactFormDetection database with the results.
"""

from typing import Optional, Dict, Any, Union, List
from urllib.parse import urljoin, urlparse
import logging
from datetime import datetime, timezone

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
import chromedriver_autoinstaller  # type: ignore

from sqlalchemy.orm import Session
from contactform.mission.crud import get_db
from contactform.detection.crud import ContactFormDetectionCRUD
from contactform.detection.models import ContactFormDetection
from contactform.detection import get_form_information, select_contact_url
from contactform.gpt import gemini_client
from contactform.insertion.form_check import get_all_links_from_source

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_webdriver(headless: bool = True) -> webdriver.Chrome:
    """
    Set up and return a Chrome WebDriver instance.

    Args:
        headless: Whether to run browser in headless mode

    Returns:
        Chrome WebDriver instance

    Raises:
        WebDriverException: If webdriver setup fails
    """
    try:
        chromedriver_autoinstaller.install()
        options = Options()

        if headless:
            options.add_argument('--headless')

        # Additional options for better reliability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)  # 30 second timeout

        return driver

    except Exception as e:
        logger.error(f"Failed to setup webdriver: {str(e)}")
        raise WebDriverException(f"Failed to setup webdriver: {str(e)}")


def validate_domain(domain: str) -> str:
    """
    Validate and normalize domain name.

    Args:
        domain: Domain name to validate

    Returns:
        Normalized domain URL

    Raises:
        ValueError: If domain is invalid
    """
    if not domain or not domain.strip():
        raise ValueError("Domain must be a non-empty string")

    # Remove whitespace
    domain = domain.strip()

    # Add protocol if missing
    if not domain.startswith(('http://', 'https://')):
        domain = f'https://{domain}'

    # Validate URL structure
    parsed = urlparse(domain)
    if not parsed.netloc:
        raise ValueError(f"Invalid domain format: {domain}")

    return domain


def detect_antibot_protection(page_source: str) -> Dict[str, Any]:
    """
    Detect anti-bot protection mechanisms in the page source.

    Args:
        page_source: HTML source code of the page

    Returns:
        Dictionary containing protection information
    """
    protection_info: Dict[str, Any] = {
        "website_antibot_detection": False,
        "form_antibot_detection": False,
        "form_antibot_type": None
    }

    source_lower = page_source.lower()

    # Check for common anti-bot protection mechanisms
    antibot_indicators = {
        "recaptcha": ["recaptcha", "g-recaptcha"],
        "hcaptcha": ["hcaptcha", "h-captcha"],
        "cloudflare": ["cloudflare", "cf-ray", "__cf_bm"],
        "turnstile": ["turnstile", "cf-turnstile"],
        "custom": ["captcha", "bot-protection", "anti-bot"]
    }

    detected_types: list[str] = []
    for protection_type, indicators in antibot_indicators.items():
        for indicator in indicators:
            if indicator in source_lower:
                detected_types.append(protection_type)
                break

    if detected_types:
        protection_info["website_antibot_detection"] = True
        protection_info["form_antibot_detection"] = True
        protection_info["form_antibot_type"] = detected_types[0]  # Use first detected type

    return protection_info


def search_domain_form(domain: str, db_session: Optional[Session] = None) -> ContactFormDetection:
    """
    Search for contact form information on a given domain using Selenium.

    This function will:
    1. Navigate to the domain
    2. Find contact page links
    3. Detect contact forms and their properties
    4. Update or create ContactFormDetection record
    5. Return the updated ContactFormDetection object

    Args:
        domain: Domain name to search (e.g., "example.com" or "https://example.com")
        db_session: Optional database session. If not provided, will create a new one.

    Returns:
        ContactFormDetection: Updated or created detection record

    Raises:
        ValueError: If domain is invalid
        WebDriverException: If selenium operations fail
        Exception: For other unexpected errors
    """
    # Validate and normalize domain
    domain_url = validate_domain(domain)
    domain_name = urlparse(domain_url).netloc

    # Set up database session
    db_provided = db_session is not None
    if not db_provided:
        db_session = get_db()

    driver = None
    detection_record = None

    try:
        logger.info(f"Starting form detection for domain: {domain_name}")

        # Check if detection record already exists
        existing_detections = ContactFormDetectionCRUD.get_by_domain(db_session, domain_name)
        detection_record = existing_detections[0] if existing_detections else None

        # Update status to indicate processing has started
        if detection_record:
            ContactFormDetectionCRUD.update(
                db_session,
                detection_record.id,
                detection_status="in_progress"
            )
        else:
            # Create new detection record
            detection_record = ContactFormDetectionCRUD.create(
                db_session,
                domain_name=domain_name,
                detection_status="in_progress"
            )

        # Set up webdriver
        driver = setup_webdriver(headless=True)

        # Step 1: Navigate to main domain
        logger.info(f"Navigating to: {domain_url}")
        driver.get(domain_url)

        # Get page source
        main_page_source = driver.page_source

        # Step 2: Detect anti-bot protection on main page
        protection_info = detect_antibot_protection(main_page_source)

        # Step 3: Find all links and select contact page
        all_links = get_all_links_from_source(main_page_source, domain_url)

        if not all_links:
            logger.warning(f"No links found on {domain_url}")
            # Update record with no form found
            updated_record = ContactFormDetectionCRUD.update(
                db_session,
                detection_record.id,
                detection_status="completed",
                contact_form_present=False,
                website_antibot_detection=protection_info["website_antibot_detection"],
                form_antibot_detection=False,
                form_antibot_type=None
            )
            if updated_record is None:
                raise RuntimeError("Failed to update detection record")
            return updated_record

        # Step 4: Select contact page using AI
        try:
            contact_page_url = select_contact_url(gemini_client, all_links)
            logger.info(f"Selected contact page: {contact_page_url}")
        except Exception as e:
            logger.warning(f"Failed to select contact page using AI: {str(e)}")
            # Try to find contact page using heuristics
            contact_keywords = ["contact", "about", "reach", "support", "team"]
            contact_page_url = None

            for text, url in all_links:
                text_lower = text.lower()
                url_lower = url.lower()
                if any(keyword in text_lower or keyword in url_lower for keyword in contact_keywords):
                    contact_page_url = url
                    break

            if not contact_page_url:
                logger.warning(f"No contact page found for {domain_name}")
                updated_record = ContactFormDetectionCRUD.update(
                    db_session,
                    detection_record.id,
                    detection_status="completed",
                    contact_form_present=False,
                    website_antibot_detection=protection_info["website_antibot_detection"],
                    form_antibot_detection=False,
                    form_antibot_type=None
                )
                if updated_record is None:
                    raise RuntimeError("Failed to update detection record")
                return updated_record

        # Step 5: Navigate to contact page
        logger.info(f"Navigating to contact page: {contact_page_url}")
        driver.get(contact_page_url)
        contact_page_source = driver.page_source

        # Step 6: Detect anti-bot protection on contact page
        contact_protection_info = detect_antibot_protection(contact_page_source)

        # Combine protection info (website-level and form-level)
        combined_protection = {
            "website_antibot_detection": protection_info["website_antibot_detection"] or contact_protection_info["website_antibot_detection"],
            "form_antibot_detection": contact_protection_info["form_antibot_detection"],
            "form_antibot_type": contact_protection_info["form_antibot_type"]
        }

        # Step 7: Analyze form using AI
        try:
            form_info_raw = get_form_information(gemini_client, contact_page_source)
            # type: ignore
            logger.info(f"Form analysis completed. Fields found: {len(form_info_raw.get('fields', []))}")
            # Cast to proper type for better type checking
            form_info = dict(form_info_raw)  # type: ignore
        except Exception as e:
            logger.error(f"Failed to analyze form using AI: {str(e)}")
            form_info = {"fields": [], "submit_button": None, "protection": []}

        # Step 8: Process form information
        fields_data = form_info.get("fields", [])  # type: ignore
        contact_form_present = bool(fields_data)  # type: ignore

        # Extract field information
        form_fields: list[str] = []
        field_selectors: Dict[str, str] = {}

        if isinstance(fields_data, list):
            for field in fields_data:  # type: ignore
                if isinstance(field, dict):
                    field_type = field.get("type", "unknown")  # type: ignore
                    field_selector = field.get("selector", "")  # type: ignore

                    if isinstance(field_type, str):
                        form_fields.append(field_type)
                    if isinstance(field_type, str) and isinstance(field_selector, str) and field_selector:
                        field_selectors[field_type] = field_selector

        # Extract submit button information
        submit_button_selector: Optional[str] = None
        submit_button_data = form_info.get("submit_button")  # type: ignore
        if isinstance(submit_button_data, dict):
            selector = submit_button_data.get("selector")  # type: ignore
            if isinstance(selector, str):
                submit_button_selector = selector

        # Update form action (try to extract from form tag)
        form_action: Optional[str] = None
        try:
            from bs4 import BeautifulSoup, Tag
            soup = BeautifulSoup(contact_page_source, 'html.parser')
            form_tag = soup.find('form')
            if isinstance(form_tag, Tag):
                action = form_tag.get('action')
                if isinstance(action, str) and action:
                    form_action = urljoin(contact_page_url, action)
        except Exception as e:
            logger.warning(f"Failed to extract form action: {str(e)}")

        # Update protection info based on AI analysis
        protection_data = form_info.get("protection", [])  # type: ignore
        if isinstance(protection_data, list) and protection_data:
            combined_protection["form_antibot_detection"] = True
            if not combined_protection["form_antibot_type"]:
                # Use first detected protection type from AI
                first_protection = protection_data[0]
                if isinstance(first_protection, dict):
                    issuer = first_protection.get("issuer")  # type: ignore
                    if isinstance(issuer, str):
                        combined_protection["form_antibot_type"] = issuer

        # Step 9: Update database record
        update_data: Dict[str, Any] = {
            "detection_status": "completed",
            "form_url": contact_page_url,
            "contact_form_present": contact_form_present,
            "website_antibot_detection": combined_protection["website_antibot_detection"],
            "form_antibot_detection": combined_protection["form_antibot_detection"],
            "form_antibot_type": combined_protection["form_antibot_type"],
            "form_fields": form_fields if form_fields else None,
            "field_selectors": field_selectors if field_selectors else None,
            "submit_button_selector": submit_button_selector,
            "form_action": form_action,
        }

        updated_record = ContactFormDetectionCRUD.update(
            db_session,
            detection_record.id,
            **update_data
        )

        if updated_record is None:
            raise RuntimeError("Failed to update detection record")

        logger.info(f"Successfully completed form detection for {domain_name}")
        return updated_record

    except WebDriverException as e:
        logger.error(f"Selenium error during form detection for {domain_name}: {str(e)}")
        # Update record with failed status
        if detection_record:
            ContactFormDetectionCRUD.update(
                db_session,
                detection_record.id,
                detection_status="failed"
            )
        raise

    except Exception as e:
        logger.error(f"Unexpected error during form detection for {domain_name}: {str(e)}")
        # Update record with failed status
        if detection_record:
            ContactFormDetectionCRUD.update(
                db_session,
                detection_record.id,
                detection_status="failed"
            )
        raise

    finally:
        # Clean up webdriver
        if driver:
            try:
                driver.quit()
            except WebDriverException as e:
                logger.warning(f"Error closing webdriver: {str(e)}")

        # Close database session if we created it
        if not db_provided and db_session:
            try:
                db_session.close()
            except RuntimeError as e:
                logger.warning(f"Error closing database session: {str(e)}")


def batch_search_domain_forms(domains: list[str], db_session: Optional[Session] = None) -> list[ContactFormDetection]:
    """
    Search for contact forms on multiple domains.

    Args:
        domains: List of domain names to search
        db_session: Optional database session

    Returns:
        List of ContactFormDetection records
    """
    results: list[ContactFormDetection] = []

    for domain in domains:
        try:
            result = search_domain_form(domain, db_session)
            results.append(result)
        except (ValueError, WebDriverException, RuntimeError) as e:
            logger.error(f"Failed to process domain {domain}: {str(e)}")
            # Continue with next domain
            continue

    return results
