from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.conf import API_TOKEN
from src.feature.request.RequestHandler import RequestDataBase
from src.logger import logger
from src.feature.bot.message_handler import MessageHandler
from src.feature.bot.media_handler import MediaHandler


class TelegramBot:
    def __init__(self):
        self.token = API_TOKEN
        self.ParseMode = ParseMode.HTML
        self.bot = self._create_bot()
        self.db = RequestDataBase()
        self.message_handler = MessageHandler(self.bot)
        self.media_handler = MediaHandler(self.bot)

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

    async def send_message(self, message: dict, seed: str) -> int:
        return await self.message_handler.send_message(message, seed)

    async def send_media_group(self, media: list, message: dict, seed: str) -> int:
        return await self.media_handler.send_media_group(media, message, seed)

    async def retry_send_media_group(self, media: list, retry_after: int):
        await self.media_handler.retry_send_media_group(media, retry_after)

    async def retry_send_message(self, message: str, retry_after: int):
        await self.message_handler.retry_send_message(message, retry_after)

    @staticmethod
    def prepare_media(files: list[str], content: str) -> list:
        return MediaHandler.prepare_media(files, content)
