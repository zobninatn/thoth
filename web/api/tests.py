from rest_framework.test import APIRequestFactory
from django.test import SimpleTestCase
from api.views import HashViewSet
from api import tasks
from time import sleep
import json

IMAGE_URL = "https://avatars1.githubusercontent.com/u/9352211"
IMAGE_URL_BROKEN = "https://avatars1.githubuserconten/"
IMAGE_URL_TEXT  = "https://github.com" 

class HashViewSetTest(SimpleTestCase):
    """
    Test module for api viewsets
    """
    factory = APIRequestFactory()

    def test_create_success(self):
        request = self.factory.post('/hash/', {'url': IMAGE_URL})
        hash_view = HashViewSet.as_view({'post': 'create'})
        response = hash_view(request)
        self.assertEqual(response.status_code, 202)

    def test_create_failure(self):
        request = self.factory.post('/hash/', {'': ''})
        hash_view = HashViewSet.as_view({'post': 'create'})
        response = hash_view(request)
        self.assertEqual(response.status_code, 400)

    """
    TODO: 
    
    Next tests should not depend on time.sleep()
    Possible solution - run celery tasks synchronously 
    or just test celery tasks without ViewSets.

    It also cause tests fails with slow internet.

    info: http://docs.celeryproject.org/projects/django-celery/en/2.4/cookbook/unit-testing.html
    """
    def retrieve_guid_with_delay(self, url):
        request = self.factory.post('/hash/', {'url': url})
        hash_view_create = HashViewSet.as_view({'post': 'create'})
        response = hash_view_create(request)
        response.render()
        guid = json.loads(response.content)['GUID']
        sleep(1)
        return guid

    def test_retrieve_success(self):
        guid = self.retrieve_guid_with_delay(IMAGE_URL)
        request = self.factory.get('/notes/')
        hash_view_retrieve = HashViewSet.as_view({'get': 'retrieve'})
        retrieve_response = hash_view_retrieve(request, pk=guid)
        self.assertEqual(retrieve_response.status_code, 200)

    def test_retrieve_failure_not_downloadable(self):
        guid = self.retrieve_guid_with_delay(IMAGE_URL_TEXT)
        request = self.factory.get('/notes/')
        hash_view_retrieve = HashViewSet.as_view({'get': 'retrieve'})
        retrieve_response = hash_view_retrieve(request, pk=guid)
        self.assertEqual(retrieve_response.status_code, 400)

    def test_retrieve_failure_broken_link(self):
        guid = self.retrieve_guid_with_delay(IMAGE_URL_BROKEN)
        request = self.factory.get('/notes/')
        hash_view_retrieve = HashViewSet.as_view({'get': 'retrieve'})
        retrieve_response = hash_view_retrieve(request, pk=guid)
        self.assertEqual(retrieve_response.status_code, 400)


class TasksTest(SimpleTestCase):
    """
    Test module for celery tasks
    """
    def test_is_downloadable_broken_link(self):
        result = tasks.is_downloadable(IMAGE_URL_BROKEN)
        self.assertEqual(result, False)

    def test_is_downloadable_text(self):
        result = tasks.is_downloadable(IMAGE_URL_TEXT)
        self.assertEqual(result, False)

    def test_is_downloadable_success(self):
        result = tasks.is_downloadable(IMAGE_URL)
        self.assertEqual(result, True)
