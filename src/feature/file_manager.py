import logging
import os
import zipfile
from io import BytesIO

import requests

from src.conf import URL_DOWNLOAD


class FileManager:
    def __init__(self, url_download: str = URL_DOWNLOAD):
        self.url_download = url_download

    @staticmethod
    def extract_files(zip_data: BytesIO, channel: str, id_post: int) -> tuple[str, list[str]]:
        """Извлекает файлы из ZIP-архива."""
        base_dir = os.path.join('media', channel, str(id_post))
        os.makedirs(base_dir, exist_ok=True)

        with zipfile.ZipFile(zip_data) as zip_ref:
            zip_ref.extractall(base_dir)

        files = [os.path.join(root, filename) for root, _, filenames in os.walk(base_dir) for filename in filenames]
        logging.info(f"Файлы успешно скачаны и распакованы в {base_dir}")
        return base_dir, files

    def handle_response(self, response, channel: str, id_post: int) -> tuple[str, list[str]]:
        if response.status_code == 200:
            zip_data = BytesIO(response.content)
            return self.extract_files(zip_data, channel, id_post)
        else:
            error_detail = response.json().get('detail', 'Неизвестная ошибка')
            logging.error(f"Ошибка при скачивании: {error_detail}")
            return "", []

    def download_media_files(self, channel: str, id_post: int) -> tuple[str, list[str]]:
        """Скачивает медиафайлы поста и сохраняет их в отдельную папку."""
        url = f"http://emily-database-handler:8000/media/download/{id_post}/{channel}"
        try:
            response = requests.post(url)
            return self.handle_response(response, channel, id_post)
        except requests.RequestException as e:
            logging.error(f"Ошибка запроса: {str(e)}")
        except Exception as e:
            logging.error(f"Произошла ошибка: {str(e)}")
        return "", []