from celery import Celery, shared_task, states, task, Task, current_task
from celery.exceptions import Ignore
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.files import File
import requests

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

app = Celery('tasks')
app.config_from_object('config:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


class CallbackTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        logger.debug("download succeed")


@shared_task(base=CallbackTask)  # this does the trick
def download(url, filename):
    """
    Downloads a file from the url to the filesystem
    """
    logger.debug(url)
    if is_downloadable(url):
        logger.debug("File downloadable")

        with open(filename, "wb") as file:
            response = requests.get(url)
            file.write(response.content)
        return filename
    else:
        logger.debug("File is not downloadable")
        download.update_state(
            state=states.FAILURE,
            info='File is not downloadable',
            meta={'info': 'File is not downloadable'}
        )
        raise Ignore()


@task(base=CallbackTask)
def hash(path):
    logger.debug(path)
    logger.debug("Hashing started")
    return path


def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True
