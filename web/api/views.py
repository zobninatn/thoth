from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from celery.result import AsyncResult

from api import serializers
from api.models import Task
from api import tasks
import logging

logger = logging.getLogger(__name__)


class HashTaskViewSet(viewsets.ViewSet):
    """
    API endpoint that allow to start document hashing or to get result from it.
    """

    def retrieve(self, request, pk=None):
        try:
            res = tasks.download.AsyncResult(pk)
            logger.debug(pk)
            logger.debug(res.state)
            logger.debug(res.get)
            if res.status == 'SUCCESS':
                content = {'result': res.get}
                return Response(content, status=status.HTTP_200_OK)
            elif res.status == 'FAILURE':
                content = {'status': res.status, 'cause': res.info}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            else:
                content = {'status': res.status}
                return Response(content, status=status.HTTP_409_CONFLICT)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        if 'url' in request.POST:
            url = request.POST['url']
            logger.debug(url)
            res = tasks.download.delay(url)
            content = {'GUID': res.id}
            return Response(content, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
