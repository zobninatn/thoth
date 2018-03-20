from celery import Celery, shared_task, states
from celery.exceptions import Ignore
from django.conf import settings
import requests
import hashlib
import os

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

app = Celery('tasks')
app.config_from_object('config:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@shared_task()
def download(url, filename):
    """
    Downloads a file from the url to the filesystem
    """
    logger.debug(url)
    if is_downloadable(url):
        logger.debug("File downloadable")
        path = './data/'
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + filename, "wb") as file:
            response = requests.get(url)
            file.write(response.content)
        return path+filename
    else:
        logger.debug("File is not downloadable")
        download.update_state(
            state=states.FAILURE,
            info='File is not downloadable',
            meta={'info': 'File is not downloadable'}
        )
        raise Ignore()


@shared_task()
def hash(path):
    """
    Counts md5 hash of a file from path
    """
    logger.debug(path)
    logger.debug("Hashing started")
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096*32), b""):
            hash_md5.update(chunk)
    os.remove(path)
    return hash_md5.hexdigest()


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
