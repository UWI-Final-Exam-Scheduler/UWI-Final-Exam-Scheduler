import os
import multiprocessing

# Bind to platform-provided port (Render) or default 8080.
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# Worker settings
workers = int(os.environ.get("WEB_CONCURRENCY", max(1, multiprocessing.cpu_count() // 2)))
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "gevent")

# Increase timeout for heavy upload endpoints (PDF/CSV processing).
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "180"))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", str(timeout)))
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))

# Logging
loglevel = os.environ.get("LOG_LEVEL", "info")
accesslog = '-'  # stdout
errorlog = '-'   # stderr