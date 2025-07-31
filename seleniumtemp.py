from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import chromedriver_autoinstaller
from gpt import select_contact_url, gemini_client
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


def get_form_information(source: str) -> dict:
    """
    Analyze HTML source to extract contact form information using Gemini AI.

    Args:
        source (str): HTML source code of the page containing the contact form

    Returns:
        dict: Form information including fields and protection mechanisms
    """
    prompt = f"""
Analyze the following HTML source code and extract contact form information. Return your response as a valid JSON object with the following structure:

{{
    "fields": [
        {{
            "label": "field label text",
            "selector": "CSS selector or name attribute to identify the field",
            "type": "FIELD_TYPE"
        }}
    ],
    "submit_button": {{
        "label": "submit button text",
        "selector": "CSS selector or name attribute to identify the submit button"
    }},
    "protection": [
        {{
            "type": "PROTECTION_TYPE",
            "issuer": "PROTECTION_PROVIDER"
        }}
    ]
}}

Rules:
- FIELD_TYPE can only be: "name", "telephone", "email", "message"
- PROTECTION_TYPE can only be: "captcha"
- PROTECTION_PROVIDER can be: "recaptcha", "hcaptcha", "cloudflare", "custom", "unknown"
- Look for form elements like input, textarea, select
- Identify field types based on labels, names, types, or placeholders
- Find the submit button (input[type="submit"], button[type="submit"], or button inside form)
- Detect protection mechanisms like reCAPTCHA, hCaptcha, etc.
- If no protection is found, return empty protection array
- If no submit button is found, return null for submit_button
- Only return the JSON object, no additional text

HTML Source:
{source}
"""

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # Extract JSON from response
        response_text = response.text.strip()

        # Remove any markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith('```'):
            response_text = response_text[3:-3].strip()

        # Parse JSON response
        import json
        form_info = json.loads(response_text)

        return form_info

    except Exception as e:
        print(f"Error analyzing form: {e}")
        return {
            "fields": [],
            "submit_button": None,
            "protection": []
        }


form_info = get_form_information(contact_page_source)
fields = form_info.get("fields", [])
protection = form_info.get("protection", [])
submit_button = form_info.get("submit_button", None)


# Analyze the contact form
form_info = get_form_information(contact_page_source)
print("Form analysis result:", form_info)

# Close the browser
driver.quit()
