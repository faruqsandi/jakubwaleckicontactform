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


def fill_form_fields(
    driver: WebDriver, fields: list[dict[str, str]], values: dict[str, str]
) -> bool | dict[str, list[str]]:
    """
    Fill form fields with provided values.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        fields (list[dict[str, str]]): List of field dictionaries containing label, selector, and type.
        values (dict[str, str]): Dictionary mapping field types to their values (e.g., {"name": "John", "email": "john@example.com"}).

    Returns:
        bool | dict[str, list[str]]: True if all fields filled successfully, otherwise dict with error messages.
    """
    print(f"Filling {len(fields)} form fields:")
    errors = []

    for field in fields:
        field_label = field["label"]
        field_selector = field["selector"]
        field_type = field[
            "type"
        ]  # This is the semantic type like "name", "email", "address"

        # Get the value for this field using the field type as key
        field_value = values.get(field_type)
        if field_value is None:
            print(
                f"⚠ No value provided for field type '{field_type}' (label: '{field_label}'), skipping"
            )
            continue

        # Find the element
        element = None
        try:
            # Try to find the element using CSS selector first
            element = driver.find_element(By.CSS_SELECTOR, field_selector)
        except NoSuchElementException:
            try:
                # If CSS selector fails, try using name attribute
                element = driver.find_element(By.NAME, field_selector)
            except NoSuchElementException:
                try:
                    # If name fails, try using ID
                    element = driver.find_element(By.ID, field_selector)
                except NoSuchElementException:
                    error_msg = f"Field '{field_label}' (type: {field_type}) NOT FOUND with selector: {field_selector}"
                    print(f"✗ {error_msg}")
                    errors.append(error_msg)
                    continue

        # Determine the HTML input type and fill accordingly
        try:
            # Get the HTML tag and type attribute
            tag_name = element.tag_name.lower()
            input_type = element.get_attribute("type")
            if input_type:
                input_type = input_type.lower()

            if tag_name == "textarea":
                # Handle textarea
                element.clear()
                element.send_keys(field_value)
                print(
                    f"✓ Filled textarea '{field_label}' ({field_type}) with: {field_value}"
                )
            elif tag_name == "select":
                # Handle select dropdown
                from selenium.webdriver.support.ui import Select

                select = Select(element)
                select.select_by_visible_text(field_value)
                print(
                    f"✓ Selected '{field_value}' in dropdown '{field_label}' ({field_type})"
                )
            elif tag_name == "input" and input_type in ["checkbox", "radio"]:
                # Handle checkbox and radio buttons
                if field_value.lower() in ["true", "1", "yes", "on", "checked"]:
                    if not element.is_selected():
                        element.click()
                    print(f"✓ Checked '{field_label}' ({field_type})")
                else:
                    if element.is_selected():
                        element.click()
                    print(f"✓ Unchecked '{field_label}' ({field_type})")
            elif tag_name == "input" and input_type in [
                "text",
                "email",
                "password",
                "tel",
                "url",
                "number",
                "search",
            ]:
                # Handle various text input types
                element.clear()
                element.send_keys(field_value)
                print(
                    f"✓ Filled {input_type} field '{field_label}' ({field_type}) with: {field_value}"
                )
            else:
                # Default behavior for unknown or standard input fields
                element.clear()
                element.send_keys(field_value)
                print(
                    f"✓ Filled field '{field_label}' ({field_type}) with: {field_value}"
                )

        except Exception as e:
            error_msg = (
                f"Failed to fill field '{field_label}' (type: {field_type}): {str(e)}"
            )
            print(f"✗ {error_msg}")
            errors.append(error_msg)

    if errors:
        return {"fill_errors": errors}
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


