#!/bin/bash

# Activate virtual environment
cd /home/mh.bigdigital.co.il/public_html/treatment_center1
source venv/bin/activate

# Start Gunicorn
exec venv/bin/gunicorn \
    --config gunicorn_config.py \
    --chdir /home/mh.bigdigital.co.il/public_html/treatment_center1 \
    treatment_center.wsgi:application
