from request.RequestHandler import RequestHandler
from src.redis.RedisManager import RedisQueue

redis = RedisQueue(queue_name="ReadyNews", host="localhost", port=6379, db=0)
api = RequestHandler(base_url="http://0.0.0.0:8000/news")
