from telebot.handler_backends import State, StatesGroup

from log import logger


@logger.catch()
class SearchToBestDeal(StatesGroup):
    """
    Класс состояний пользователя при вводе команды best_deal
    """
    city = State()
    hotel = State()
    data_in = State()
    data_out = State()
    low_pr = State()
    high_pr = State()
    small_dist = State()
    big_dist = State()
    inter_state = State()
    answer = State()
    photo = State()
    question_bot = State()