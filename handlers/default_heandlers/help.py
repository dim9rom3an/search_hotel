from telebot.types import Message

from loader import bot
from log import logger
from config_data.config import DEFAULT_COMMANDS


@bot.message_handler(commands=['help'])
@logger.catch()
def bot_help(message: Message) -> None:
    """
    Хендлер, при вызове команды help.
    Отображает команду и действие, которое она может совершить.
    """
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, '\n'.join(text))
    bot.delete_state(message.from_user.id, message.chat.id)
