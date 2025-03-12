import os

from dotenv import load_dotenv
from src.feature.request.RequestHandler import RequestHandler
from src.feature.redis.RedisManager import RedisQueue

load_dotenv()

redis = RedisQueue(queue_name="ReadyNews", host="redis", port=6379, db=0)
api = RequestHandler(base_url="http://emily-database-handler:8000/")

API_TOKEN = os.getenv('API_TOKEN')
PUBLIC_CHAT_ID = os.getenv('PUBLIC_CHAT_ID')
URL_DOWNLOAD = os.getenv('URL_DOWNLOAD', "http://emily-database-handler:8000/")
