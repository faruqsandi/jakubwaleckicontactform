from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
from contactform.detection import get_form_information, select_contact_url
from contactform.gpt import gemini_client


from contactform.gpt import select_contact_url, get_form_information
from contactform.insertion.form_check import get_all_links_from_source, verify_form_elements, fill_form_fields

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


# Verify form elements using the helper function
verify_form_elements(driver, form_info)

values = {
    "name": "John Doe",
    "email": "john@example.com",
    "address": "123 Main St, City, State",
    "message": "Hello, this is my message"
}

fields = form_info['fields']
result = fill_form_fields(driver, fields, values)

# Close the browser
driver.quit()
