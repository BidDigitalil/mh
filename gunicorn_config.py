import multiprocessing
import os

# Binding
bind = "...:8"

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"

# Logging
errorlog = '/var/log/treatment_center/gunicorn_error.log'
accesslog = '/var/log/treatment_center/gunicorn_access.log'
loglevel = 'debug'
capture_output = True

# Timeouts
timeout = 12
keepalive = 5

# Process Name
proc_name = "treatment_center"

# Additional Worker Settings
max_requests = 1
max_requests_jitter = 5

# Additional Gunicorn settings
forwarded_allow_ips = '*'  # Allow all IPs to set forwarded headers
