from telebot.handler_backends import State, StatesGroup

from log import logger


@logger.catch()
class SearchToLowPrice(StatesGroup):
    """
    Класс состояний пользователя при вводе команды low_price
    """
    city = State()
    hotel = State()
    data_in = State()
    data_out = State()
    inter_state = State()
    answer = State()
    photo = State()
    question_bot = State()