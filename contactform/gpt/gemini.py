from google import genai

from config import Config

config = Config()
# The client gets the API key from the environment variable `GEMINI_API_KEY`.
gemini_client = genai.Client(api_key=config.GOOGLE_AI_API_KEY)
