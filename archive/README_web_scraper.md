# Web Scraper Module

A Python module for web scraping using Selenium and BeautifulSoup, refactored from the original `seleniumtemp.py` script.

## Features

- **Modular Design**: Separated into different classes for specific functionality
- **Context Manager Support**: Automatic browser cleanup
- **Type Hints**: Full type annotation support
- **Error Handling**: Robust error handling with proper exception management
- **Flexible Link Extraction**: Extract all links or filter by CSS selectors
- **Search Functionality**: Automated search operations (use responsibly)

## Classes

### `WebDriver`
Base class for managing Chrome browser instances with automatic chromedriver installation.

**Key Features:**
- Automatic chromedriver installation (if `chromedriver_autoinstaller` is available)
- Headless mode support
- Context manager support for automatic cleanup
- Configurable timeout settings

### `LinkExtractor`
Specialized class for extracting links from web pages.

**Methods:**
- `extract_links(url, filter_empty=True)`: Extract all links from a webpage
- `extract_links_by_selector(url, selector)`: Extract links matching CSS selector

### `SearchEngine`
Class for performing automated search operations.

**Methods:**
- `google_search(query, search_url)`: Perform search and click first result
- `search_and_extract_results(query, max_results)`: Extract search results without clicking

### `WebScraper`
High-level class that combines all functionality.

**Methods:**
- `scrape_links(url)`: Simple link extraction
- `search_and_click_first(query)`: Search and navigate to first result
- Context manager support for automatic cleanup

## Installation

Required dependencies:
```bash
pip install selenium beautifulsoup4 chromedriver-autoinstaller
```

## Usage Examples

### Basic Link Extraction
```python
from web_scraper import WebScraper

# Using context manager (recommended)
with WebScraper(headless=False) as scraper:
    links = scraper.scrape_links("https://example.com")
    for text, href in links:
        print(f"{text}: {href}")
```

### Advanced Usage with Individual Components
```python
from web_scraper import WebDriver, LinkExtractor

with WebDriver(headless=True, timeout=15) as driver:
    extractor = LinkExtractor(driver)
    
    # Extract all links
    all_links = extractor.extract_links("https://example.com")
    
    # Extract only navigation links
    nav_links = extractor.extract_links_by_selector(
        "https://example.com", 
        "nav a"
    )
```

### Search Operations (Use Responsibly)
```python
from web_scraper import WebScraper

with WebScraper() as scraper:
    # Search and click first result
    result_title = scraper.search_and_click_first("python tutorial")
    print(f"Navigated to: {result_title}")
```

## Configuration Options

- `headless`: Run browser in headless mode (default: False)
- `timeout`: Default timeout for web operations (default: 10 seconds)

## Error Handling

The module includes proper error handling for common scenarios:
- Network timeouts
- Element not found
- Browser automation detection
- Invalid URLs

## Migration from Original Script

The original `seleniumtemp.py` script has been refactored into this modular structure:

**Original Script Functionality → New Module**
- Direct browser instantiation → `WebDriver` class
- Inline link extraction → `LinkExtractor.extract_links()`
- Search operations → `SearchEngine.google_search()`
- Mixed functionality → `WebScraper` high-level interface

## Best Practices

1. **Use Context Managers**: Always use `with` statements for automatic cleanup
2. **Respect Rate Limits**: Add delays between requests to avoid being blocked
3. **Handle Exceptions**: Wrap operations in try-catch blocks
4. **Use Headless Mode**: For production scripts, use headless mode
5. **Be Respectful**: Follow website robots.txt and terms of service

## Notes

- The module automatically installs chromedriver if `chromedriver_autoinstaller` is available
- Search functionality should be used responsibly to avoid violating terms of service
- Some websites may detect and block automated access

## Example Files

- `example_usage.py`: Demonstrates basic usage patterns
- `web_scraper.py`: Main module file

Run the example:
```bash
python example_usage.py
```
