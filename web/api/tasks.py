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


def unpack_chain(nodes):
    while nodes.parent:
        yield nodes.parent
        nodes = nodes.parent
    yield nodes


@app.task(bind=True)
def download(self, url, filename):
    """
    Downloads a file from the url to the filesystem
    """
    logger.debug(url)
    if is_downloadable(url):
        logger.debug('File downloadable')
        path = './data/'
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + filename, 'wb') as file:
            response = requests.get(url)
            file.write(response.content)
        return path+filename
    else:
        logger.debug('File is not downloadable')
        return False


@app.task(bind=True)
def hash(self, path):
    """
    Counts md5 hash of a file from path
    """
    if path is False:
        raise Exception('File is not downloadable')
    logger.debug(path)
    logger.debug('Hashing started')
    hash_md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096*32), b""):
            hash_md5.update(chunk)
    os.remove(path)
    return hash_md5.hexdigest()


def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    try:
        h = requests.head(url, allow_redirects=True)
        header = h.headers
        content_type = header.get('content-type')
        logger.debug('content_type: {}'.format(content_type))
        keywords = ['text/html', 'text', 'html']
        for word in keywords:
            if word in content_type.lower():
                return False
        return True
    except requests.exceptions.MissingSchema:
        return False
