"""
Contact form detection module.

This module provides functionality for detecting contact forms on websites,
including CRUD operations for storing and managing detection results.
"""

from .models import ContactFormDetection
from .crud import (
    ContactFormDetectionCRUD,
    create_detection,
    get_detection,
    update_detection,
    delete_detection,
)

from .gemini import get_form_information, select_contact_url, find_success_message

__all__ = [
    "ContactFormDetection",
    "ContactFormDetectionCRUD",
    "create_detection",
    "get_detection",
    "update_detection",
    "delete_detection",
    "get_form_information",
    "select_contact_url",
    "find_success_message",
]
