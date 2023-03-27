"""
Содержит функции и хэндлеры команды best_deal.
* message - сообщение от пользователя.
* from_user.id - индификационный номер пользователя.
* chat.id - индификационный номер сообщения от пользователя.
* set_state - устанавливает новое состояние SearchToLowPrice.
* send_message - отправляет сообщение пользователю.
* retrieve_data - контекстный менеджер для хранения информации пользователей.
"""
from datetime import datetime, date

from telebot.types import Message, CallbackQuery
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from loader import bot
from log import logger
from database import database
from keyboards.inline.choose_group import choose_place
from keyboards.reply.choose_answer import yes_no
from states.information_command_bestdeal import SearchToBestDeal
from utils import surf_internet, print_text, sort


@bot.message_handler(commands=['best_deal'])
@logger.catch()
def high_price(message: Message) -> None:
    """
    Отлавливает команду best_deal.
    """
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, SearchToBestDeal.city, message.chat.id)
    logger.info(f'{message.from_user.full_name} выбрал команду best_deal')
    bot.send_message(message.from_user.id, 'Введите город, где будет проводиться поиск '
                                           '(на английском языке и кроме городов россии).')


@bot.message_handler(state=SearchToBestDeal.city)
@logger.catch()
def set_part_city(message: Message) -> None:
    """
    Отлавливает состояние пользователя SearchToLowPrice.city.
    * reply_markup - Выводит клавиатуру для выбора района.
    """
    city = message.text.title()
    logger.info(f'{message.from_user.full_name} выбрал город {city}')
    city_group = surf_internet.search_group({"query": city})
    if city_group is None:
        bot.send_message(message.from_user.id, 'Попробуйте снова выбрать нужную команду.')
    if city_group[0]["name"] == city:
        bot.send_message(message.from_user.id, 'Уточните, пожалуйста.',
                         reply_markup=choose_place(city_group, 'b'))
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
            data_bot['city'] = city
    else:
        bot.send_message(message.from_user.id, 'Такого города не существует. Попробуйте еще раз.')


@bot.callback_query_handler(func=lambda call: call.data[-1] == 'b')
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
            bot.set_state(call.from_user.id, SearchToBestDeal.data_in, call.message.chat.id)


@bot.message_handler(state=SearchToBestDeal.data_in)
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
        calendar, step = DetailedTelegramCalendar(calendar_id=5, min_date=date.today()).build()
        bot.send_message(message.from_user.id, 'Выберите дату начала проживания.')
        bot.send_message(message.from_user.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)
    else:
        bot.send_message(message.from_user.id, 'Вводятся только цифры')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=5))
@logger.catch()
def set_date_in(call: CallbackQuery):
    """
    Обработка кнопок календаря.
    * calendar_id - номер календаря.
    * min_date - минимальное значения для отображения в календаре.
    * edit_message_text - заменяет календарь на выбранную дату.
    """
    result, key, step = DetailedTelegramCalendar(calendar_id=5, min_date=date.today()).process(call.data)
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
        bot.set_state(call.from_user.id, SearchToBestDeal.data_out, call.message.chat.id)


