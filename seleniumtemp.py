from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import chromedriver_autoinstaller
from gpt import select_contact_url, gemini_client, get_form_information
from helper import get_all_links_from_source

chromedriver_autoinstaller.install()
options = Options()
# options.add_argument('--headless')  # Remove this line if you want to see the browser
service = Service()
driver = webdriver.Chrome(service=service, options=options)


url = "https://50safe.pl/"
# Step 1: Open Google
driver.get(url)

source = driver.page_source

all_links = get_all_links_from_source(source, url)
contact_page = select_contact_url(gemini_client, all_links)


driver.get(contact_page)
contact_page_source = driver.page_source


form_info = get_form_information(gemini_client, contact_page_source)
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
        element = driver.find_element(By.CSS_SELECTOR, field_selector)
        print(f"✓ Field '{field_label}' ({field_type}) found: {field_selector}")
    except NoSuchElementException:
        try:
            # If CSS selector fails, try using name attribute
            element = driver.find_element(By.NAME, field_selector)
            print(
                f"✓ Field '{field_label}' ({field_type}) found by name: {field_selector}"
            )
        except NoSuchElementException:
            try:
                # If name fails, try using ID
                element = driver.find_element(By.ID, field_selector)
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
        element = driver.find_element(By.CSS_SELECTOR, submit_selector)
        print(f"✓ Submit button '{submit_label}' found: {submit_selector}")
    except NoSuchElementException:
        try:
            # Try by name
            element = driver.find_element(By.NAME, submit_selector)
            print(f"✓ Submit button '{submit_label}' found by name: {submit_selector}")
        except NoSuchElementException:
            try:
                # Try by ID
                element = driver.find_element(By.ID, submit_selector)
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


# Close the browser
driver.quit()
