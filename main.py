from telebot.custom_filters import StateFilter

from loader import bot
from log import logger
import handlers
from utils.set_bot_commands import set_default_commands
from database import database


if __name__ == '__main__':
    try:
        bot.add_custom_filter(StateFilter(bot))
        set_default_commands(bot)
        bot.infinity_polling()
    except Exception:
        logger.exception('Exception')





