from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.signals import task_failure
from celery.schedules import crontab
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shahin.settings')

app = Celery('shahin')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')



@task_failure.connect
def task_failure_handler(sender, task_id, exception, args, kwargs, **kw):
    print(f"Task {task_id} failed. Exception: {exception}")
    # You can log the failure to a file or perform any other actions here

CELERY_BEAT_SCHEDULE = {
    'generate_quote_by_ai_fitness': {
        'task': 'ai.tasks.generate_quote',
        'schedule': crontab(hour=0, minute=0),  
        'args': ('Fitness'),  
    },
        'generate_quote_by_ai_career': {
        'task': 'ai.tasks.generate_quote',  
        'schedule': crontab(hour=0, minute=6),  
        'args': ('Career'),  
    },
        'generate_quote_by_ai_business': {
        'task': 'ai.tasks.generate_quote',  
        'schedule': crontab(hour=0, minute=13),  
        'args': ('Business'),  
    },
        'generate_quote_by_ai_discipline': {
        'task': 'ai.tasks.generate_quote',  
        'schedule': crontab(hour=0, minute=20),  
        'args': ('Discipline'),  
    },
        'generate_quote_by_ai_mindset': {
        'task': 'ai.tasks.generate_quote',  
        'schedule': crontab(hour=0, minute=26),  
        'args': ('Mindset'), 
    },
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()