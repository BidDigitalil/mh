"""
Script to change the password for a user in the treatment center management system.

This script provides a command-line interface to change a user's password.
It uses Django's authentication system to update the user's credentials.

Usage:
    python change_password.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treatment_center.settings')
django.setup()

from treatment_app.models import User
from django.contrib.auth.hashers import make_password

# עדכון סיסמה למשתמש admin
user = User.objects.get(username='admin')
user.password = make_password('Admin123!')
user.save()

print("הסיסמה עודכנה בהצלחה")
