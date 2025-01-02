#!/bin/bash

echo "=== Comprehensive Django and Gunicorn Debugging ==="

echo -e "\n--- Gunicorn Service Status ---"
systemctl status treatment_center.service

echo -e "\n--- Gunicorn Processes ---"
ps aux | grep gunicorn

echo -e "\n--- Listening Ports ---"
netstat -tuln | grep 8

echo -e "\n--- Gunicorn Error Log (Last 5 lines) ---"
tail -n 5 /var/log/treatment_center/gunicorn_error.log

echo -e "\n--- Gunicorn Access Log (Last 5 lines) ---"
tail -n 5 /var/log/treatment_center/gunicorn_access.log

echo -e "\n--- System Journal for Gunicorn (Last 5 lines) ---"
journalctl -u treatment_center.service -n 5

echo -e "\n--- Django Project Verification ---"
cd /home/mh.bigdigital.co.il/public_html/treatment_center1
source venv/bin/activate
python3 manage.py check

echo -e "\n--- Network Configuration ---"
ip addr show
netstat -tuln

