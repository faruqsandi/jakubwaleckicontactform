"""
Web Scraper Module

This module provides functionality for web scraping using Selenium and BeautifulSoup.
It includes classes for link extraction and search operations.
"""

from urllib.parse import urljoin
from typing import Any
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    import chromedriver_autoinstaller
except ImportError:
    chromedriver_autoinstaller = None


class WebDriver:
    """Base web driver class for managing Chrome browser instances."""

    def __init__(self, headless: bool = False, timeout: int = 10):
        """
        Initialize the web driver.

        Args:
            headless (bool): Whether to run browser in headless mode
            timeout (int): Default timeout for web driver waits
        """
        self.timeout = timeout
        self.driver: webdriver.Chrome = self._setup_driver(headless)

    def _setup_driver(self, headless: bool) -> webdriver.Chrome:
        """Set up Chrome driver with specified options."""
        if chromedriver_autoinstaller:
            chromedriver_autoinstaller.install()

        options = Options()
        if headless:
            options.add_argument("--headless")

        service = Service()
        return webdriver.Chrome(service=service, options=options)

    def get_page_source(self, url: str) -> str:
        """
        Navigate to URL and return page source.

        Args:
            url (str): The URL to navigate to

        Returns:
            str: The page source HTML
        """
        self.driver.get(url)
        return self.driver.page_source

    def quit(self) -> None:
        """Close the browser and quit the driver."""
        if self.driver:
            self.driver.quit()

    def __enter__(self) -> "WebDriver":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.quit()


class LinkExtractor:
    """Class for extracting links from web pages."""

    def __init__(self, web_driver: WebDriver):
        """
        Initialize with a web driver instance.

        Args:
            web_driver (WebDriver): The web driver to use for navigation
        """
        self.web_driver = web_driver

    def extract_links(
        self, url: str, filter_empty: bool = True
    ) -> list[tuple[str, str]]:
        """
        Extract all links from a web page.

        Args:
            url (str): The URL to extract links from
            filter_empty (bool): Whether to filter out empty text or href values

        Returns:
            List[Tuple[str, str]]: List of (text, href) tuples
        """
        source = self.web_driver.get_page_source(url)
        soup = BeautifulSoup(source, "html.parser")
        links = soup.find_all("a")

        link_list: list[tuple[str, str]] = []
        for link in links:
            if not isinstance(link, Tag):
                continue

            text = link.get_text(strip=True)
            href = link.get("href")

            if filter_empty and (not href or not text):
                continue

            if href == "#":
                continue

            # Ensure href is a string
            if isinstance(href, str):
                # Make sure href is absolute
                href = urljoin(url, href)
                link_list.append((text, href))

        return link_list

    def extract_links_by_selector(
        self, url: str, selector: str
    ) -> list[tuple[str, str]]:
        """
        Extract links matching a specific CSS selector.

        Args:
            url (str): The URL to extract links from
            selector (str): CSS selector to filter links

        Returns:
            List[Tuple[str, str]]: List of (text, href) tuples
        """
        source = self.web_driver.get_page_source(url)
        soup = BeautifulSoup(source, "html.parser")
        links = soup.select(selector)

        link_list: list[tuple[str, str]] = []
        for link in links:
            if not isinstance(link, Tag):
                continue

            text = link.get_text(strip=True)
            href = link.get("href")

            if href and text and href != "#" and isinstance(href, str):
                href = urljoin(url, href)
                link_list.append((text, href))

        return link_list


