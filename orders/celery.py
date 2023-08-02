import os

from celery import Celery
from orders.settings import CELERY_BROKER_URL

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ordering_groceries.settings')
app = Celery('ordering_groceries', broker=CELERY_BROKER_URL)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()