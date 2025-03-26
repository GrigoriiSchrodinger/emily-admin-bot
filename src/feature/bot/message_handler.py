from typing import Dict
import json
from aiogram import Bot
import asyncio

from src.conf import PUBLIC_CHAT_ID
from src.logger import logger
from src.service import redis, request_db


class MessageHandler:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_message(self, message: Dict, seed: str) -> int:
        try:
            logger.debug(f"Отправка текста - {message}")
            reply_to_message_id = request_db.get_related_news(seed=seed).tied
            
            if reply_to_message_id:
                try:
                    message_id = await self.bot.send_message(
                        chat_id=PUBLIC_CHAT_ID,
                        text=message["content"],
                        reply_to_message_id=reply_to_message_id
                    )
                    return message_id.message_id
                except Exception as reply_error:
                    if "message to be replied not found" in str(reply_error):
                        logger.warning("Сообщение для ответа не найдено, отправляем без reply_to_message_id")
                        return await self._send_simple_message(message["content"])
                    raise reply_error
            else:
                return await self._send_simple_message(message["content"])
                
        except Exception as error:
            logger.error(f"Ошибка: {error}")
            redis.send_to_queue(queue="text_conversion", data=json.dumps(message))
            raise

    async def _send_simple_message(self, content: str) -> int:
        message_id = await self.bot.send_message(chat_id=PUBLIC_CHAT_ID, text=content)
        return message_id.message_id

    async def retry_send_message(self, message: str, retry_after: int):
        logger.debug(f"Повторная отправка текста через {retry_after} секунд - {message}")
        await asyncio.sleep(retry_after)
        await self.bot.send_message(chat_id=PUBLIC_CHAT_ID, text=message) 