FROM python:3.6.4-stretch
ENV PYTHONUNFUFFERED 1
RUN mkdir web
WORKDIR /web
ADD . /web
RUN pip install -r requirements.txt