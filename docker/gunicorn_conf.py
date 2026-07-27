bind = "0.0.0.0:5000"
# Worker Options
workers = 5
worker_class = "uvicorn.workers.UvicornWorker"

# Logging Options
loglevel = "info"
accesslog = "/var/log/forc.access.log"
errorlog = "/var/log/forc.error.log"