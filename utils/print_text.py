import re

from telebot.types import Message

from log import logger
from loader import bot


@logger.catch()
def change_place(hotel: dict) -> str:
    """
    Проверяет есть ли расстояние до центра в описании отеле или нет.
    Возвращает строку с расстоянием до центра или информирует, что его в описании отеля нет.
    * hotel - один из выбранных отелей.
    """
    if "City center" in hotel["landmarks"][0]["label"]:
        distance = hotel["landmarks"][0]["distance"][:3]
        return f'Расстояние до центра {distance} миль.'
    else:
        return f'Расстояние до центра не известно'


@logger.catch()
def com(hotel: dict, day: int) -> str:
    """
    Создает текст для вывода информации об отеле.
    Возвращает текстовое сообщение.
    * hotel - Подробная информация об отеле.
    * day - количество дней проживания пользователя в отеле.
    """
    price = re.search(r'\d+', hotel["ratePlan"]["price"]["current"]).group()
    res = day * int(price)
    text = 'Отель: {name}\n' \
           'Адрес: {address}\n' \
           '{place}\n' \
           'Стоимость: за одну ночь {price}, за {day} ночей ${res}\n' \
           'Ссылка на карточку отеля {url}'.format(name=hotel["name"],
                                                   address=hotel["address"]["streetAddress"]
                                                   if hotel["address"].get("streetAddress") else hotel["address"][
                                                       "locality"],
                                                   place=change_place(hotel),
                                                   price=hotel["ratePlan"]["price"]["current"],
                                                   day=day,
                                                   res=res,
                                                   url=f'https://www.hotels.com/ho{hotel["id"]}')
    return text


@logger.catch()
def com_price_check(message: Message) -> str:
    """
    Создает текст для уточнения информации, вводимой пользователем.
    Возвращает текстовое сообщение.
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
        text = 'Город: {city}\n' \
               'Количество отелей: {num_hostel}\n' \
               'Количество фотографий: {num_photo}\n ' \
               'Дата заезда: {hotel_in}\n ' \
               'Дата выезда: {hotel_out}'.format(city=data_bot['city'],
                                                 num_hostel=data_bot['quantity_hotel'],
                                                 num_photo=data_bot['quantity_photo'],
                                                 hotel_in=data_bot['data_in'],
                                                 hotel_out=data_bot['data_out'])
    return text


@logger.catch()
def com_best_deal_check(message: Message) -> str:
    """
    Создает текст для уточнения информации, вводимой пользователем.
    Возвращает текстовое сообщение.
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
        text = 'Город: {city}\n' \
               'Минимальная стоимость: {min_price}\n' \
               'Максимальная стоимость: {max_price}\n' \
               'Минимальное расстояние до центра города: {min_dis}\n' \
               'Максимальная расстояние до центра города: {max_dis}\n' \
               'Количество отелей: {num_hostel}\n' \
               'Количество фотографий: {num_photo}\n ' \
               'Дата заезда: {hotel_in}\n ' \
               'Дата выезда: {hotel_out}'.format(city=data_bot['city'],
                                                 min_price=data_bot['price_min'],
                                                 max_price=data_bot['price_max'],
                                                 min_dis=data_bot['dis_min'],
                                                 max_dis=data_bot['dis_max'],
                                                 num_hostel=data_bot['quantity_hotel'],
                                                 num_photo=data_bot['quantity_photo'],
                                                 hotel_in=data_bot['data_in'],
                                                 hotel_out=data_bot['data_out'])
    return text

