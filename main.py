import logging
import os
import sys

import requests
from aiogram import Bot, Dispatcher
import asyncio

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InputMediaPhoto, FSInputFile
from aiogram.exceptions import TelegramRetryAfter

from src.conf import redis

logging.basicConfig(level=logging.INFO)

API_TOKEN = '7867687005:AAFnCIP8PNzN8dmqp941COFvU7r3KrNmIe0'
PUBLIC_CHAT_ID = '@FakeNewsBots'

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)


def download_media_files(base_url: str, channel: str, id_post: int) -> tuple[str, list[str]]:
    """
    Скачивает медиафайлы поста и сохраняет их в отдельную папку

    Args:
        base_url (str): Базовый URL API
        channel (str): Название канала
        id_post (int): ID поста

    Returns:
        tuple[str, list[str]]: Кортеж из пути к папке и списка файлов, или ("", []) в случае ошибки
    """
    try:
        import os
        import zipfile
        from io import BytesIO

        base_dir = os.path.join('media', channel, str(id_post))
        os.makedirs(base_dir, exist_ok=True)

        url = f"{base_url}/download-media/{id_post}/{channel}"

        response = requests.post(url)

        if response.status_code == 200:
            # Создаем объект ZIP из полученных данных
            zip_data = BytesIO(response.content)
            
            # Распаковываем архив
            with zipfile.ZipFile(zip_data) as zip_ref:
                zip_ref.extractall(base_dir)
                
            # Получаем список всех файлов в директории
            files = []
            for root, _, filenames in os.walk(base_dir):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    files.append(file_path)
                
            print(f"Файлы успешно скачаны и распакованы в {base_dir}")
            return base_dir, files
        else:
            print(f"Ошибка при скачивании: {response.json().get('detail', 'Неизвестная ошибка')}")
            return "", []

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return "", []


async def send_message():
    try:
        message = redis.receive_from_queue()
        if message and "content" in message and isinstance(message["content"], str):
            print(message["content"])
            path_media, media = download_media_files(base_url="http://0.0.0.0:8000/news", channel=message["channel"], id_post=message["id_post"])
            list_media = []
            content = message["content"]

            if path_media:
                for files in media:
                    if len(list_media) < 10:
                        if not list_media:
                            preview_text = content[:900] + ("..." if len(content) > 900 else "")
                            list_media.append(InputMediaPhoto(media=FSInputFile(path=os.path.join(files)), caption=preview_text))
                        else:
                            list_media.append(InputMediaPhoto(media=FSInputFile(path=os.path.join(files))))
                
                if list_media:
                    try:
                        await bot.send_media_group(chat_id=PUBLIC_CHAT_ID, media=list_media)
                        await asyncio.sleep(5)
                        if len(content) > 900:
                            await bot.send_message(chat_id=PUBLIC_CHAT_ID, text=content)
                    except TelegramRetryAfter as e:
                        await asyncio.sleep(e.retry_after)
                        await bot.send_media_group(chat_id=PUBLIC_CHAT_ID, media=list_media)
                else:
                    await bot.send_message(chat_id=PUBLIC_CHAT_ID, text=content)
            else:
                await bot.send_message(chat_id=PUBLIC_CHAT_ID, text=content)
        else:
            print("Ошибка: Нет контента или неверный формат данных.")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
    
    await asyncio.sleep(1)

async def main() -> None:
    while True:
        await send_message()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

