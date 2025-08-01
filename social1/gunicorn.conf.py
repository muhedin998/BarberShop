# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Process naming
proc_name = 'social1'

# User and group
user = "www-data"
group = "www-data"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Enable preload_app for better memory usage
preload_app = True

# Restart workers gracefully on code changes
reload = False

# Enable worker recycling for memory leaks
max_requests_jitter = 10

# Environment variables
env = [
    'DJANGO_SETTINGS_MODULE=social1.settings',
]