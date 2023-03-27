from telebot.types import ReplyKeyboardMarkup


def yes_no() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру для ответов да или нет.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row('Да', 'Нет')
    return keyboard