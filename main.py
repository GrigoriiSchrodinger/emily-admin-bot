import asyncio
import logging

from src.feature.bot.bot import TelegramBot
from src.service import redis, request_db, file_manager

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
                message_id = await bot.send_message(message=message, seed=message["seed"])
            else:
                list_media = bot.prepare_media(media, message["content"])
                if not list_media:
                    logging.error("Ошибка: Не удалось подготовить медиафайлы.")
                    message_id = await bot.send_message(message=message, seed=message["seed"])
                else:
                    media_chunk = list_media[:10]
                    message_id = await bot.send_media_group(media=media_chunk, message=message, seed=message["seed"])
        else:
            message_id = await bot.send_message(message=message, seed=message["seed"])

        request_db.create_send_news(channel=message["channel"], id_post=message["id_post"], message_id=message_id)
    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}")


async def main() -> None:
    while True:
        await send_message()


if __name__ == '__main__':
    bot = TelegramBot()
    bot.start()
    asyncio.run(main())
