import os
from celery import Celery

# set default Django settings module for 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ishemalink.settings')

app = Celery('ishemalink')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# Optionally add a debug task
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
