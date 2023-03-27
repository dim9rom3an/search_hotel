import json
import re

from requests import Response, get, codes, TooManyRedirects
from telebot.types import InputMediaPhoto

from log import logger
from config_data import config
from utils.sort import sort_distance


@logger.catch()
def request_to_api(url: str, headers: dict, querystring: dict) -> Response:
    """
    Делает запрос с сайта по ссылке url, с параметрами headers и querystring.
    Возвращает, полученные данные с сайта, в формате JSON.
    """
    try:
        response = get(url, headers=headers, params=querystring, timeout=15)
        if response.status_code == codes.ok:
            return response
    except TooManyRedirects:
        logger.exception('Превышено время ожидания ответа от сервера.')
    except ConnectionError:
        logger.exception('Неполадки с сервером.')


@logger.catch()
def search_group(data: dict) -> dict:
    """
    Обрабатывает запрос по выбранной локации и находит группу отелей.
    Возвращает словарь со списком районов города.
    * data - параметры поиска по сайту
    """
    pattern = r'(?<="CITY_GROUP",).*?[\]]'
    info_internet = request_to_api(url=config.url_search_group, headers=config.headers, querystring=data)
    info = re.search(pattern, info_internet.text)
    if info:
        result = json.loads(f"{{{info[0]}}}")
        city_group = result['entities']
        main_city = city_group[0]["name"]
        for city in city_group:
            info_group = ''.join(re.findall(r'<.*>', city["caption"])) \
                if re.search(r'<.*>', city["caption"]) else 'пусто'
            if f' {main_city}' in city["caption"].split(','):
                city["caption"] = re.sub(info_group, '', city["caption"])
            else:
                city["caption"] = re.sub(info_group, main_city, city["caption"])
        return city_group


@logger.catch()
def search_hotel(data: dict, num_hotels: int, command: bool, dis_min: float = 0, dis_max: float = 0) -> list:
    """
    Обрабатывает запрос, и предоставляет ответ с точной информацией по отелям.
    Возвращает список отелей, определенного количества.
    * data - параметры поиска по сайту.
    * num_hotels - количество отелей для вывода.
    * bool - команда, выбранная пользователем (low - True, high - True, best - False)
    * dis_min - минимальное расстояние до центра (по умолчанию значение равно 0).
    * dis_max - максимальное расстояние до центра (по умолчанию значение равно 0).
    """
    choose_hotel = list()
    info_internet = request_to_api(url=config.url_search_hotel, headers=config.headers, querystring=data)
    info = json.loads(info_internet.text)
    hotels = info["data"]["body"]["searchResults"]["results"]
    if len(hotels) < num_hotels:
        num_hotels = len(hotels)
    if command:
        logger.info('попал')
        for ind in range(num_hotels):
            choose_hotel.append(hotels[ind])
        return choose_hotel
    else:
        hotels_sort = sort_distance(hotels, dis_min, dis_max)
        for ind in range(num_hotels):
            choose_hotel.append(hotels_sort[ind])
        return choose_hotel


@logger.catch()
def search_photo(data: dict, num_photo: int) -> list:
    """
    Обрабатывает запрос по фотографиям, выбранного отеля.
    Возвращает список фотографий.
    * data - параметры поиска по сайту.
    * num_photo - количество нужных фото.
    """
    text_photo = request_to_api(url=config.url_search_photo, headers=config.headers, querystring=data)
    photo_list = list()
    info = json.loads(text_photo.text)
    for ind, fail in enumerate(info["hotelImages"]):
        if ind == num_photo:
            break
        photo = re.sub(r'_{.*}', '', fail["baseUrl"])
        ph = InputMediaPhoto(photo)
        photo_list.append(ph)
    return photo_list