def submit_form(
    driver: WebDriver, submit_button: dict[str, str] | None
) -> bool | dict[str, list[str]]:
    """
    Submit the form by clicking the submit button.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        submit_button (dict[str, str] | None): Dictionary containing submit button information or None.

    Returns:
        bool | dict[str, list[str]]: True if form submitted successfully, otherwise dict with error messages.
    """
    if not submit_button:
        error_msg = "No submit button information provided"
        print(f"✗ {error_msg}")
        return {"submit_errors": [error_msg]}

    submit_label = submit_button.get("label", "Submit")
    submit_selector = submit_button.get("selector", "")

    if not submit_selector:
        error_msg = f"No selector provided for submit button '{submit_label}'"
        print(f"✗ {error_msg}")
        return {"submit_errors": [error_msg]}

    errors: list[str] = []
    element = None

    try:
        # Try to find the submit button using CSS selector first
        element = driver.find_element(By.CSS_SELECTOR, submit_selector)
        print(f"✓ Submit button '{submit_label}' found: {submit_selector}")
    except NoSuchElementException:
        try:
            # If CSS selector fails, try using name attribute
            element = driver.find_element(By.NAME, submit_selector)
            print(f"✓ Submit button '{submit_label}' found by name: {submit_selector}")
        except NoSuchElementException:
            try:
                # If name fails, try using ID
                element = driver.find_element(By.ID, submit_selector)
                print(
                    f"✓ Submit button '{submit_label}' found by ID: {submit_selector}"
                )
            except NoSuchElementException:
                error_msg = f"Submit button '{submit_label}' NOT FOUND with selector: {submit_selector}"
                print(f"✗ {error_msg}")
                errors.append(error_msg)
                return {"submit_errors": errors}

    # Try to click the submit button
    try:
        if element and element.is_enabled():
            element.click()
            print(f"✓ Form submitted successfully by clicking '{submit_label}'")
            return True
        else:
            error_msg = f"Submit button '{submit_label}' is not enabled or clickable"
            print(f"✗ {error_msg}")
            errors.append(error_msg)
            return {"submit_errors": errors}
    except (NoSuchElementException, AttributeError) as e:
        error_msg = f"Failed to click submit button '{submit_label}': {str(e)}"
        print(f"✗ {error_msg}")
        errors.append(error_msg)
        return {"submit_errors": errors}


def fill_and_submit_form(
    driver: WebDriver, form_info: dict[str, Any], values: dict[str, str]
) -> bool | dict[str, list[str]]:
    """
    Fill and submit a form with provided values.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        form_info (dict[str, Any]): Dictionary containing form information with fields and submit_button.
        values (dict[str, str]): Dictionary mapping field types to their values.

    Returns:
        bool | dict[str, list[str]]: True if form filled and submitted successfully, otherwise dict with error messages.
    """
    fields = form_info.get("fields", [])
    submit_button = form_info.get("submit_button", None)

    # First, fill the form fields
    fill_result = fill_form_fields(driver, fields, values)

    if isinstance(fill_result, dict):
        return fill_result  # Return fill errors if any

    print("✓ All form fields filled successfully")

    # Then submit the form
    submit_result = submit_form(driver, submit_button)

    if isinstance(submit_result, dict):
        return submit_result  # Return submit errors if any

    print("✓ Form submitted successfully")
    return True


