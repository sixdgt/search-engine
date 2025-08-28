# backend/celery.py (or scraper_project/celery.py)
import os
import logging
from celery import Celery

# Set up logging
logger = logging.getLogger(__name__)

# Set the default Django settings module for the 'celery' program
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
except ImportError as e:
    logger.error(f"Failed to set DJANGO_SETTINGS_MODULE: {e}")
    raise

# Create Celery app
app = Celery('backend')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in specific apps (optional: limits scope)
app.autodiscover_tasks(['core'])

# Optional: Log Celery setup completion
logger.debug("Celery app initialized successfully")