import logging
import os

from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

logger = logging.getLogger(__name__)


class Config:
    GOOGLE_SEARCH_API_KEY = os.environ["GOOGLE_SEARCH_API_KEY"]
    SEARCH_ENGINE_ID = os.environ["SEARCH_ENGINE_ID"]
