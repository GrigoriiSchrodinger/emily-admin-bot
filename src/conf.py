import os

from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv('ENV', "localhost")
API_TOKEN = os.getenv('API_TOKEN')
PUBLIC_CHAT_ID = os.getenv('PUBLIC_CHAT_ID')
