import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InputMediaPhoto, FSInputFile, InputMediaVideo

from src.conf import API_TOKEN, PUBLIC_CHAT_ID
from src.logger import logger


class TelegramBot:
    def __init__(self):
        self.token = API_TOKEN
        self.ParseMode = ParseMode.HTML
        self.bot = self._create_bot()

    def _create_bot(self):
        try:
            return Bot(token=self.token, default=DefaultBotProperties(parse_mode=self.ParseMode))
        except Exception as error:
            logger.error(f"Ошибка при создании бота: {error}")
            raise

    def create_dispatcher(self):
        return Dispatcher(bot=self.bot, storage=MemoryStorage())

    def start(self):
        self.create_dispatcher()

    async def send_message(self, message: str):
        try:
            logger.debug(f"Отправка текста - {message}")
            await self.bot.send_message(chat_id=PUBLIC_CHAT_ID, text=message)
        except TelegramRetryAfter as error:
            logger.error(f"Ошибка: {error.message}")
            await self._retry_send_media_message(message=message, retry_after=error.retry_after)

    async def send_media_group(self, media: list):
        try:
            logger.debug(f"Отправка медиа - {media}")
            await self.bot.send_media_group(chat_id=PUBLIC_CHAT_ID, media=media)
        except TelegramRetryAfter as error:
            logger.error(f"Ошибка: {error.message}")
            await self._retry_send_media_group(media, error.retry_after)

    async def _retry_send_media_group(self, media: list, retry_after: int):
        logger.debug(f"Повторная отправка медиа через {retry_after} секунд - {media}")
        await asyncio.sleep(retry_after)
        await self.bot.send_media_group(chat_id=PUBLIC_CHAT_ID, media=media)

    async def _retry_send_media_message(self, message: str, retry_after: int):
        logger.debug(f"Повторная отправка текста через {retry_after} секунд - {message}")
        await asyncio.sleep(retry_after)
        await self.bot.send_message(chat_id=PUBLIC_CHAT_ID, text=message)

    @staticmethod
    def prepare_media(files: list[str], content: str) -> list:
        return [
            (InputMediaVideo if file.endswith('.mp4') else InputMediaPhoto)(
                media=FSInputFile(path=file),
                caption=content if index == 0 else ""
            )
            for index, file in enumerate(files)
        ]
