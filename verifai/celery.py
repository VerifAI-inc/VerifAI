# verifai/celery.py
import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verifai.settings')

app = Celery('verifai')

# Read config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks from all apps
app.autodiscover_tasks()
