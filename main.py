import asyncio
import logging

from src.conf import redis
from src.feature.bot import TelegramBot
from src.feature.file_manager import FileManager

logging.basicConfig(level=logging.INFO)


async def send_message():
    try:
        message = redis.receive_from_queue()
        if not message or "content" not in message or not isinstance(message["content"], str):
            logging.error("Ошибка: Нет контента или неверный формат данных.")
            return

        logging.info(message["content"])

        path_media, media = await asyncio.to_thread(
            file_manager.download_media_files,
            channel=message["channel"],
            id_post=message["id_post"]
        )

        if not path_media:
            logging.error("Ошибка: Не удалось загрузить медиафайлы.")
            await bot.send_message(message=message["content"])
        else:
            list_media = bot.prepare_media(media, message["content"])
            if not list_media:
                logging.error("Ошибка: Не удалось подготовить медиафайлы.")
                await bot.send_message(message=message["content"])
            else:
                media_chunk = list_media[:10]
                await bot.send_media_group(media=media_chunk)

    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}")

async def main() -> None:
    while True:
        await send_message()

if __name__ == '__main__':
    file_manager = FileManager()
    bot = TelegramBot()
    bot.start()
    asyncio.run(main())

