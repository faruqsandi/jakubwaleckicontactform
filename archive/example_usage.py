"""
Example usage of the web_scraper module.

This file demonstrates how to use the refactored web scraper functionality.
"""

from web_scraper import WebScraper, WebDriver, LinkExtractor, SearchEngine


def main():
    """Main function demonstrating various web scraper functionalities."""

    # Example 1: Using the high-level WebScraper class
    print("=== Example 1: Using WebScraper class ===")
    try:
        with WebScraper(headless=False) as scraper:
            # Extract links from a website
            url = "https://50safe.pl/"
            print(f"Extracting links from {url}...")

            links = scraper.scrape_links(url)
            print(f"Found {len(links)} links:")

            # Display first 5 links
            for i, (text, href) in enumerate(links[:5], 1):
                print(f"  {i}. {text}: {href}")

            if len(links) > 5:
                print(f"  ... and {len(links) - 5} more links")

    except Exception as e:
        print(f"Error in Example 1: {e}")

    # Example 2: Using individual components
    print("\n=== Example 2: Using individual components ===")
    try:
        with WebDriver(headless=False) as driver:
            # Create link extractor
            extractor = LinkExtractor(driver)

            # Extract links with custom filtering
            url = "https://httpbin.org/"
            print(f"Extracting links from {url}...")

            links = extractor.extract_links(url, filter_empty=True)
            print(f"Found {len(links)} links:")

            for i, (text, href) in enumerate(links[:3], 1):
                print(f"  {i}. {text}: {href}")

    except Exception as e:
        print(f"Error in Example 2: {e}")

    # Example 3: Search functionality (commented out to avoid Google automation detection)
    print("\n=== Example 3: Search functionality (disabled for demo) ===")
    print("Search functionality is available but disabled in this demo")
    print("to avoid Google's automation detection.")

    """
    # Uncomment to test search functionality (use responsibly)
    try:
        with WebScraper(headless=False) as scraper:
            query = "python selenium tutorial"
            print(f"Searching for: {query}")
            
            result_title = scraper.search_and_click_first(query)
            if result_title:
                print(f"Successfully navigated to: {result_title}")
            else:
                print("Search failed")
    
    except Exception as e:
        print(f"Error in Example 3: {e}")
    """


if __name__ == "__main__":
    main()
