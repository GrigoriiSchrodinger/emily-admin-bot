import asyncio
import logging

import requests

from src.feature.bot import TelegramBot
from src.feature.file_manager import FileManager
from src.feature.request.RequestHandler import RequestDataBase
from src.service import redis
from src.service_url import get_url_emily_database_handler

logging.basicConfig(level=logging.INFO)


async def send_message():
    try:
        message = redis.receive_from_queue()
        logging.info(message["seed"])

        detail_by_seed = request_db.get_detail_by_seed(message["seed"])
        message = {
            "content": detail_by_seed.new_content,
            "channel": detail_by_seed.channel,
            "id_post": detail_by_seed.id_post,
            "outlinks": detail_by_seed.outlinks,
            "seed": message["seed"],
            "media_resolution": detail_by_seed.media_resolution,
        }
        if message["media_resolution"]:
            path_media, media = await asyncio.to_thread(
                file_manager.download_media_files,
                channel=message["channel"],
                id_post=message["id_post"]
            )
            if not path_media:
                logging.error("Ошибка: Не удалось загрузить медиафайлы.")
                await bot.send_message(message=message)
            else:
                list_media = bot.prepare_media(media, message["content"])
                if not list_media:
                    logging.error("Ошибка: Не удалось подготовить медиафайлы.")
                    await bot.send_message(message=message)
                else:
                    media_chunk = list_media[:10]
                    await bot.send_media_group(media=media_chunk, message=message)
        else:
            await bot.send_message(message=message)


        url = f"{get_url_emily_database_handler()}/send-news/create"
        data = {
            "channel": message["channel"],
            "id_post": message["id_post"]
        }
        requests.post(url, json=data)
    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}")

async def main() -> None:
    while True:
        await send_message()

if __name__ == '__main__':
    request_db = RequestDataBase()
    file_manager = FileManager()
    bot = TelegramBot()
    bot.start()
    asyncio.run(main())

