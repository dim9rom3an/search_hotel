from telebot import types

from log import logger


@logger.catch()
def choose_place(cities: dict, command: str) -> types.InlineKeyboardMarkup:
    """
    Создает клавиатуру.
    Возвращает клавиатуру с районами города.
    * cities - словарь группы по локации.
    * command - первая буква выбранной команды для дальнейшего отлавливания callback_query_handler.
    """
    buttons = list()
    for city in cities:
        callback = f'{city["destinationId"]}{command}'
        button = types.InlineKeyboardButton(text=city["caption"], callback_data=callback)
        buttons.append(button)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard
