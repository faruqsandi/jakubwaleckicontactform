"""
Contact form detection module.

This module provides functionality for detecting contact forms on websites,
including CRUD operations for storing and managing detection results.
"""

from .models import ContactFormDetection
from .crud import (
    ContactFormDetectionCRUD,
)

from .gemini import get_form_information, select_contact_url, find_success_message
from .selenium_handler import search_domain_form

__all__ = [
    "ContactFormDetection",
    "ContactFormDetectionCRUD",
    "get_form_information",
    "select_contact_url",
    "find_success_message",
    "search_domain_form",
]
