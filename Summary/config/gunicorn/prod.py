#Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "summary.wsgi:application"
# The granularity of Error log outputs
loglevel = "debug"
# The number of worker processes for handling requests
workers = 1
worker_class = "gthread"
# The number of threads that can be used 
threads = 2
timeout = 7200
graceful_timeout  = 7200
keepalive = 5
# The socket to bind
bind = "0.0.0.0:8000"
# Restart workers when code changes (development only!)
reload = True
# Write access and error info to /var/log
accesslog = errorlog = "/home/hktang/var/log/gunicorn/prod.log"
# Redirect stdout/stderr to log file
capture_output = True
# PID file so you can easily fetch process ID
pidfile = "/home/hktang/var/run/gunicorn/prod.pid"
# Daemonize the Gunicorn process (detach & enter background)
daemon = True
pythonpath = "/home/hktang/projects/tang-task-extractor/venv/bin/python"