def verify_success_message(
    driver: WebDriver, success_info: dict[str, Any]
) -> bool | dict[str, list[str]]:
    """
    Verify the presence of success message elements on the page.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        success_info (dict[str, Any]): Dictionary containing success message information from Gemini AI.

    Returns:
        bool | dict[str, list[str]]: True if success elements found as expected, otherwise dict with error messages.
    """
    success_found = success_info.get("success_found", False)
    success_elements = success_info.get("success_elements", [])
    confidence = success_info.get("confidence", "low")

    print(f"\nChecking for success message (confidence: {confidence}):")

    if not success_found:
        print("✓ No success message expected and none should be found")
        return True

    errors = []

    print(f"Looking for {len(success_elements)} success elements:")

    for i, element_info in enumerate(success_elements):
        element_text = element_info.get("text", "")
        element_selector = element_info.get("selector", "")
        element_type = element_info.get("element_type", "unknown")

        if not element_selector:
            error_msg = f"Success element {i + 1} has no selector provided"
            print(f"✗ {error_msg}")
            errors.append(error_msg)
            continue

        # Try to find the success element
        element_found = False
        try:
            # Try to find the element using CSS selector first
            element = driver.find_element(By.CSS_SELECTOR, element_selector)
            if element.is_displayed():
                print(
                    f"✓ Success {element_type} found and visible: '{element_text}' (selector: {element_selector})"
                )
                element_found = True
            else:
                print(
                    f"⚠ Success {element_type} found but not visible: '{element_text}' (selector: {element_selector})"
                )
                element_found = True
        except NoSuchElementException:
            try:
                # If CSS selector fails, try using ID
                element = driver.find_element(By.ID, element_selector)
                if element.is_displayed():
                    print(
                        f"✓ Success {element_type} found by ID and visible: '{element_text}' (selector: {element_selector})"
                    )
                    element_found = True
                else:
                    print(
                        f"⚠ Success {element_type} found by ID but not visible: '{element_text}' (selector: {element_selector})"
                    )
                    element_found = True
            except NoSuchElementException:
                try:
                    # Try using class name if selector looks like a class
                    if element_selector.startswith("."):
                        class_name = element_selector[1:]
                        element = driver.find_element(By.CLASS_NAME, class_name)
                        if element.is_displayed():
                            print(
                                f"✓ Success {element_type} found by class and visible: '{element_text}' (selector: {element_selector})"
                            )
                            element_found = True
                        else:
                            print(
                                f"⚠ Success {element_type} found by class but not visible: '{element_text}' (selector: {element_selector})"
                            )
                            element_found = True
                except NoSuchElementException:
                    # Try to find by text content as fallback
                    try:
                        xpath_text_selector = f"//*[contains(text(), '{element_text}')]"
                        element = driver.find_element(By.XPATH, xpath_text_selector)
                        if element.is_displayed():
                            print(
                                f"✓ Success {element_type} found by text content and visible: '{element_text}'"
                            )
                            element_found = True
                        else:
                            print(
                                f"⚠ Success {element_type} found by text content but not visible: '{element_text}'"
                            )
                            element_found = True
                    except NoSuchElementException:
                        pass

        if not element_found:
            error_msg = f"Success {element_type} NOT FOUND: '{element_text}' (selector: {element_selector})"
            print(f"✗ {error_msg}")
            errors.append(error_msg)

    if errors:
        # Check confidence level to determine if errors are critical
        if confidence == "high":
            return {"success_verification_errors": errors}
        elif confidence == "medium":
            print(
                f"⚠ Some success elements not found, but confidence is only {confidence}"
            )
            return {"success_verification_warnings": errors}
        else:
            print(
                f"⚠ Success elements not found, but confidence is {confidence} - treating as non-critical"
            )
            return True

    print("✓ All expected success elements found")
    return True


def check_success_message_after_submission(
    driver: WebDriver, success_info: dict[str, Any]
) -> dict[str, Any]:
    """
    Check for success message after form submission and return detailed results.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        success_info (dict[str, Any]): Dictionary containing expected success message information from Gemini AI.

    Returns:
        dict[str, Any]: Detailed results of the success message verification including status, elements found, and any issues.
    """
    result = {
        "success_expected": success_info.get("success_found", False),
        "confidence": success_info.get("confidence", "low"),
        "elements_checked": len(success_info.get("success_elements", [])),
        "elements_found": 0,
        "elements_visible": 0,
        "verification_passed": False,
        "issues": [],
        "found_elements": [],
    }

    verification_result = verify_success_message(driver, success_info)

    if verification_result is True:
        result["verification_passed"] = True
        result["elements_found"] = result["elements_checked"]
        result["elements_visible"] = result["elements_checked"]
    elif isinstance(verification_result, dict):
        # Count successful elements by checking which ones didn't have errors
        errors = verification_result.get("success_verification_errors", [])
        warnings = verification_result.get("success_verification_warnings", [])

        if errors:
            result["issues"].extend(errors)
            result["elements_found"] = max(0, result["elements_checked"] - len(errors))
        elif warnings:
            result["issues"].extend(warnings)
            result["elements_found"] = max(
                0, result["elements_checked"] - len(warnings)
            )
            # For warnings (medium confidence), still consider it passed
            if result["confidence"] == "medium":
                result["verification_passed"] = True

    # Try to get actual text content of found elements for verification
    success_elements = success_info.get("success_elements", [])
    for element_info in success_elements:
        element_selector = element_info.get("selector", "")
        element_text = element_info.get("text", "")

        if element_selector:
            try:
                element = driver.find_element(By.CSS_SELECTOR, element_selector)
                actual_text = element.text.strip()
                result["found_elements"].append(
                    {
                        "expected_text": element_text,
                        "actual_text": actual_text,
                        "selector": element_selector,
                        "visible": element.is_displayed(),
                    }
                )
                if element.is_displayed():
                    result["elements_visible"] += 1
            except NoSuchElementException:
                result["found_elements"].append(
                    {
                        "expected_text": element_text,
                        "actual_text": None,
                        "selector": element_selector,
                        "visible": False,
                    }
                )

    return result
