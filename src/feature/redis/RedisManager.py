import json

import redis

from src.service_url import get_url_redis


class RedisQueue:
    def __init__(self, queue_name, host=get_url_redis(), port=6379, db=0):
        """
        Инициализирует подключение к Redis и имя очереди.
        """
        self.queue_name = queue_name
        self.redis_conn = redis.Redis(host=host, port=port, db=db)

    def send_to_queue(self, queue, data):
        """
        Отправляет данные в очередь
        """
        self.redis_conn.rpush(queue, data)

    def receive_from_queue(self, block=True, timeout=None):
        """
        Получает данные из очереди
        Если блокировка включена, будет ждать до появления данных.
        """
        if block:
            item = self.redis_conn.blpop(self.queue_name, timeout=timeout)
        else:
            item = self.redis_conn.lpop(self.queue_name)

        if item:
            return json.loads(item[1].decode('utf-8'))
        return None
