#!/usr/bin/env python
"""
Django Development Server Runner with SSL Certificate Bypass
Handles SSL certificate verification issues for API calls
"""

import os
import sys
import ssl
import urllib3

# CRITICAL: Set these BEFORE importing Django or any API libraries
os.environ['GRPC_DEFAULT_SSL_ROOTS_FILE_PATH'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['PYTHONHTTPSVERIFY'] = '0'

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Monkey patch ssl module BEFORE anything imports it
_original_create_context = ssl.create_default_context

def _create_unverified_context(*args, **kwargs):
    context = _original_create_context(*args, **kwargs)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

ssl.create_default_context = _create_unverified_context
ssl._create_unverified_context = _create_unverified_context

# Disable certificate warnings from libraries
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TBZBlogs.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Run the development server
    execute_from_command_line(sys.argv)
