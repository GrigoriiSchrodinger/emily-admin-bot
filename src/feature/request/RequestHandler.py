from typing import Optional

import requests
from pydantic import BaseModel, ValidationError

from src.feature.request.schemas import DetailByChannelIdPost, DetailBySeed, DetailBySeedResponse, \
    ToggleMediaResolution, ToggleMediaResolutionResponse, SendPost, GetRelatedNews, GetRelationshipIdMessage
from src.service_url import get_url_emily_database_handler


class RequestHandler:
    def __init__(self, base_url=get_url_emily_database_handler(), headers=None, timeout=10):
        """
        Инициализация класса для работы с запросами.

        :param base_url: Базовый URL для запросов
        :param headers: Заголовки для запросов (по умолчанию None)
        :param timeout: Тайм-аут для запросов (по умолчанию 10 секунд)
        """
        self.base_url = base_url
        self.headers = headers if headers is not None else {}
        self.timeout = timeout

    def get(
            self, endpoint: str, path_params: Optional = None, query_params: Optional = None,
            response_model: Optional = None
    ):
        """
        Выполняет GET-запрос к указанному endpoint.

        :param query_params:
        :param path_params:
        :param response_model:
        :param endpoint: Путь к ресурсу относительно base_url
        :return: Ответ сервера в формате JSON (если есть) или текстовый ответ
        """
        # Формируем URL с подстановкой параметров пути
        if path_params:
            endpoint = endpoint.format(**path_params.dict())

        url = f"{self.base_url}/{endpoint}"

        try:
            # Преобразуем параметры запроса в словарь
            query_params_dict = query_params.dict() if query_params else None
            response = requests.get(url, headers=self.headers, params=query_params_dict, timeout=self.timeout)
            response.raise_for_status()

            # Обрабатываем ответ с использованием модели
            data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            return response_model.parse_obj(data) if response_model else data
        except requests.exceptions.RequestException as e:
            print(f"Ошибка GET-запроса: {e}")
            return None
        except ValidationError as ve:
            print(f"Ошибка валидации данных ответа: {ve}")
            return None

    def post_files(self, endpoint: str) -> dict:
        # if path_params:
        #     endpoint = endpoint.format(**path_params.dict())
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: Optional[BaseModel] = None, response_model: Optional = None):
        """
            Выполняет POST-запрос к указанному endpoint.

            :param self:
            :param response_model:
            :param endpoint: Путь к ресурсу относительно base_url
            :param data: Данные для отправки в формате form-encoded (по умолчанию None)
            :return: Ответ сервера в формате JSON (если есть) или текстовый ответ
            """
        url = f"{self.base_url}/{endpoint}"
        try:
            data_dict = data.dict() if data else None
            response = requests.post(url, headers=self.headers, json=data_dict, timeout=self.timeout)
            response.raise_for_status()

            data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            return response_model.parse_obj(data) if response_model else data
        except requests.exceptions.RequestException as e:
            print(f"Ошибка POST-запроса: {e}")
            return None
        except ValidationError as ve:
            print(f"Ошибка валидации данных ответа: {ve}")
            return None

    def set_headers(self, headers):
        """
        Устанавливает или обновляет заголовки для запросов.

        :param self:
        :param headers: Словарь с заголовками
        """
        self.headers.update(headers)

    def set_timeout(self, timeout):
        """
        Устанавливает тайм-аут для запросов.

        :param self:
        :param timeout: Тайм-аут в секундах
        """
        self.timeout = timeout


class RequestDataBase(RequestHandler):
    def __get_detail_by_seed__(self, seed: str):
        seed_req = DetailBySeed(
            seed=seed
        )
        return self.get(
            endpoint='all-news/detail-by-seed/{seed}',
            path_params=seed_req,
            response_model=DetailBySeedResponse
        )

    def get_detail_news_by_channel_id_post(self, channel: str, id_post: int):
        details = DetailByChannelIdPost(
            channel=channel,
            id_post=id_post
        )
        return self.get(endpoint="all-news/detail-by-channel-id_post/{channel}/{id_post}", path_params=details)

    def get_detail_by_seed(self, seed: str) -> DetailBySeedResponse:
        return self.__get_detail_by_seed__(seed=seed)

    def get_media_resolution(self, seed: str):
        data = ToggleMediaResolution(
            seed=seed
        )
        return self.post(
            endpoint='setting/toggle-media-resolution-by-seed',
            data=data,
            response_model=ToggleMediaResolutionResponse
        ).media_resolution

    def create_send_news(self, channel: str, id_post: int, message_id: int):
        data = SendPost(
            channel=channel,
            id_post=id_post,
            message_id=message_id
        )
        self.post(endpoint="send-news/create", data=data)

    def get_related_news(self, seed: str) -> GetRelationshipIdMessage:
        data = GetRelatedNews(seed=seed)
        response = self.get(
            endpoint='/all-news/related-news/{seed}',
            path_params=data,
            response_model=GetRelationshipIdMessage
        )
        return response