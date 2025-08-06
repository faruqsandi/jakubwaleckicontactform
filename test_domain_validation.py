#!/usr/bin/env python3
"""
Test script to verify domain validation functionality.
"""

from app.blueprints.config import extract_fqdn
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_extract_fqdn():
    """Test the extract_fqdn function with various inputs."""
    test_cases = [
        # (input, expected_domain, expected_valid)
        ("https://example.com/contact", "example.com", True),
        ("testsite.org", "testsite.org", True),
        ("demo.net/form", "demo.net", True),
        ("https://sample.io", "sample.io", True),
        ("contact-form.com/contact-us", "contact-form.com", True),
        ("business-site.net", "business-site.net", True),
        ("www.another-site.com", "www.another-site.com", True),
        ("http://old-site.com/contact/form", "old-site.com", True),
        ("invalidsite", "invalidsite", False),
        ("localhost", "localhost", False),
        ("test", "test", False),
        ("another-invalid", "another-invalid", False),
        ("validsite.co.uk", "validsite.co.uk", True),
        ("sub.domain.com", "sub.domain.com", True),
        ("example.com:8080", "example.com", True),
        ("https://sub.example.co.uk:8080/path/index.html", "sub.example.co.uk", True),
        ("", "", False),
        ("   ", "", False),
    ]

    print("Testing extract_fqdn function:")
    print("=" * 50)

    all_passed = True
    for i, (input_domain, expected_domain, expected_valid) in enumerate(test_cases, 1):
        try:
            result_domain, result_valid = extract_fqdn(input_domain)

            domain_match = result_domain == expected_domain
            valid_match = result_valid == expected_valid

            if domain_match and valid_match:
                status = "✓ PASS"
            else:
                status = "✗ FAIL"
                all_passed = False

            print(f"Test {i:2d}: {status}")
            print(f"  Input:    '{input_domain}'")
            print(f"  Expected: '{expected_domain}', valid={expected_valid}")
            print(f"  Got:      '{result_domain}', valid={result_valid}")

            if not domain_match:
                print(f"  Domain mismatch!")
            if not valid_match:
                print(f"  Validity mismatch!")
            print()

        except Exception as e:
            print(f"Test {i:2d}: ✗ ERROR")
            print(f"  Input:    '{input_domain}'")
            print(f"  Error:    {e}")
            print()
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")

    return all_passed


if __name__ == "__main__":
    success = test_extract_fqdn()
    sys.exit(0 if success else 1)
