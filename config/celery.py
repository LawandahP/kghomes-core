from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf.settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    #Scheduler Name
    'Create Recurring Invoices': {
        # Task Name (Name Specified in Decorator)
        'task': 'create_recurring_invoices',  
        # Schedule      
        'schedule': crontab(minute='*/1'),
    },

    'Update Invoice Status': {
        'task': 'update-invoice-status',
        'schedule': crontab(minute='*/1')
    },

    'Update Lease Status': {
        'task': 'update-lease-status',
        'schedule': crontab(minute='*/1')
    }
}

