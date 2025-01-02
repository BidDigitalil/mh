#!/bin/bash

cd /home/mh.bigdigital.co.il/public_html/treatment_center1
source venv/bin/activate

# Manually start Gunicorn with verbose logging
gunicorn \
    --config gunicorn_config.py \
    --log-level=debug \
    --capture-output \
    treatment_center.wsgi:application
