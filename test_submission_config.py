#!/usr/bin/env python3
"""
Simple test to verify the submission config functionality works correctly.
"""

from app.blueprints.submission import _determine_field_type, _determine_if_required
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_field_type_determination():
    """Test field type determination logic."""
    print("Testing field type determination...")

    # Test email fields
    assert _determine_field_type("email") == "email"
    assert _determine_field_type("user_email") == "email"
    assert _determine_field_type("EMAIL_ADDRESS") == "email"

    # Test phone fields
    assert _determine_field_type("phone") == "tel"
    assert _determine_field_type("telephone") == "tel"
    assert _determine_field_type("tel_number") == "tel"

    # Test textarea fields
    assert _determine_field_type("message") == "textarea"
    assert _determine_field_type("comment") == "textarea"
    assert _determine_field_type("description") == "textarea"

    # Test text fields (default)
    assert _determine_field_type("name") == "text"
    assert _determine_field_type("company") == "text"
    assert _determine_field_type("subject") == "text"

    print("✓ Field type determination tests passed")


def test_required_field_determination():
    """Test required field determination logic."""
    print("Testing required field determination...")

    # Test required fields
    assert _determine_if_required("name") == True
    assert _determine_if_required("email") == True
    assert _determine_if_required("message") == True
    assert _determine_if_required("subject") == True
    assert _determine_if_required("first_name") == True
    assert _determine_if_required("user_email") == True

    # Test optional fields
    assert _determine_if_required("phone") == False
    assert _determine_if_required("company") == False
    assert _determine_if_required("website") == False
    assert _determine_if_required("address") == False

    print("✓ Required field determination tests passed")


def test_form_data_structure():
    """Test the form data structure."""
    print("Testing form data structure...")

    # Simulate what the function would create
    test_fields = ["name", "email", "phone", "message", "company"]
    existing_values = {"name": "John Doe", "email": "john@example.com", "message": "Test message"}

    dynamic_fields = []
    for field_name in sorted(test_fields):
        field_type = _determine_field_type(field_name)
        is_required = _determine_if_required(field_name)

        dynamic_fields.append({
            "name": field_name,
            "type": field_type,
            "required": is_required,
            "value": existing_values.get(field_name, "")
        })

    # Verify the structure
    assert len(dynamic_fields) == 5
    assert dynamic_fields[1]["name"] == "email"  # Should be sorted: company, email, message, name, phone
    assert dynamic_fields[1]["type"] == "email"
    assert dynamic_fields[1]["required"] == True
    assert dynamic_fields[1]["value"] == "john@example.com"

    # Check field with no existing value
    phone_field = next(f for f in dynamic_fields if f["name"] == "phone")
    assert phone_field["value"] == ""
    assert phone_field["type"] == "tel"
    assert phone_field["required"] == False

    print("✓ Form data structure tests passed")


if __name__ == "__main__":
    print("Running submission config tests...\n")

    try:
        test_field_type_determination()
        test_required_field_determination()
        test_form_data_structure()

        print("\n🎉 All tests passed successfully!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
