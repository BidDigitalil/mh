#!/bin/bash

echo "=== System Configuration Debugging ==="

echo -e "\n--- Python and Virtual Environment ---"
which python3
python3 --version
echo "Virtual Env: $VIRTUAL_ENV"

echo -e "\n--- Django Project Details ---"
echo "Project Directory: $(pwd)"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

echo -e "\n--- Gunicorn Service Status ---"
systemctl status treatment_center.service

echo -e "\n--- Network Listening Ports ---"
netstat -tuln | grep LISTEN

echo -e "\n--- Gunicorn Error Log (Last 20 lines) ---"
tail -n 20 /var/log/treatment_center/gunicorn_error.log

echo -e "\n--- Gunicorn Access Log (Last 20 lines) ---"
tail -n 20 /var/log/treatment_center/gunicorn_access.log

echo -e "\n--- Django Settings Check ---"
python3 -c "
import os
import sys
sys.path.append('$(pwd)')
os.environ['DJANGO_SETTINGS_MODULE'] = 'treatment_center.settings'
from django.conf import settings

print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)
print('DEBUG:', settings.DEBUG)
print('STATIC_URL:', settings.STATIC_URL)
print('MEDIA_URL:', settings.MEDIA_URL)
"