@bot.message_handler(state=SearchToBestDeal.data_out)
@logger.catch()
def cal_out(message: Message):
    """
    Отлавливает состояние пользователя SearchToLowPrice.data_in.
    Выводит календарь для выбора даты.
    """
    if message.text.lower() == 'да':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
            calendar, step = DetailedTelegramCalendar(calendar_id=6, min_date=data_bot['data_in']).build()
            bot.send_message(message.from_user.id, 'Выберите дату завершения проживания.')
            bot.send_message(message.from_user.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)
    elif message.text.lower() == 'нет':
        calendar, step = DetailedTelegramCalendar(calendar_id=5, min_date=date.today()).build()
        bot.send_message(message.from_user.id, 'Выберите дату начала проживания.')
        bot.send_message(message.from_user.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)
    else:
        bot.send_message(message.from_user.id, 'Введите да или нет.', reply_markup=yes_no())


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=6))
@logger.catch()
def set_date_out(call: CallbackQuery):
    """
    Обработка кнопок календаря.
    * calendar_id - номер календаря.
    * min_date - минимальное значения для отображения в календаре.
    * edit_message_text - заменяет календарь на выбранную дату.
    """
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data_bot:
        result, key, step = DetailedTelegramCalendar(calendar_id=6,
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
        bot.set_state(call.from_user.id, SearchToBestDeal.inter_state, call.message.chat.id)


@bot.message_handler(state=SearchToBestDeal.inter_state)
@logger.catch()
def question_data(message: Message) -> None:
    """
    Отлавливает состояние пользователя SearchToLowPrice.inter_state.
    Промежуточное состояние о правильности даты.
    """
    if message.text.lower() == 'да':
        bot.set_state(message.from_user.id, SearchToBestDeal.low_pr, message.chat.id)
        bot.send_message(message.from_user.id, 'По какой минимальной цене вы ищите отель (в $)?')
    elif message.text.lower() == 'нет':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
            calendar, step = DetailedTelegramCalendar(calendar_id=6, min_date=data_bot['data_in']).build()
            bot.send_message(message.from_user.id, 'Выберите дату завершения проживания.')
            bot.send_message(message.from_user.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)
    else:
        bot.send_message(message.from_user.id, 'Введите да или нет.', reply_markup=yes_no())


@bot.message_handler(state=SearchToBestDeal.low_pr)
@logger.catch()
def set_low_pr(message: Message) -> None:
    """
    Отлавливает состояние пользователя SearchToLowPrice.low_pr.
    Устанавливает минимальную цену для поиска отелей.
    """
    if message.text.isdigit():
        bot.set_state(message.from_user.id, SearchToBestDeal.high_pr, message.chat.id)
        bot.send_message(message.from_user.id, 'По какой максимальной цене вы ищите отель (в $)?')
        logger.info(f'{message.from_user.full_name} выбрал мин. цену: {message.text}')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
            data_bot['price_min'] = int(message.text)
    else:
        bot.send_message(message.from_user.id, 'Нужно вводить только цифры.')


@bot.message_handler(state=SearchToBestDeal.high_pr)
@logger.catch()
def set_high_pr(message: Message) -> None:
    """
    Отлавливает состояние пользователя SearchToLowPrice.high_pr.
    Устанавливает максимальную цену для поиска отелей.
    """
    if message.text.isdigit():
        bot.set_state(message.from_user.id, SearchToBestDeal.small_dist, message.chat.id)
        bot.send_message(message.from_user.id, 'Какое минимальное расстояние от отеля до центра города '
                                               '(в милях через запятую)?')
        logger.info(f'{message.from_user.full_name} выбрал макс. цену: {message.text}')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
            data_bot['price_max'] = int(message.text)
    else:
        bot.send_message(message.from_user.id, 'Нужно вводить только цифры.')


@bot.message_handler(state=SearchToBestDeal.small_dist)
@logger.catch()
def set_min_dis(message: Message) -> None:
    """
    Отлавливает состояние пользователя SearchToLowPrice.small_dist.
    Устанавливает минимальное расстояние до центра города для поиска отелей.
    """
    if sort.check_number(message.text):
        bot.set_state(message.from_user.id, SearchToBestDeal.big_dist)
        bot.send_message(message.from_user.id, 'Какое максимальное расстояние от отеля до центра города '
                                               '(в милях через запятую)?')
        logger.info(f'{message.from_user.full_name} выбрал мин. расстояние: {message.text}')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
            data_bot['dis_min'] = float(message.text.replace(',', '.'))
    else:
        bot.send_message(message.from_user.id, 'Нужно вводить только цифры и через запятую.')


@bot.message_handler(state=SearchToBestDeal.big_dist)
@logger.catch()
def set_min_dis(message: Message) -> None:
    """
    Отлавливает состояние пользователя SearchToLowPrice.big_dist.
    Устанавливает максимальное расстояние до центра города для поиска отелей.
    """
    if sort.check_number(message.text):
        bot.set_state(message.from_user.id, SearchToBestDeal.question_bot)
        bot.send_message(message.from_user.id, 'Нужны вам фотографии отелей (да/нет)?', reply_markup=yes_no())
        logger.info(f'{message.from_user.full_name} выбрал макс. расстояние: {message.text}')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
            data_bot['dis_max'] = float(message.text.replace(',', '.'))
    else:
        bot.send_message(message.from_user.id, 'Нужно вводить только цифры и через запятую.')


@bot.message_handler(state=SearchToBestDeal.question_bot)
@logger.catch()
def question_photo(message: Message) -> None:
    """
    Отлавливает состояние пользователя SearchToLowPrice.question_bot.
    Выбираем нужны ли нам фотографии.
    """
    if message.text.lower() == 'да':
        bot.set_state(message.from_user.id, SearchToBestDeal.photo, message.chat.id)
        bot.send_message(message.from_user.id, 'Сколько фотографий одного отеля вам нужно (не больше 25)?')
    elif message.text.lower() == 'нет':
        bot.set_state(message.from_user.id, SearchToBestDeal.answer, message.chat.id)
        bot.send_message(message.from_user.id, 'Верная информация (да или нет)?', reply_markup=yes_no())
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
            data_bot['quantity_photo'] = 0
        bot.send_message(message.from_user.id, print_text.com_best_deal_check(message))
    else:
        bot.send_message(message.from_user.id, 'Введите да или нет.', reply_markup=yes_no())


@bot.message_handler(state=SearchToBestDeal.photo)
@logger.catch()
def set_photo(message: Message) -> None:
    """
    Отлавливает состояние пользователя SearchToLowPrice.photo.
    Сохраняет, выбранное количество фотографий.
    Уточняет, запрошенную пользователем информацию.
    """
    if message.text.isdigit():
        bot.set_state(message.from_user.id, SearchToBestDeal.answer, message.chat.id)
        bot.send_message(message.from_user.id, 'Верная информация (да или нет)?', reply_markup=yes_no())
        logger.info(f'{message.from_user.full_name} выбрал {message.text} фотографий')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_bot:
            data_bot['quantity_photo'] = int(message.text)
        bot.send_message(message.from_user.id, print_text.com_best_deal_check(message))
    else:
        bot.send_message(message.from_user.id, 'Нужно вводить только цифры.')


@bot.message_handler(state=SearchToBestDeal.answer)
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
            param_search = {"destinationId": data_bot['id_group'], "priceMin": data_bot['price_min'],
                            "priceMax": data_bot['price_max'], "sortOrder": "DISTANCE_FROM_LANDMARK"}
            hotels = surf_internet.search_hotel(param_search, data_bot['quantity_hotel'], False,
                                                data_bot['dis_min'], data_bot['dis_max'])
            for hotel in hotels:
                text = print_text.com(hotel, delta_date.days)
                bot.send_message(message.chat.id, text, disable_web_page_preview=True)
                date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                database.add_command(message.from_user.id, date_time, 'best_deal', data_bot['city'], hotel["name"],
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