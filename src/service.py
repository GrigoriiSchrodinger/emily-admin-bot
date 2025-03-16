from src.feature.redis.RedisManager import RedisQueue

redis = RedisQueue(queue_name="ReadyNews", port=6379, db=0)
