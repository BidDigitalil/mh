"""
Script to create a new user in the treatment center management system.

This script provides a command-line interface to create a new user with 
specified details, including username, email, and password.

Usage:
    python create_user.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treatment_center.settings')
django.setup()

from django.contrib.auth.models import User

# יצירת משתמש מנהל חדש
username = 'admin'
email = 'admin@example.com'
password = 'Admin123!'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'משתמש מנהל {username} נוצר בהצלחה')
else:
    print(f'משתמש {username} כבר קיים')
