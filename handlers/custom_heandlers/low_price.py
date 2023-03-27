"""
Содержит функции и хэндлеры команды low_price.
* message - сообщение от пользователя.
* from_user.id - индификационный номер пользователя.
* chat.id - индификационный номер сообщения от пользователя.
* set_state - устанавливает новое состояние SearchToLowPrice.
* send_message - отправляет сообщение пользователю.
* retrieve_data - контекстный менеджер для хранения информации пользователей.
"""
from datetime import datetime, date
import re

from telebot.types import Message, CallbackQuery
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from loader import bot
from log import logger
from database import database
from keyboards.inline.choose_group import choose_place
from keyboards.reply.choose_answer import yes_no
from states.information_command_lowprice import SearchToLowPrice
from utils import surf_internet, print_text


@bot.message_handler(commands=['low_price'])
@logger.catch()
def low_price(message: Message) -> None:
    """
    Отлавливает команду low_price.
    """
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, SearchToLowPrice.city, message.chat.id)
    logger.info(f'{message.from_user.full_name} выбрал команду low_price')
    bot.send_message(message.from_user.id, 'Введите город, где будет проводиться поиск '
                                           '(на английском языке и кроме городов россии).')


@bot.message_handler(state=SearchToLowPrice.city)
@logger.catch()
def set_part_city(message: Message) -> None:
    """
    Отлавливает состояние пользователя SearchToLowPrice.city.
    * reply_markup - Выводит клавиатуру для выбора района.
    """
    city = message.text.title()
    logger.info(f'{message.from_user.full_name} выбрал город {city}')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
        city_group = surf_internet.search_group({"query": city})
        if city_group is None:
            bot.send_message(message.from_user.id, 'Попробуйте снова выбрать нужную команду.')
        if city_group[0]["name"] == city:
            bot.send_message(message.from_user.id, 'Уточните, пожалуйста.',
                             reply_markup=choose_place(city_group, 'l'))
            data_bot['city'] = city
        else:
            bot.send_message(message.from_user.id, 'Такого города не существует. Попробуйте еще раз.')


@bot.callback_query_handler(func=lambda call: call.data[-1] == 'l')
@logger.catch()
def callback_button(call: CallbackQuery) -> None:
    """
    Обработка кнопок районов города.
    """
    if call.message:
        if call.data:
            bot.answer_callback_query(callback_query_id=call.id)
            with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data_bot:
                data_bot['id_group'] = call.data[0:-1]
            logger.info(f'{call.from_user.full_name} выбрал destination_id: {call.data[0:-1]}')
            bot.send_message(call.message.chat.id,
                             'Введите количество отелей, которые необходимо вывести в результате (не больше 25).')
            bot.set_state(call.from_user.id, SearchToLowPrice.data_in, call.message.chat.id)


@bot.message_handler(state=SearchToLowPrice.data_in)
@logger.catch()
def cal_in(message: Message):
    """
    Отлавливает состояние пользователя SearchToLowPrice.data_in.
    Выводит календарь для выбора даты.
    """
    if message.text.isdigit():
        logger.info(f'{message.from_user.full_name} выбрал {message.text} отелей')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
            data_bot['quantity_hotel'] = int(message.text)
        calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today()).build()
        bot.send_message(message.from_user.id, 'Выберите дату начала проживания.')
        bot.send_message(message.from_user.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)
    else:
        bot.send_message(message.from_user.id, 'Вводятся только цифры')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
@logger.catch()
def set_date_in(call: CallbackQuery):
    """
    Обработка кнопок календаря.
    * calendar_id - номер календаря.
    * min_date - минимальное значения для отображения в календаре.
    * edit_message_text - заменяет календарь на выбранную дату.
    """
    result, key, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              call.from_user.id, call.message.message_id, reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}.",
                              call.from_user.id, call.message.message_id)
        bot.send_message(call.from_user.id, 'Верно (да или нет)?', reply_markup=yes_no())
        logger.info(f'{call.from_user.full_name} будет жить с {result}')
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data_bot:
            data_bot['data_in'] = result
        bot.set_state(call.from_user.id, SearchToLowPrice.data_out, call.message.chat.id)


@bot.message_handler(state=SearchToLowPrice.data_out)
@logger.catch()
def cal_out(message: Message):
    """
    Отлавливает состояние пользователя SearchToLowPrice.data_in.
    Выводит календарь для выбора даты.
    """
    if message.text.lower() == 'да':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
            calendar, step = DetailedTelegramCalendar(calendar_id=2, min_date=data_bot['data_in']).build()
            bot.send_message(message.from_user.id, 'Выберите дату завершения проживания.')
            bot.send_message(message.from_user.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)
    elif message.text.lower() == 'нет':
        calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today()).build()
        bot.send_message(message.from_user.id, 'Выберите дату начала проживания.')
        bot.send_message(message.from_user.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)
    else:
        bot.send_message(message.from_user.id, 'Введите да или нет.', reply_markup=yes_no())


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
@logger.catch()
def set_date_out(call: CallbackQuery):
    """
    Обработка кнопок календаря.
    * calendar_id - номер календаря.
    * min_date - минимальное значения для отображения в календаре.
    * edit_message_text - заменяет календарь на выбранную дату.
    """
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data_bot:
        result, key, step = DetailedTelegramCalendar(calendar_id=2,
                                                     min_date=data_bot['data_in']).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              call.from_user.id, call.message.message_id, reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}.",
                              call.from_user.id, call.message.message_id)
        bot.send_message(call.from_user.id, 'Верно (да или нет)?', reply_markup=yes_no())
        logger.info(f'{call.from_user.full_name} будет жить по {result}')
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data_bot:
            data_bot['data_out'] = result
        bot.set_state(call.from_user.id, SearchToLowPrice.inter_state, call.message.chat.id)


