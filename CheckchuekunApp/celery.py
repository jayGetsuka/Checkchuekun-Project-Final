import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CheckchuekunApp.settings')

app = Celery('CheckchuekunApp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# use Django Channels worker
app.conf.update(
    worker_class='channels.worker.ChannelsWorker',
)