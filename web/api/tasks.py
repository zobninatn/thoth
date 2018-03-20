from celery import Celery, shared_task
from django.conf import settings

import logging

logger = logging.getLogger(__name__)

app = Celery('tasks')
app.config_from_object('config:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@shared_task
def download(url):
    logger.debug(url)
    return "data"


@shared_task
def hash(path):
    logger.debug(path)
    return True
