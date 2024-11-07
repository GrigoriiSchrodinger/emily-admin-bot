import json
import logging
import sys

from aiogram import Bot, Dispatcher
import asyncio

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.conf import redis

logging.basicConfig(level=logging.INFO)

API_TOKEN = '7867687005:AAFnCIP8PNzN8dmqp941COFvU7r3KrNmIe0'
PUBLIC_CHAT_ID = '@FakeNewsBots'

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

async def send_message():
    message = redis.receive_from_queue()
    if message and "content" in message and isinstance(message["content"], str):
        print(message["content"])
        await bot.send_message(chat_id=PUBLIC_CHAT_ID, text=message["content"])
    else:
        print("Ошибка: Нет контента или неверный формат данных.")
    await asyncio.sleep(1)

async def main() -> None:
    while True:
        await send_message()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
