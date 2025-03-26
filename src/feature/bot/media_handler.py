from typing import List, Dict
import json
import asyncio
from aiogram import Bot
from aiogram.types import InputMediaPhoto, FSInputFile, InputMediaVideo

from src.conf import PUBLIC_CHAT_ID
from src.feature.request.RequestHandler import RequestDataBase
from src.logger import logger
from src.service import redis, request_db


class MediaHandler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = RequestDataBase()

    async def send_media_group(self, media: List, message: Dict, seed: str) -> int:
        try:
            logger.debug(f"Отправка медиа - {media}")
            reply_to_message_id = request_db.get_related_news(seed=seed).tied
            
            if reply_to_message_id:
                try:
                    message_id = await self.bot.send_media_group(
                        chat_id=PUBLIC_CHAT_ID,
                        media=media,
                        reply_to_message_id=reply_to_message_id
                    )
                    return message_id[0].message_id
                except Exception as reply_error:
                    if "message to be replied not found" in str(reply_error):
                        logger.warning("Сообщение для ответа не найдено, отправляем без reply_to_message_id")
                        return await self._send_simple_media_group(media)
                    raise reply_error
            else:
                return await self._send_simple_media_group(media)
                
        except Exception as error:
            logger.error(f"Ошибка: {error}")
            detail_post = self.db.get_detail_news_by_channel_id_post(
                channel=message["channel"],
                id_post=message["id_post"]
            )
            redis.send_to_queue(queue="text_conversion", data=json.dumps(detail_post))
            raise

    async def _send_simple_media_group(self, media: List) -> int:
        message_id = await self.bot.send_media_group(chat_id=PUBLIC_CHAT_ID, media=media)
        return message_id[0].message_id

    async def retry_send_media_group(self, media: List, retry_after: int):
        logger.debug(f"Повторная отправка медиа через {retry_after} секунд - {media}")
        await asyncio.sleep(retry_after)
        await self.bot.send_media_group(chat_id=PUBLIC_CHAT_ID, media=media)

    @staticmethod
    def prepare_media(files: List[str], content: str) -> List:
        return [
            (InputMediaVideo if file.endswith('.mp4') else InputMediaPhoto)(
                media=FSInputFile(path=file),
                caption=content if index == 0 else ""
            )
            for index, file in enumerate(files)
        ] 