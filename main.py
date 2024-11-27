import logging
import os
import sys
import requests
import asyncio
import zipfile
from io import BytesIO
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InputMediaPhoto, FSInputFile, InputMediaVideo
from aiogram.exceptions import TelegramRetryAfter
from src.conf import redis

logging.basicConfig(level=logging.INFO)

API_TOKEN = '7867687005:AAFnCIP8PNzN8dmqp941COFvU7r3KrNmIe0'
PUBLIC_CHAT_ID = '@FakeNewsBots'

def create_bot() -> Bot:
    """Создает экземпляр бота."""
    return Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

def create_dispatcher(bot: Bot) -> Dispatcher:
    """Создает экземпляр диспетчера."""
    return Dispatcher(bot=bot, storage=MemoryStorage())

def handle_response(response, channel: str, id_post: int) -> tuple[str, list[str]]:
    """Обрабатывает ответ от сервера."""
    if response.status_code == 200:
        zip_data = BytesIO(response.content)
        return extract_files(zip_data, channel, id_post)
    else:
        logging.error(f"Ошибка при скачивании: {response.json().get('detail', 'Неизвестная ошибка')}")
        return "", []

def extract_files(zip_data: BytesIO, channel: str, id_post: int) -> tuple[str, list[str]]:
    """Извлекает файлы из ZIP-архива."""
    base_dir = os.path.join('media', channel, str(id_post))
    os.makedirs(base_dir, exist_ok=True)

    with zipfile.ZipFile(zip_data) as zip_ref:
        zip_ref.extractall(base_dir)

    files = [os.path.join(root, filename) for root, _, filenames in os.walk(base_dir) for filename in filenames]
    logging.info(f"Файлы успешно скачаны и распакованы в {base_dir}")
    return base_dir, files

def prepare_media(files: list[str], content: str) -> list:
    """Подготавливает медиа для отправки."""
    list_media = []
    for index, file in enumerate(files):
        preview_text = content if index == 0 else ""  # Подпись только для первого медиа
        media_type = InputMediaVideo if file.endswith('.mp4') else InputMediaPhoto
        list_media.append(media_type(media=FSInputFile(path=file), caption=preview_text))
    return list_media

async def send_media_group(media: list) -> None:
    """Отправляет группу медиа и редактирует текст медиа."""
    try:
        await bot.send_media_group(chat_id=PUBLIC_CHAT_ID, media=media)
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await bot.send_media_group(chat_id=PUBLIC_CHAT_ID, media=media)

def download_media_files(base_url: str, channel: str, id_post: int) -> tuple[str, list[str]]:
    """Скачивает медиафайлы поста и сохраняет их в отдельную папку."""
    try:
        url = f"{base_url}/download-media/{id_post}/{channel}"
        response = requests.post(url)
        return handle_response(response, channel, id_post)
    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}")
        return "", []

async def send_message():
    """Обрабатывает и отправляет сообщения из очереди."""
    try:
        message = redis.receive_from_queue()
        if message and "content" in message and isinstance(message["content"], str):
            logging.info(message["content"])
            path_media, media = download_media_files(
                base_url="http://0.0.0.0:8000/news",
                channel=message["channel"],
                id_post=message["id_post"]
            )
            if path_media:
                list_media = prepare_media(media, message["content"])
                if list_media:
                    await send_media_group(list_media)
        else:
            logging.error("Ошибка: Нет контента или неверный формат данных.")
    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}")

async def main() -> None:
    """Основной цикл отправки сообщений."""
    while True:
        await send_message()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    bot = create_bot()
    dp = create_dispatcher(bot)
    asyncio.run(main())

