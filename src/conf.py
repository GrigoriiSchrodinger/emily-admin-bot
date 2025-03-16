import os

from dotenv import load_dotenv
from src.feature.request.RequestHandler import RequestHandler
from src.feature.redis.RedisManager import RedisQueue

load_dotenv()

ENV = os.getenv('ENV', "localhost")
API_TOKEN = os.getenv('API_TOKEN')
PUBLIC_CHAT_ID = os.getenv('PUBLIC_CHAT_ID')

redis = RedisQueue(queue_name="ReadyNews", port=6379, db=0)
api = RequestHandler()