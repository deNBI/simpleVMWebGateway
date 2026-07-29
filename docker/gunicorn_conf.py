# Socket Path
bind = "unix:/tmp/forc.sock"

# Worker Options
workers = 5
worker_class = "uvicorn.workers.UvicornWorker"

# Logging Options
loglevel = "info"
accesslog = "/tmp/forc.access.log"
errorlog = "/tmp/forc.error.log"