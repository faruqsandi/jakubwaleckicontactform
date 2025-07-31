from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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


form_info = get_form_information(contact_page_source)
fields = form_info.get("fields", [])
protection = form_info.get("protection", [])
submit_button = form_info.get("submit_button", None)


# Analyze the contact form
form_info = get_form_information(contact_page_source)
print("Form analysis result:", form_info)

# Close the browser
driver.quit()
