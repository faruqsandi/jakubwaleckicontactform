from urllib.parse import urljoin
from typing import Any
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement


def get_all_links_from_source(source: str, base_url: str) -> list[tuple[str, str]]:
    """
    Extract all links from the given HTML source code.

    Args:
        source (str): The HTML source code as a string.
        base_url (str): The base URL to resolve relative links.

    Returns:
        list[tuple[str, str]]: A list of tuples containing link text and href.
    """

    soup = BeautifulSoup(source, "html.parser")
    links = soup.find_all("a")

    link_list = []
    for link in links:
        text = link.get_text(strip=True)
        href = link.get("href")
        if href and text:
            if href == "#":
                continue
            # This urljoin can handle both slash and no slash
            href = urljoin(base_url, href)  # Make sure href is absolute
            link_list.append((text, href))

    return link_list


def verify_form_fields(
    driver: WebDriver, fields: list[dict[str, str]]
) -> bool | dict[str, list[str]]:
    """
    Verify the presence of form fields.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        fields (list[dict[str, str]]): List of field dictionaries containing label, selector, and type.

    Returns:
        bool | dict[str, list[str]]: True if all fields found, otherwise dict with error messages.
    """
    print(f"Found {len(fields)} form fields to check:")
    errors = []

    for field in fields:
        field_label = field["label"]
        field_selector = field["selector"]
        field_type = field["type"]

        # Check if the element is present on the page
        try:
            # Try to find the element using CSS selector first
            _: WebElement = driver.find_element(By.CSS_SELECTOR, field_selector)
            print(f"✓ Field '{field_label}' ({field_type}) found: {field_selector}")
        except NoSuchElementException:
            try:
                # If CSS selector fails, try using name attribute
                _ = driver.find_element(By.NAME, field_selector)
                print(
                    f"✓ Field '{field_label}' ({field_type}) found by name: {field_selector}"
                )
            except NoSuchElementException:
                try:
                    # If name fails, try using ID
                    _ = driver.find_element(By.ID, field_selector)
                    print(
                        f"✓ Field '{field_label}' ({field_type}) found by ID: {field_selector}"
                    )
                except NoSuchElementException:
                    error_msg = f"Field '{field_label}' ({field_type}) NOT FOUND with selector: {field_selector}"
                    print(f"✗ {error_msg}")
                    errors.append(error_msg)

    if errors:
        return {"field_errors": errors}
    return True


def verify_submit_button(
    driver: WebDriver, submit_button: dict[str, str] | None
) -> bool | dict[str, list[str]]:
    """
    Verify the presence of the submit button.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        submit_button (dict[str, str] | None): Dictionary containing submit button information or None.

    Returns:
        bool | dict[str, list[str]]: True if submit button found or not required, otherwise dict with error messages.
    """
    # Check submit button presence if it exists
    if submit_button:
        submit_label = submit_button.get("label", "Submit")
        submit_selector = submit_button.get("selector", "")
        errors = []

        try:
            # Try to find the submit button
            _ = driver.find_element(By.CSS_SELECTOR, submit_selector)
            print(f"✓ Submit button '{submit_label}' found: {submit_selector}")
            return True
        except NoSuchElementException:
            try:
                # Try by name
                _ = driver.find_element(By.NAME, submit_selector)
                print(
                    f"✓ Submit button '{submit_label}' found by name: {submit_selector}"
                )
                return True
            except NoSuchElementException:
                try:
                    # Try by ID
                    _ = driver.find_element(By.ID, submit_selector)
                    print(
                        f"✓ Submit button '{submit_label}' found by ID: {submit_selector}"
                    )
                    return True
                except NoSuchElementException:
                    error_msg = f"Submit button '{submit_label}' NOT FOUND with selector: {submit_selector}"
                    print(f"✗ {error_msg}")
                    errors.append(error_msg)
                    return {"submit_button_errors": errors}
    else:
        print("No submit button information found")
        return True


def verify_protection_mechanisms(
    protection: list[dict[str, str]],
) -> bool | dict[str, list[str]]:
    """
    Verify and display protection mechanisms.

    Args:
        protection (list[dict[str, str]]): List of protection mechanism dictionaries.

    Returns:
        bool | dict[str, list[str]]: True if protection mechanisms are valid, otherwise dict with error messages.
    """
    # Check protection mechanisms
    if protection:
        print(f"\nFound {len(protection)} protection mechanisms:")
        errors = []

        for prot in protection:
            prot_type = prot.get("type", "unknown")
            prot_issuer = prot.get("issuer", "unknown")

            if prot_type == "unknown" or prot_issuer == "unknown":
                error_msg = f"Invalid protection mechanism: type='{prot_type}', issuer='{prot_issuer}'"
                errors.append(error_msg)
                print(f"✗ {error_msg}")
            else:
                print(f"✓ {prot_type} by {prot_issuer}")

        if errors:
            return {"protection_errors": errors}
        return True
    else:
        print("\nNo protection mechanisms detected")
        return True


def verify_form_elements(
    driver: WebDriver, form_info: dict[str, Any]
) -> bool | dict[str, list[str]]:
    """
    Verify the presence of form fields, submit button, and protection mechanisms.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        form_info (dict[str, Any]): Dictionary containing form information with fields, submit_button, and protection.

    Returns:
        bool | dict[str, list[str]]: True if all verifications pass, otherwise dict with all error messages.
    """
    fields = form_info.get("fields", [])
    protection = form_info.get("protection", [])
    submit_button = form_info.get("submit_button", None)

    field_result = verify_form_fields(driver, fields)
    button_result = verify_submit_button(driver, submit_button)
    protection_result = verify_protection_mechanisms(protection)

    # Collect all errors
    all_errors = []

    if isinstance(field_result, dict):
        all_errors.extend(field_result.get("field_errors", []))

    if isinstance(button_result, dict):
        all_errors.extend(button_result.get("submit_button_errors", []))

    if isinstance(protection_result, dict):
        all_errors.extend(protection_result.get("protection_errors", []))

    if all_errors:
        return {"errors": all_errors}

    return True
