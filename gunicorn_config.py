import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
graceful_timeout = 30
keepalive = 2

# Restart workers after this many seconds
max_requests_jitter = 50

# Logging
accesslog = "/var/log/trialssfinder/access.log"
errorlog = "/var/log/trialssfinder/error.log"
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True

# Process naming
proc_name = "trialssfinder"

# Server mechanics
daemon = False
pidfile = "/var/run/trialssfinder.pid"
user = "trialssfinder"
group = "trialssfinder"
tmp_upload_dir = None

# SSL (if not using nginx)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'


# Pre-request hook
def pre_request(worker, req):  # nosec
    worker.log.debug("%s %s" % (req.method, req.path))


# Post-request hook
def post_request(worker, req, environ, resp):  # nosec
    worker.log.debug("%s %s %s" % (req.method, req.path, resp.status))


# Worker timeout
def worker_int(worker):  # nosec
    worker.log.info("worker received INT or QUIT signal")


# Called just after the server is started
def on_starting(server):
    server.log.info("Starting TrialsFinder server")


# Called just before the master process is initialized
def on_reload(server):
    server.log.info("Reloading TrialsFinder server")


# Called just after a worker has been forked
def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)


# Called just before a worker is forked
def pre_fork(server, worker):
    pass


# Called just before a new master process is forked
def when_ready(server):
    server.log.info("Server is ready. Spawning workers")


# Environment variables
raw_env = [
    "DJANGO_SETTINGS_MODULE=trialssfinder.settings_production",
]
