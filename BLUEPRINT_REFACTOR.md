# Contact Form Manager - Refactored with Blueprints and CRUD

This project has been refactored to use Flask Blueprints for better organization and includes a complete CRUD system for mission management using SQLAlchemy.

## New Architecture

### Mission CRUD Module (`contactform/mission/`)
- **`models.py`**: SQLAlchemy Mission model
- **`crud.py`**: Complete CRUD operations for missions
- **`__init__.py`**: Easy imports for mission functionality

### Flask Blueprints (`app/blueprints/`)
- **`mission.py`**: Mission-related routes (list, create, select)
- **`config.py`**: Configuration routes (CSV upload, settings)
- **`forms.py`**: Form detection routes
- **`submission.py`**: Form submission routes

### Main Application (`app/app.py`)
- Simplified main app file
- Blueprint registration
- Database initialization

## Key Features

### Mission Management
- **Create Mission**: Store missions with pre-defined form fields
- **List Missions**: View all missions with database integration
- **Select Mission**: Choose a mission for the current workflow
- **Update/Delete**: Full CRUD operations available

### Database Integration
- SQLAlchemy models with proper relationships
- Automatic table creation
- Proper session management
- Error handling and fallbacks

### Blueprint Organization
- **Mission Blueprint** (`/mission/`):
  - `GET /mission/` - List all missions
  - `GET,POST /mission/create` - Create new mission
  - `GET /mission/<id>/select` - Select mission
  
- **Config Blueprint** (`/config/`):
  - `GET /config/` - Configuration page
  - `POST /config/upload_csv` - CSV upload
  - `GET /config/clear_csv` - Clear CSV data
  
- **Forms Blueprint** (`/forms/`):
  - `GET /forms/missing` - Missing forms page
  - `POST /forms/get_forms` - Get form information
  
- **Submission Blueprint** (`/submission/`):
  - `GET /submission/config` - Submission configuration
  - `POST /submission/save_config` - Save configuration
  - `GET /submission/process` - Process submissions
  - `POST /submission/submit_forms` - Submit forms

## Usage

### Running the Application
```bash
# Test the setup
python test_setup.py

# Run the Flask app
python app/app.py
```

### Using the Mission CRUD
```python
from contactform.mission import create_mission, get_all_missions, get_mission

# Create a new mission
mission = create_mission("My Campaign", {
    "name": "My Campaign",
    "email": "test@example.com",
    "message": "Hello world",
    "phone": "123-456-7890",
    "company": "My Company"
})

# Get all missions
missions = get_all_missions()

# Get specific mission
mission = get_mission(mission_id)
```

### Database Schema
The Mission model includes:
- `id`: Primary key
- `pre_defined_fields`: JSON field storing form field values
- `created_date`: Auto-generated creation timestamp
- `last_updated`: Auto-updated modification timestamp
- `form_submissions`: Relationship to FormSubmission model

## Benefits of Refactoring

1. **Better Organization**: Each blueprint handles specific functionality
2. **Scalability**: Easy to add new features without cluttering main app
3. **Database Integration**: Real mission storage instead of sample data
4. **Maintainability**: Clear separation of concerns
5. **Reusability**: CRUD functions can be used from CLI or other interfaces
6. **Type Safety**: Proper type annotations throughout
7. **Error Handling**: Graceful fallbacks when database is unavailable

## Next Steps

The application is now ready for:
1. Enhanced form detection logic
2. Real CSV processing
3. Form submission automation
4. User authentication
5. Mission templates
6. Bulk operations
7. Reporting and analytics

All the infrastructure is in place to support these advanced features.
