from telebot.types import Message

from log import logger
from loader import bot


@bot.message_handler(state=None, time=1)
@logger.catch()
def bot_echo(message: Message) -> None:
    """
    Хендлер, куда летят текстовые сообщения без указанного состояния.
    """
    bot.reply_to(message, "Эхо без состояния или фильтра.\nСообщение:"
                          f"{message.text}")
