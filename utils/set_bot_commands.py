from telebot.types import BotCommand

from log import logger
from config_data.config import DEFAULT_COMMANDS


@logger.catch()
def set_default_commands(bot):
    """
    Устанавливает выбор команд для пользователя.
    """
    bot.set_my_commands(
        [BotCommand(*i) for i in DEFAULT_COMMANDS]
    )