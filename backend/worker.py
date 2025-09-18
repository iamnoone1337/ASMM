# Entrypoint for RQ worker (import path used in docker-compose)
from rq import Connection, Worker
from redis import Redis
from backend.app.config import settings

if __name__ == "__main__":
    redis = Redis.from_url(settings.REDIS_URL)
    with Connection(redis):
        w = Worker([settings.RQ_QUEUE_NAME])
        w.work()