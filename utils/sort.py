import re

from log import logger


@logger.catch()
def sort_distance(hotels: list, dis_min: float, dis_max: float) -> list:
    """
    Сортирует отели по расстоянию от центра, в диапазоне введенном пользователем.
    Возвращает список, отсортированных отелей по диапазону нужной дистанции от центра.
    Если в описании отеля не имеется расстояние до центра, то возвращает обратно изначальный список отелей.
    * hotels - список отелей, полученных в ходе запроса.
    * dis_min - минимальное расстояние до центра.
    * dis_max - максимальное расстояние до центра.
    """
    sort_dis_hotel = list()
    for hotel in hotels:
        if "City center" in hotel["landmarks"][0]["label"]:
            mile = float(hotel["landmarks"][0]["distance"][:3])
            if dis_min <= mile <= dis_max:
                sort_dis_hotel.append(hotel)
    if len(sort_dis_hotel) != 0:
        logger.info('sort_dis_hotel')
        return sort_dis_hotel
    else:
        logger.info('hotels')
        return hotels


def check_number(number: str) -> bool:
    """
    Проверяет соответствие числа, вводимого пользователем.
    Возвращает True при соответствии или False при несоответствии.
    """
    if len(re.findall(r'\d,\d', number)) != 0:
        return True
    else:
        return False