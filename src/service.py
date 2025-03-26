from src.feature.file_manager import FileManager
from src.feature.redis.RedisManager import RedisQueue
from src.feature.request.RequestHandler import RequestDataBase

redis = RedisQueue(queue_name="ReadyNews", port=6379, db=0)
request_db = RequestDataBase()
file_manager = FileManager()
