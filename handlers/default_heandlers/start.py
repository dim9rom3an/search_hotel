from telebot.types import Message

from log import logger
from loader import bot


@bot.message_handler(commands=['start'])
@logger.catch()
def bot_start(message: Message) -> None:
    """
    Хендлер приветствия пользователя.
    """
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!")