@bot.message_handler(state=SearchToLowPrice.inter_state)
@logger.catch()
def question_data(message: Message) -> None:
    """
    Отлавливает состояние пользователя SearchToLowPrice.inter_state.
    Промежуточное состояние о правильности даты.
    """
    if message.text.lower() == 'да':
        bot.set_state(message.from_user.id, SearchToLowPrice.question_bot, message.chat.id)
        bot.send_message(message.from_user.id, 'Нужны вам фотографии отелей (да/нет)? ', reply_markup=yes_no())
    elif message.text.lower() == 'нет':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
            calendar, step = DetailedTelegramCalendar(calendar_id=2, min_date=data_bot['data_in']).build()
            bot.send_message(message.from_user.id, 'Выберите дату завершения проживания.')
            bot.send_message(message.from_user.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)
    else:
        bot.send_message(message.from_user.id, 'Введите да или нет.' , reply_markup=yes_no())


@bot.message_handler(state=SearchToLowPrice.question_bot)
@logger.catch()
def question_photo(message: Message) -> None:
    """
    Отлавливает состояние пользователя SearchToLowPrice.question_bot.
    Выбираем нужны ли нам фотографии.
    """
    if message.text.lower() == 'да':
        bot.set_state(message.from_user.id, SearchToLowPrice.photo, message.chat.id)
        bot.send_message(message.from_user.id, 'Сколько фотографий одного отеля вам нужно (не больше 25)?')
    elif message.text.lower() == 'нет':
        bot.set_state(message.from_user.id, SearchToLowPrice.answer, message.chat.id)
        bot.send_message(message.from_user.id, 'Верная информация (да или нет)?', reply_markup=yes_no())
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
            data_bot['quantity_photo'] = 0
        bot.send_message(message.from_user.id, print_text.com_price_check(message))
    else:
        bot.send_message(message.from_user.id, 'Введите да или нет.', reply_markup=yes_no())


@bot.message_handler(state=SearchToLowPrice.photo)
@logger.catch()
def set_photo(message: Message) -> None:
    """
    Отлавливает состояние пользователя SearchToLowPrice.photo.
    Сохраняет, выбранное количество фотографий.
    Уточняет, запрошенную пользователем информацию.
    """
    if message.text.isdigit():
        bot.set_state(message.from_user.id, SearchToLowPrice.answer, message.chat.id)
        bot.send_message(message.from_user.id, 'Верная информация (да или нет)?', reply_markup=yes_no())
        logger.info(f'{message.from_user.full_name} выбрал {message.text} фотографий')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
            data_bot['quantity_photo'] = int(message.text)
        bot.send_message(message.from_user.id, print_text.com_price_check(message))
    else:
        bot.send_message(message.from_user.id, 'Нужно вводить только цифры.')


@bot.message_handler(state=SearchToLowPrice.answer)
@logger.catch()
def send_info(message: Message) -> None:
    """
    Отлавливает состояние пользователя SearchToLowPrice.answer.
    Выводит, запрошенную информацию пользователем
    * send_media_group - отправляет группу фотографий пользователю.
    * delete_state - удаляет состояние пользователя.
    """
    if message.text.lower() == 'да':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
            delta_date = data_bot['data_out'] - data_bot['data_in']
            hotels = surf_internet.search_hotel({"destinationId": data_bot['id_group'],
                                                 "sortOrder": "PRICE"}, data_bot['quantity_hotel'], True)
            for hotel in hotels:
                text = print_text.com(hotel, delta_date.days)
                bot.send_message(message.chat.id, text, disable_web_page_preview=True)
                date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                database.add_command(message.from_user.id, date_time, 'low_price', data_bot['city'], hotel["name"],
                                     hotel["ratePlan"]["price"]["current"])
                if 'quantity_photo' in data_bot:
                    photos = surf_internet.search_photo({"id": hotel["id"]}, data_bot['quantity_photo'])
                    bot.send_media_group(message.from_user.id, photos)
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.from_user.id, 'Поиск завершен.')
    elif message.text.lower() == 'нет':
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.from_user.id, 'Попробуйте выбрать нужную команду.')
    else:
        bot.send_message(message.from_user.id, 'Введите да или нет.', reply_markup=yes_no())