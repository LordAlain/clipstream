from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, shared_task
import subprocess
from pathlib import Path

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clipstream.settings')

app = Celery('clipstream')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# Namespace 'CELERY' means all celery-related configs must start with 'CELERY_'.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover and load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
