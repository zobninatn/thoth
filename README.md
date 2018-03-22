Thoth uses Celery as a task queue, RabbitMQ as a message broker and MongoDB as a celery result backend

# Basic Setup

## Development

From the root of the project directory:

```bash
docker-compose up
```

If you want to enter debug mode of the django application:

```bash
echo "DJANGO_DEBUG=True" >> web/web-variables.env
```

## Production

From the root of the project directory:

```bash
echo "DJANGO_KEY=your_key" > web/web-variables.env
docker-compose up
```

# Usage

`POST localhost:8000/hash` with `url` paramenter returns GUID of the task

`GET localhost:8000/hash/GUID` where GUID is your task GUID returns:
* `state` state of the task - `PENDING`, `FAILURE`, `SUCCESS`
* `result` with md5 sum if `"state": "SUCCESS"` 
* `cause` with error message if `"state": "FAILURE"`
