from google import genai

import re
import json


def select_contact_url(client: genai.Client, url_list: list[tuple[str, str]]) -> str:
    # If the list is empty, return None
    if not url_list:
        raise ValueError("The URL list is empty.")

    # Construct a prompt for Gemini to analyze the links
    prompt = """You are analyzing a list of website links to find the CONTACT PAGE. The website may be in Polish or English.

PRIORITY ORDER (choose the highest priority match):
1. CONTACT PAGES - Look for these keywords in link text or URL:
   - English: "contact", "contact us", "get in touch", "reach us", "write to us"
   - Polish: "kontakt", "skontaktuj się", "napisz do nas", "kontakt z nami"
   - URL patterns: "/contact", "/kontakt", "/contact-us", "/kontakt-z-nami"

2. ABOUT/COMPANY PAGES (only if no contact page found):
   - English: "about", "about us", "company", "team", "who we are"
   - Polish: "o nas", "o firmie", "kim jesteśmy", "zespół", "firma"
   - URL patterns: "/about", "/o-nas", "/o-firmie", "/about-us"

RULES:
- Return ONLY the index number (0-based) of the BEST match
- Prefer exact "contact"/"kontakt" matches over about pages
- Prefer pages from the SAME DOMAIN (not external links)
- If multiple contact pages exist, choose the most direct one
- If NO contact or about pages found, return the index of the most relevant page

Links to analyze:
    """

    # Add each link to the prompt
    for i, (text, url) in enumerate(url_list):
        prompt += f"{i}: Text: '{text}', URL: '{url}'\n"

    prompt += f"\nReturn ONLY the index number (0-{len(url_list)}) of the best contact page!"

    try:
        # Send the prompt to Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        # Get the response text and extract the index
        response_text = response.text.strip()
        match = re.search(r"\b(\d+)\b", response_text)

        if match:
            index = int(match.group(1))
            if 0 <= index < len(url_list):
                return url_list[index][1]  # Return the URL at the selected index

    except Exception as e:
        print(f"Error calling Gemini API: {e}")

    # Fallback: Use a heuristic approach with Polish and English keywords
    contact_keywords = [
        # English keywords
        "contact", "contact us", "get in touch", "reach us", "write to us", "support",
        # Polish keywords
        "kontakt", "skontaktuj się", "napisz do nas", "kontakt z nami",
        # URL patterns
        "/contact", "/kontakt", "/contact-us", "/kontakt-z-nami"
    ]

    about_keywords = [
        # English keywords
        "about", "about us", "company", "team", "who we are",
        # Polish keywords
        "o nas", "o firmie", "kim jesteśmy", "zespół", "firma",
        # URL patterns
        "/about", "/o-nas", "/o-firmie", "/about-us"
    ]

    # First try to find contact pages
    for text, url in url_list:
        text_lower = text.lower()
        url_lower = url.lower()
        for keyword in contact_keywords:
            if keyword in text_lower or keyword in url_lower:
                return url

    # If no contact page found, try about pages
    for text, url in url_list:
        text_lower = text.lower()
        url_lower = url.lower()
        for keyword in about_keywords:
            if keyword in text_lower or keyword in url_lower:
                return url

    raise ValueError("No suitable contact page found in the provided URLs.")


def get_form_information(client: genai.Client, source: str) -> dict:
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
- FIELD_TYPE can only be: "name", "telephone", "email", "message", "unknown"
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
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        # Extract JSON from response
        response_text = response.text.strip()

        # Remove any markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()

        # Parse JSON response
        form_info = json.loads(response_text)

        return form_info

    except Exception as e:
        print(f"Error analyzing form: {e}")
        return {"fields": [], "submit_button": None, "protection": []}


def find_success_message(client: genai.Client, source: str) -> dict:
    """
    Analyze HTML source to find elements indicating successful form submission.

    Args:
        source (str): HTML source code of the page after form submission

    Returns:
        dict: Information about success indicators found on the page
    """
    prompt = f"""
Analyze the following HTML source code to find elements that indicate a contact form was successfully submitted. Return your response as a valid JSON object with the following structure:

{{
    "success_found": true/false,
    "success_elements": [
        {{
            "text": "the text content of the success element",
            "selector": "CSS selector to identify the element",
            "element_type": "ELEMENT_TYPE"
        }}
    ],
    "confidence": "high/medium/low"
}}

Rules:
- ELEMENT_TYPE can be: "message", "banner", "alert", "modal", "redirect", "other"
- Look for elements that contain success indicators like:
  - "thank you", "message sent", "form submitted", "we'll get back to you"
  - "success", "submitted successfully", "received your message"
  - CSS classes like "success", "alert-success", "message-success"
  - Elements with green styling or checkmark icons
- Set confidence based on how clear the success indication is:
  - "high": Clear success message with explicit confirmation
  - "medium": Likely success indication but somewhat ambiguous
  - "low": Possible success indication but uncertain
- If no success indicators are found, set success_found to false and return empty success_elements array
- Only return the JSON object, no additional text

HTML Source:
{source}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        # Extract JSON from response
        response_text = response.text.strip()

        # Remove any markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()

        # Parse JSON response
        success_info = json.loads(response_text)

        return success_info

    except Exception as e:
        print(f"Error analyzing success message: {e}")
        return {"success_found": False, "success_elements": [], "confidence": "low"}
