from google import genai
import re
import json

from config import Config

config = Config()
# The client gets the API key from the environment variable `GEMINI_API_KEY`.
gemini_client = genai.Client(api_key=config.GOOGLE_AI_API_KEY)

# response = client.models.generate_content(
#     model="gemini-2.5-flash", contents="Explain how AI works in a few words"
# )
# print(response.text)


def select_contact_url(client: genai.Client, url_list: list[tuple[str, str]]) -> str:
    # If the list is empty, return None
    if not url_list:
        raise ValueError("The URL list is empty.")

    # Construct a prompt for Gemini to analyze the links
    prompt = """
    Analyze the following list of website links (text and URL) and identify which one most likely points to a contact page or about page.
    Consider both the link text and URL path. Return only the index number (0-based) of the best match.
    
    Links:
    """

    # Add each link to the prompt
    for i, (text, url) in enumerate(url_list):
        prompt += f"{i}: Text: '{text}', URL: '{url}'\n"

    prompt += "\nReturn only the index number of the best contact/about page link:"

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

    # # Fallback: Use a heuristic approach
    # contact_keywords = ["contact", "about", "reach us", "get in touch", "support", "team"]
    # for text, url in url_list:
    #     text_lower = text.lower()
    #     url_lower = url.lower()
    #     for keyword in contact_keywords:
    #         if keyword in text_lower or keyword in url_lower:
    #             return url
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
