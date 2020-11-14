#!/usr/bin/env python
import os
import sys

import dotenv
from sentry_sdk import capture_exception

if __name__ == "__main__":
    try:
        dotenv.read_dotenv()
    except Exception as read_env_fail:
        capture_exception(read_env_fail)
        print("Could not read .env file")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        capture_exception(exc)
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
    execute_from_command_line(sys.argv)
