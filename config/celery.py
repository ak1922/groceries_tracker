import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('groceries_tracker')
# Using CELERY_ namespace means all celery configs must be uppercase in settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