class SearchEngine:
    """Class for performing search operations using Selenium."""

    def __init__(self, web_driver: WebDriver):
        """
        Initialize with a web driver instance.

        Args:
            web_driver (WebDriver): The web driver to use for search operations
        """
        self.web_driver = web_driver

    def google_search(
        self, query: str, search_url: str = "https://www.google.com"
    ) -> str | None:
        """
        Perform a Google search and click the first result.

        Args:
            query (str): The search query
            search_url (str): The search engine URL (default: Google)

        Returns:
            Optional[str]: The title of the first result page, or None if failed
        """
        try:
            # Navigate to search engine
            self.web_driver.driver.get(search_url)

            # Find search box and perform search
            search_box = WebDriverWait(
                self.web_driver.driver, self.web_driver.timeout
            ).until(EC.presence_of_element_located((By.NAME, "q")))
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)

            # Wait for results and click first result
            first_result = WebDriverWait(
                self.web_driver.driver, self.web_driver.timeout
            ).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "h3")))
            first_result.click()

            # Wait for page to load and return title
            WebDriverWait(self.web_driver.driver, self.web_driver.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "title"))
            )

            return self.web_driver.driver.title

        except (TimeoutException, NoSuchElementException) as e:
            print(f"Search failed: {e}")
            return None

    def search_and_extract_results(
        self, query: str, max_results: int = 10
    ) -> list[tuple[str, str]]:
        """
        Perform a search and extract result links without clicking them.

        Args:
            query (str): The search query
            max_results (int): Maximum number of results to extract

        Returns:
            List[Tuple[str, str]]: List of (title, url) tuples
        """
        try:
            # Navigate to Google
            self.web_driver.driver.get("https://www.google.com")

            # Perform search
            search_box = WebDriverWait(
                self.web_driver.driver, self.web_driver.timeout
            ).until(EC.presence_of_element_located((By.NAME, "q")))
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)

            # Wait for results
            WebDriverWait(self.web_driver.driver, self.web_driver.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h3"))
            )

            # Extract results
            results = []
            result_elements = self.web_driver.driver.find_elements(
                By.CSS_SELECTOR, "h3"
            )[:max_results]

            for element in result_elements:
                try:
                    title = element.text
                    link_element = element.find_element(By.XPATH, "./..")
                    url = link_element.get_attribute("href")
                    if title and url:
                        results.append((title, url))
                except Exception:
                    continue

            return results

        except (TimeoutException, NoSuchElementException) as e:
            print(f"Search failed: {e}")
            return []


class WebScraper:
    """Main web scraper class combining link extraction and search functionality."""

    def __init__(self, headless: bool = False, timeout: int = 10):
        """
        Initialize the web scraper.

        Args:
            headless (bool): Whether to run browser in headless mode
            timeout (int): Default timeout for operations
        """
        self.web_driver = WebDriver(headless=headless, timeout=timeout)
        self.link_extractor = LinkExtractor(self.web_driver)
        self.search_engine = SearchEngine(self.web_driver)

    def scrape_links(self, url: str) -> list[tuple[str, str]]:
        """
        Scrape all links from a URL.

        Args:
            url (str): The URL to scrape

        Returns:
            List[Tuple[str, str]]: List of (text, href) tuples
        """
        return self.link_extractor.extract_links(url)

    def search_and_click_first(self, query: str) -> str | None:
        """
        Search for a query and click the first result.

        Args:
            query (str): The search query

        Returns:
            Optional[str]: The title of the result page
        """
        return self.search_engine.google_search(query)

    def close(self) -> None:
        """Close the web driver."""
        self.web_driver.quit()

    def __enter__(self) -> "WebScraper":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


# Example usage functions
def demo_link_extraction():
    """Demonstrate link extraction functionality."""
    with WebScraper(headless=False) as scraper:
        url = "https://50safe.pl/"
        links = scraper.scrape_links(url)

        print(f"Found {len(links)} links on {url}:")
        for text, href in links[:10]:  # Show first 10 links
            print(f"  {text}: {href}")


def demo_search():
    """Demonstrate search functionality."""
    with WebScraper(headless=False) as scraper:
        query = "site:openai.com ChatGPT"
        result_title = scraper.search_and_click_first(query)

        if result_title:
            print(f"Successfully navigated to: {result_title}")
        else:
            print("Search failed")


if __name__ == "__main__":
    # Run demonstrations
    print("=== Link Extraction Demo ===")
    demo_link_extraction()

    print("\n=== Search Demo ===")
    demo_search()
