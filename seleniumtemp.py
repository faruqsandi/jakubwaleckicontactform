from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
from contactform.detection import (
    get_form_information,
    select_contact_url,
    find_success_message,
)
from contactform.gpt import gemini_client


from contactform.insertion.form_check import (
    get_all_links_from_source,
    verify_form_elements,
    fill_form_fields,
    submit_form,
    verify_success_message,
)

chromedriver_autoinstaller.install()
options = Options()
# options.add_argument('--headless')  # Remove this line if you want to see the browser
service = Service()
driver = webdriver.Chrome(service=service, options=options)


url = "https://50safe.pl/"
# Step 1: Open Google
driver.set_page_load_timeout(60)  # Set 60 second timeout
driver.get(url)

source = driver.page_source

all_links = get_all_links_from_source(source, url)
contact_page = select_contact_url(gemini_client, all_links)


driver.set_page_load_timeout(60)  # Set 60 second timeout
driver.get(contact_page)
contact_page_source = driver.page_source


form_info = get_form_information(gemini_client, contact_page_source)


# Verify form elements using the helper function
verify_form_elements(driver, form_info)

values = {
    "name": "John Doe",
    "email": "john@example.com",
    # "address": "123 Main St, City, State",
    "message": "Hello, this is my message",
    "telephone": "1234567890",
}

fields = form_info["fields"]
result = fill_form_fields(driver, fields, values)

submit_button = form_info["submit_button"]

submit_form(driver, submit_button)


contact_page_source_post_insertion = driver.page_source

# Check if the page content changed after form submission
page_changed = contact_page_source_post_insertion != contact_page_source
print(f"\nPage content changed after form submission: {page_changed}")

success_message = find_success_message(
    gemini_client, contact_page_source_post_insertion
)


# Basic verification
success_verification_result = verify_success_message(driver, success_message)

# Close the browser
driver.quit()
