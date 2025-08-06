#!/usr/bin/env python3
"""
Test script to verify the mission CRUD functionality and Flask app integration.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contactform.mission import create_mission, get_all_missions, get_mission, update_mission, delete_mission, create_tables

def test_mission_crud():
    """Test all CRUD operations for Mission"""
    
    print("Testing Mission CRUD operations...")
    
    # Initialize database tables
    try:
        create_tables()
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False
    
    # Test Create
    try:
        mission = create_mission(
            "Test Marketing Campaign",
            {
                "name": "Test Marketing Campaign",
                "email": "test@example.com",
                "message": "This is a test message for marketing campaign",
                "phone": "+1234567890",
                "company": "Test Company"
            }
        )
        print(f"✓ Mission created: ID={mission.id}, Name={mission.pre_defined_fields.get('name')}")
    except Exception as e:
        print(f"✗ Error creating mission: {e}")
        return False
    
    # Test Read All
    try:
        all_missions = get_all_missions()
        print(f"✓ Retrieved {len(all_missions)} missions")
    except Exception as e:
        print(f"✗ Error getting all missions: {e}")
        return False
    
    # Test Read One
    try:
        retrieved_mission = get_mission(mission.id)
        if retrieved_mission:
            print(f"✓ Retrieved mission: {retrieved_mission.pre_defined_fields.get('name')}")
        else:
            print("✗ Mission not found")
            return False
    except Exception as e:
        print(f"✗ Error getting mission: {e}")
        return False
    
    # Test Update
    try:
        updated_mission = update_mission(
            mission.id,
            "Updated Marketing Campaign",
            {
                "name": "Updated Marketing Campaign",
                "email": "updated@example.com",
                "message": "Updated message",
                "phone": "+0987654321",
                "company": "Updated Company"
            }
        )
        if updated_mission:
            print(f"✓ Mission updated: {updated_mission.pre_defined_fields.get('name')}")
        else:
            print("✗ Mission update failed")
            return False
    except Exception as e:
        print(f"✗ Error updating mission: {e}")
        return False
    
    # Test Delete
    try:
        delete_result = delete_mission(mission.id)
        if delete_result:
            print("✓ Mission deleted successfully")
        else:
            print("✗ Mission deletion failed")
            return False
    except Exception as e:
        print(f"✗ Error deleting mission: {e}")
        return False
    
    print("All CRUD tests passed! ✓")
    return True

def test_flask_app_import():
    """Test that the Flask app can be imported successfully"""
    try:
        from app.app import app
        print("✓ Flask app imported successfully")
        print(f"✓ Registered blueprints: {[bp.name for bp in app.blueprints.values()]}")
        return True
    except Exception as e:
        print(f"✗ Error importing Flask app: {e}")
        return False

if __name__ == "__main__":
    print("=== Contact Form Manager Test Suite ===\n")
    
    crud_test = test_mission_crud()
    print()
    
    flask_test = test_flask_app_import()
    print()
    
    if crud_test and flask_test:
        print("🎉 All tests passed! The application is ready to use.")
        print("\nTo run the Flask app:")
        print("python app/app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
