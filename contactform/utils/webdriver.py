"""
WebDriver utilities for Selenium operations.

This module provides shared functionality for setting up and managing WebDriver instances
across different modules to avoid circular dependencies.
"""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import chromedriver_autoinstaller  # type: ignore

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_webdriver(headless: bool = True) -> webdriver.Chrome:
    """
    Set up and return a Chrome WebDriver instance.

    Args:
        headless: Whether to run browser in headless mode

    Returns:
        Chrome WebDriver instance

    Raises:
        WebDriverException: If webdriver setup fails
    """
    try:
        chromedriver_autoinstaller.install()
        options = Options()

        if headless:
            options.add_argument("--headless")

        # Additional options for better reliability
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)  # 30 second timeout

        return driver

    except Exception as e:
        logger.error(f"Failed to setup webdriver: {str(e)}")
        raise WebDriverException(f"Failed to setup webdriver: {str(e)}") from e
