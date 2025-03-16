from src.conf import ENV

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