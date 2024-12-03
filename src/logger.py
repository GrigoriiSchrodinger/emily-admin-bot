import json
import logging

import requests


class LokiHandler(logging.Handler):
    def __init__(self, url, tags):
        super().__init__()
        self.url = url
        self.tags = tags

    def emit(self, record):
        log_entry = self.format(record)
        tags_with_level = {
            **self.tags,
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "time": record.created
        }

        if record.levelname == "ERROR":
            tags_with_level["error_count"] = 1

        payload = {
            "streams": [
                {
                    "stream": tags_with_level,
                    "values": [
                        [str(int(record.created * 1e9)), log_entry]
                    ]
                }
            ]
        }
        headers = {'Content-Type': 'application/json'}
        try:
            requests.post(self.url, data=json.dumps(payload), headers=headers)
        except Exception as e:
            print(f"Failed to send log to Loki: {e}")


logger = logging.getLogger("Emily")
logger.setLevel(logging.DEBUG)

loki_handler = LokiHandler(
    url="http://localhost:3100/loki/api/v1/push",
    tags={"project": "Emily"},
)
logger.addHandler(loki_handler)
