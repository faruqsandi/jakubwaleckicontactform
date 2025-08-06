# ContactFormDetection CRUD Operations

This module provides comprehensive CRUD (Create, Read, Update, Delete) operations for the `ContactFormDetection` model, which stores information about contact forms detected on websites.

## Features

- **Full CRUD Operations**: Create, read, update, and delete contact form detection records
- **Advanced Querying**: Search by domain, URL, status, anti-bot protection, and more
- **Bulk Operations**: Delete multiple records by domain
- **Pagination Support**: Retrieve records with skip/limit parameters
- **Search Functionality**: Full-text search across multiple fields
- **Status Management**: Track detection status (pending, completed, failed, etc.)
- **Type Safety**: Full type annotations for better IDE support

## Quick Start

### Basic Usage

```python
from sqlalchemy.orm import Session
from contactform.detection import ContactFormDetectionCRUD, create_detection

# Create a new detection record
detection = create_detection(
    db=db_session,
    domain_name="example.com",
    form_url="https://example.com/contact",
    contact_form_present=True,
    form_antibot_type="recaptcha",
    form_fields=["name", "email", "message"],
    field_selectors={
        "name": "#contact-name",
        "email": "#contact-email",
        "message": "#contact-message"
    },
    detection_status="completed"
)

# Retrieve a detection by ID
detection = ContactFormDetectionCRUD.get_by_id(db_session, detection_id)

# Update a detection
updated = ContactFormDetectionCRUD.update(
    db_session, 
    detection_id, 
    detection_status="verified",
    form_antibot_type="hcaptcha"
)

# Delete a detection
deleted = ContactFormDetectionCRUD.delete(db_session, detection_id)
```

## Available Operations

### Create Operations

- `create()` - Create a new detection record
- `create_detection()` - Convenience function for creating records

### Read Operations

- `get_by_id(id)` - Get record by primary key
- `get_by_domain(domain)` - Get all records for a specific domain
- `get_by_url(url)` - Get record by form URL
- `get_all()` - Get all records with pagination
- `get_by_status(status)` - Get records by detection status
- `get_with_contact_forms()` - Get records where contact forms are present
- `get_with_antibot_protection(level)` - Get records with anti-bot protection
- `search(term, fields)` - Search across specified fields

### Update Operations

- `update(id, **data)` - Update any fields of a record
- `update_status(id, status)` - Update only the detection status

### Delete Operations

- `delete(id)` - Delete a single record
- `delete_by_domain(domain)` - Delete all records for a domain

### Count Operations

- `count_all()` - Count total records
- `count_by_status(status)` - Count records by status
- `count_by_domain(domain)` - Count records for a domain

## Advanced Usage

### Pagination

```python
# Get first 20 records, ordered by detection date (newest first)
detections = ContactFormDetectionCRUD.get_all(
    db_session, 
    skip=0, 
    limit=20, 
    order_by="detection_date", 
    order_direction="desc"
)
```

### Anti-bot Protection Filtering

```python
# Get records with any anti-bot protection
any_antibot = ContactFormDetectionCRUD.get_with_antibot_protection(
    db_session, level="any"
)

# Get records with both website and form anti-bot protection
both_antibot = ContactFormDetectionCRUD.get_with_antibot_protection(
    db_session, level="both"
)

# Get records with only website-level protection
website_antibot = ContactFormDetectionCRUD.get_with_antibot_protection(
    db_session, level="website"
)
```

### Search Operations

```python
# Search in domain names and URLs
results = ContactFormDetectionCRUD.search(
    db_session,
    search_term="contact",
    search_fields=["domain_name", "form_url"],
    limit=50
)

# Search only in domain names
results = ContactFormDetectionCRUD.search(
    db_session,
    search_term="example.com",
    search_fields=["domain_name"]
)
```

### Bulk Operations

```python
# Count records for a domain before deletion
count = ContactFormDetectionCRUD.count_by_domain(db_session, "old-site.com")
print(f"Found {count} records")

# Delete all records for a domain
deleted_count = ContactFormDetectionCRUD.delete_by_domain(db_session, "old-site.com")
print(f"Deleted {deleted_count} records")
```

## Model Fields

The `ContactFormDetection` model includes the following fields:

### Required Fields
- `domain_name` - The domain where the form was detected
- `form_url` - The URL where the form was found

### Form Detection Fields
- `contact_form_present` - Whether a contact form is present
- `form_fields` - List of form field names (JSON array)
- `field_selectors` - CSS selectors for form fields (JSON object)
- `submit_button_selector` - CSS selector for the submit button
- `form_action` - Form action URL

### Anti-bot Detection Fields
- `website_antibot_detection` - Anti-bot protection at website level
- `form_antibot_detection` - Anti-bot protection at form level
- `form_antibot_type` - Type of protection (recaptcha, hcaptcha, etc.)

### Metadata Fields
- `detection_status` - Status of detection (pending, completed, failed)
- `detection_date` - When the detection was first recorded
- `last_updated` - When the record was last modified

## Error Handling

All CRUD operations include proper error handling:

```python
# Safe retrieval
detection = ContactFormDetectionCRUD.get_by_id(db_session, 999)
if detection is None:
    print("Detection not found")

# Safe update
updated = ContactFormDetectionCRUD.update(db_session, 999, status="completed")
if updated is None:
    print("Detection not found for update")

# Safe deletion
deleted = ContactFormDetectionCRUD.delete(db_session, 999)
if not deleted:
    print("Detection not found for deletion")
```

## Testing

The module includes comprehensive unit tests in `test_crud.py`. Run them with:

```bash
pytest contactform/detection/test_crud.py -v
```

## Examples

See `examples.py` for detailed usage examples and demonstrations of all CRUD operations.

## Integration

To use this CRUD module in your application:

1. Import the necessary components:
```python
from contactform.detection import ContactFormDetectionCRUD, create_detection
```

2. Set up your database session according to your application's configuration

3. Use the CRUD operations as needed in your application logic

The CRUD operations are designed to be used with SQLAlchemy sessions and follow standard database transaction patterns.
