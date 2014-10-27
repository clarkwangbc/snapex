#!/usr/bin/env python
import os
import sys

sys.path.insert(1, '/Users/Yuming/Codes/BAE/appid282gcboc93')

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snapex.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
