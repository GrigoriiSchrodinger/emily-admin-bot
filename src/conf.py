from src.redis.RedisManager import RedisQueue

redis = RedisQueue(queue_name="ReadyNews", host="localhost", port=6379, db=0)
