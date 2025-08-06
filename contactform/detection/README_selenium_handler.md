# Selenium Form Detection Handler

This module provides a comprehensive solution for detecting contact forms on websites using Selenium WebDriver and AI-powered analysis.

## Overview

The `search_domain_form` function automates the process of:
1. Navigating to a domain
2. Finding contact pages
3. Detecting contact forms and their properties
4. Analyzing anti-bot protection mechanisms
5. Updating the database with results

## Main Function

### `search_domain_form(domain: str, db_session: Optional[Session] = None) -> ContactFormDetection`

**Parameters:**
- `domain`: Domain name to search (e.g., "example.com" or "https://example.com")
- `db_session`: Optional database session. If not provided, a new session will be created

**Returns:**
- `ContactFormDetection`: Database record with detection results

**Raises:**
- `ValueError`: If domain is invalid
- `WebDriverException`: If selenium operations fail
- `RuntimeError`: For database or other unexpected errors

## Features

### 1. Comprehensive Form Detection
- Finds contact pages using AI-powered link analysis
- Detects form fields (name, email, message, telephone, etc.)
- Identifies submit buttons and form actions
- Extracts CSS selectors for all form elements

### 2. Anti-Bot Protection Detection
- Detects reCAPTCHA, hCAPTCHA, Cloudflare Turnstile
- Identifies website-level and form-level protection
- Supports custom anti-bot mechanisms

### 3. Robust Error Handling
- Graceful fallback when AI analysis fails
- Proper cleanup of WebDriver resources
- Database transaction management
- Detailed logging for debugging

### 4. Database Integration
- Creates or updates ContactFormDetection records
- Tracks detection status (pending → in_progress → completed/failed)
- Stores comprehensive form metadata

## Usage Examples

### Basic Usage
```python
from contactform.detection.selenium_handler import search_domain_form

# Detect forms on a single domain
result = search_domain_form("example.com")

print(f"Form found: {result.contact_form_present}")
print(f"Form URL: {result.form_url}")
print(f"Fields: {result.form_fields}")
```

### With Existing Database Session
```python
from contactform.mission.crud import get_db
from contactform.detection.selenium_handler import search_domain_form

db = get_db()
try:
    result = search_domain_form("example.com", db)
    # Use result...
finally:
    db.close()
```

### Batch Processing
```python
from contactform.detection.selenium_handler import batch_search_domain_forms

domains = ["example.com", "test.com", "demo.org"]
results = batch_search_domain_forms(domains)

for result in results:
    print(f"{result.domain_name}: {result.contact_form_present}")
```

## Database Schema

The function works with the `ContactFormDetection` model:

```python
class ContactFormDetection:
    domain_name: str                    # Domain name
    form_url: str                      # URL where form was found
    contact_form_present: bool         # Whether form exists
    
    # Anti-bot protection
    website_antibot_detection: bool    # Site-level protection
    form_antibot_detection: bool       # Form-level protection
    form_antibot_type: str            # Type (recaptcha, hcaptcha, etc.)
    
    # Form structure
    form_fields: list[str]            # Field types found
    field_selectors: dict[str, str]   # CSS selectors for fields
    submit_button_selector: str       # Submit button selector
    form_action: str                  # Form action URL
    
    # Status tracking
    detection_status: str             # pending/in_progress/completed/failed
    detection_date: datetime          # When detection started
    last_updated: datetime           # Last update time
```

## Configuration

### WebDriver Options
The function automatically configures Chrome with these options:
- Headless mode by default
- No sandbox mode for server environments
- Disabled dev-shm-usage for stability
- Custom user agent
- 30-second page load timeout

### AI Integration
Uses Google Gemini for:
- Contact page selection from available links
- Form field detection and classification
- Anti-bot protection analysis

## Error Handling

The function handles various error scenarios:

1. **Invalid Domain**: Returns `ValueError` for malformed domains
2. **Network Issues**: Selenium exceptions for connection problems
3. **Page Loading**: Timeout handling for slow-loading pages
4. **AI Failures**: Fallback to heuristic methods when AI analysis fails
5. **Database Errors**: Proper transaction rollback and error reporting

## Logging

Enable logging to see detailed operation progress:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

Log levels:
- INFO: Progress updates and successful operations
- WARNING: Non-critical issues (AI fallbacks, missing elements)
- ERROR: Critical failures requiring attention

## Dependencies

Required packages:
- `selenium`: Web automation
- `chromedriver-autoinstaller`: Automatic ChromeDriver management
- `beautifulsoup4`: HTML parsing
- `sqlalchemy`: Database operations
- `google-genai`: AI-powered analysis

## Performance Considerations

- Each domain analysis takes 10-30 seconds depending on site complexity
- Use batch processing for multiple domains to optimize database connections
- Consider running in background tasks for large datasets
- WebDriver resources are automatically cleaned up

## Celery Integration Ready

The function is designed to be easily converted to a Celery task:

```python
from celery import Celery

app = Celery('form_detection')

@app.task
def detect_domain_form_task(domain: str) -> dict:
    result = search_domain_form(domain)
    return {
        'domain': result.domain_name,
        'form_found': result.contact_form_present,
        'status': result.detection_status
    }
```

## Troubleshooting

### Common Issues

1. **ChromeDriver Not Found**: Ensure `chromedriver-autoinstaller` can download the driver
2. **Permission Errors**: Run with appropriate system permissions for driver installation
3. **Memory Issues**: Consider running in headless mode and limiting concurrent operations
4. **AI API Limits**: Handle rate limiting and implement retry logic if needed

### Debug Mode

For development, disable headless mode:

```python
# Modify setup_webdriver function
driver = setup_webdriver(headless=False)
```

This allows you to see the browser actions in real-time.
