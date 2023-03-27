"""
Содержит функции и хэндлеры команды history.
* message - сообщение от пользователя.
* from_user.id - индификационный номер пользователя.
* send_message - отправляет сообщение пользователю.
"""
from telebot.types import Message

from loader import bot
from log import logger
from database import database


@bot.message_handler(commands=['history'])
@logger.catch()
def history(message: Message) -> None:
    """
    Отлавливает команду history.
    Выводит результат из базы данных.
    """
    for data in database.find_hotel(message.from_user.id):
        text = 'Команда: {command}, Дата: {date}, Время: {time}, Город: {city}, Отель: {hotel}, Цена на ночь: {price}'.\
            format(command=data.command,
                   date=data.date_time.strftime('%Y-%m-%d'),
                   time=data.date_time.strftime('%H:%M:%S'),
                   city=data.city,
                   hotel=data.hotel,
                   price=data.price)
        bot.send_message(message.from_user.id, text)