"""
Pytest configuration for Django project.
Reference: https://pytest-django.readthedocs.io/
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TBZBlogs.settings')

django.setup()
