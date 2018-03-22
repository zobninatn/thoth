from rest_framework.test import APIRequestFactory
from django.test import SimpleTestCase
from api.views import HashViewSet
from api import tasks
from time import sleep
import json


class HashViewSetTest(SimpleTestCase):
    """
    Test module for api viewsets
    """
    factory = APIRequestFactory()

    def test_create_success(self):
        url = 'https://sun1-12.userapi.com/c816421/u16366863/docs/2e45b2ea34b1/sciencelabvk.gif'
        request = self.factory.post('/hash/', {'url': url})
        hash_view = HashViewSet.as_view({'post': 'create'})
        response = hash_view(request)
        self.assertEqual(response.status_code, 202)

    def test_create_failure(self):
        request = self.factory.post('/hash/', {'': ''})
        hash_view = HashViewSet.as_view({'post': 'create'})
        response = hash_view(request)
        self.assertEqual(response.status_code, 400)

    def test_retrieve_pending(self):
        url = 'https://sun1-12.userapi.com/c816421/u16366863/docs/2e45b2ea34b1/sciencelabvk.gif'
        request = self.factory.post('/hash/', {'url': url})
        hash_view_create = HashViewSet.as_view({'post': 'create'})
        response = hash_view_create(request)
        response.render()
        guid = json.loads(response.content)['GUID']

        request = self.factory.get('/notes/')
        hash_view_retrieve = HashViewSet.as_view({'get': 'retrieve'})
        retrieve_response = hash_view_retrieve(request, pk=guid)
        self.assertEqual(retrieve_response.status_code, 409)

    """
    TODO: 
    
    Next tests should not depend on time.sleep()
    Possible solution - run celery tasks synchronously 
    or just test celery tasks without ViewSets.

    info: http://docs.celeryproject.org/projects/django-celery/en/2.4/cookbook/unit-testing.html
    """



    def test_retrieve_success(self):
        url = 'https://sun1-12.userapi.com/c816421/u16366863/docs/2e45b2ea34b1/sciencelabvk.gif'
        request = self.factory.post('/hash/', {'url': url})
        hash_view_create = HashViewSet.as_view({'post': 'create'})
        response = hash_view_create(request)
        response.render()
        guid = json.loads(response.content)['GUID']
        sleep(5)

        request = self.factory.get('/notes/')
        hash_view_retrieve = HashViewSet.as_view({'get': 'retrieve'})
        retrieve_response = hash_view_retrieve(request, pk=guid)
        self.assertEqual(retrieve_response.status_code, 200)

    def test_retrieve_failure_not_downloadable(self):
        url = 'https://sun1-12.userapi.com/c816421/u16366863/docs/2e45b2ea34b1/science'
        request = self.factory.post('/hash/', {'url': url})
        hash_view_create = HashViewSet.as_view({'post': 'create'})
        response = hash_view_create(request)
        response.render()
        guid = json.loads(response.content)['GUID']
        sleep(5)

        request = self.factory.get('/notes/')
        hash_view_retrieve = HashViewSet.as_view({'get': 'retrieve'})
        retrieve_response = hash_view_retrieve(request, pk=guid)
        self.assertEqual(retrieve_response.status_code, 400)

    def test_retrieve_failure_broken_link(self):
        url = 'sun1-12.userapi.com/c816421/u16366863/docs/2e45b2ea34b1/sciencelabvk.gif'
        request = self.factory.post('/hash/', {'url': url})
        hash_view_create = HashViewSet.as_view({'post': 'create'})
        response = hash_view_create(request)
        response.render()
        guid = json.loads(response.content)['GUID']
        sleep(5)

        request = self.factory.get('/notes/')
        hash_view_retrieve = HashViewSet.as_view({'get': 'retrieve'})
        retrieve_response = hash_view_retrieve(request, pk=guid)
        self.assertEqual(retrieve_response.status_code, 400)


class TasksTest(SimpleTestCase):
    """
    Test module for celery tasks
    """
    def test_is_downloadable_broken_link(self):
        url = 'sun1-12.userapi.com/c816421/u16366863/docs/2e45b2ea34b1/sciencelabvk.gif'
        result = tasks.is_downloadable(url)
        self.assertEqual(result, False)

    def test_is_downloadable_text(self):
        url = 'https://sun1-12.userapi.com/c816421/u16366863/docs/2e45b2ea34b1/science'
        result = tasks.is_downloadable(url)
        self.assertEqual(result, False)

    def test_is_downloadable_success(self):
        url = 'https://sun1-12.userapi.com/c816421/u16366863/docs/2e45b2ea34b1/sciencelabvk.gif'
        result = tasks.is_downloadable(url)
        self.assertEqual(result, True)
