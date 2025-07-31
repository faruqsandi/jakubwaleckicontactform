from google import genai
import re
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
            model="gemini-2.5-flash",
            contents=prompt
        )

        # Get the response text and extract the index
        response_text = response.text.strip()
        match = re.search(r'\b(\d+)\b', response_text)

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
