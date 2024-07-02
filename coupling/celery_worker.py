from . import celery
from . import logical_coupling

# Ensure the Celery app is loaded when the worker starts
if __name__ == '__main__':
    celery.start()
