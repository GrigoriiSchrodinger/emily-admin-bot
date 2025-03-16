import os

from dotenv import load_dotenv
from src.feature.request.RequestHandler import RequestHandler
from src.feature.redis.RedisManager import RedisQueue

load_dotenv()

ENV = os.getenv('ENV', "localhost")
API_TOKEN = os.getenv('API_TOKEN')
PUBLIC_CHAT_ID = os.getenv('PUBLIC_CHAT_ID')

SERVICE_URLS = {
    "localhost": {
        "emily_database_handler": "http://localhost:8000",
        "redis": "localhost",
        "loki": "http://localhost:3100"
    },
    "production": {
        "emily_database_handler": "http://emily-database-handler:8000",
        "redis": "redis",
        "loki": "http://loki:3100"
    }
}

def get_url_emily_database_handler():
    return SERVICE_URLS[ENV]["emily_database_handler"]

def get_url_redis():
    return SERVICE_URLS[ENV]["redis"]

def get_url_loki():
    return SERVICE_URLS[ENV]["loki"]

redis = RedisQueue(queue_name="ReadyNews", host=get_url_redis(), port=6379, db=0)
api = RequestHandler()