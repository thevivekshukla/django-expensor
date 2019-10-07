import os

from django.core import management
from django.conf import settings

from celery import Celery
from celery.schedules import crontab

environment = os.getenv('DJANGO_ENV', 'production')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expensor.settings.' + environment)

app = Celery('expensor')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(name="backup")
def backup():
    management.call_command('dbbackup')


if not settings.DEBUG:
    app.conf.beat_schedule = {
        'backup-database-everynight': {
            'task': 'backup',
            'schedule': crontab(minute=0, hour=0),
        },
    }
