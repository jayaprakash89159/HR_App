"""
WorkSphere HR - Gunicorn Configuration
Production WSGI server settings - EC2 Ubuntu optimized
"""
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Workers: on a t2/t3.micro use 2-3 workers, not cpu*2+1 (OOM risk)
# Auto-detect: small EC2 gets 3 workers, larger gets cpu*2+1
cpu_count = multiprocessing.cpu_count()
workers = min(cpu_count * 2 + 1, 4)  # Cap at 4 for EC2 free tier safety

worker_class = "sync"
worker_connections = 1000
timeout = 120        # Django startup can be slow on first request
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Restart workers gracefully
graceful_timeout = 30
preload_app = True   # Saves memory by sharing app code across workers

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = "worksphere_hr"

def worker_exit(server, worker):
    pass

def on_starting(server):
    server.log.info("WorkSphere HR starting up...")

def on_exit(server):
    server.log.info("WorkSphere HR shutting down...")
