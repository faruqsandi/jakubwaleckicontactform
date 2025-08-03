from urllib.parse import urljoin
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


def verify_form_elements(driver: WebDriver, form_info: dict) -> None:
    """
    Verify the presence of form fields, submit button, and protection mechanisms.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        form_info (dict): Dictionary containing form information with fields, submit_button, and protection.
    """
    fields = form_info.get("fields", [])
    protection = form_info.get("protection", [])
    submit_button = form_info.get("submit_button", None)

    print(f"Found {len(fields)} form fields to check:")

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
                    print(
                        f"✗ Field '{field_label}' ({field_type}) NOT FOUND with selector: {field_selector}"
                    )

    # Check submit button presence if it exists
    if submit_button:
        submit_label = submit_button.get("label", "Submit")
        submit_selector = submit_button.get("selector", "")

        try:
            # Try to find the submit button
            _ = driver.find_element(By.CSS_SELECTOR, submit_selector)
            print(f"✓ Submit button '{submit_label}' found: {submit_selector}")
        except NoSuchElementException:
            try:
                # Try by name
                _ = driver.find_element(By.NAME, submit_selector)
                print(
                    f"✓ Submit button '{submit_label}' found by name: {submit_selector}"
                )
            except NoSuchElementException:
                try:
                    # Try by ID
                    _ = driver.find_element(By.ID, submit_selector)
                    print(
                        f"✓ Submit button '{submit_label}' found by ID: {submit_selector}"
                    )
                except NoSuchElementException:
                    print(
                        f"✗ Submit button '{submit_label}' NOT FOUND with selector: {submit_selector}"
                    )
    else:
        print("No submit button information found")

    # Check protection mechanisms
    if protection:
        print(f"\nFound {len(protection)} protection mechanisms:")
        for prot in protection:
            prot_type = prot.get("type", "unknown")
            prot_issuer = prot.get("issuer", "unknown")
            print(f"- {prot_type} by {prot_issuer}")
    else:
        print("\nNo protection mechanisms detected")
