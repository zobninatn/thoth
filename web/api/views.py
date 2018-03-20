from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from celery.result import AsyncResult
from celery import uuid

from api import tasks
import logging

logger = logging.getLogger(__name__)


class HashTaskViewSet(viewsets.ViewSet):
    """
    API endpoint that allow to start document hashing or to get result from it.
    """
    def retrieve(self, request, pk=None):
        try:
            res = AsyncResult(pk)
            logger.debug(pk)
            logger.debug(res.state)
            logger.debug(res.get)
            if res.state == 'SUCCESS':
                content = {'state': res.state, 'result': res.get()}
                return Response(content, status=status.HTTP_200_OK)
            elif res.state == 'FAILURE':
                # logger.debug(res.get())
                # logger.debug(res.result)
                # logger.debug(res.info)
                # logger.debug(res.msg)
                content = {'state': res.state}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            else:
                content = {'state': res.state}
                return Response(content, status=status.HTTP_409_CONFLICT)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        if 'url' in request.POST:
            url = request.POST['url']
            logger.debug(url)
            filename = uuid()
            chain = (tasks.download.s(url, filename) | tasks.hash.s()).apply_async()
            logger.debug("id: {}".format(id))
            content = {'GUID': chain.id}
            return Response(content, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
