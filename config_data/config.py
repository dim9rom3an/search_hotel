import os

from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')

DEFAULT_COMMANDS = (
    ('help', "Вывести справку"),
    ('low_price', 'вывод самых дешёвых отелей в городе'),
    ('high_price', 'вывод самых дорогих отелей в городе'),
    ('best_deal', 'вывод отелей, наиболее подходящих по цене и расположению от центра'),
    ('history', 'вывод истории поиска отелей')
)

headers = {
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

url_search_group = "https://hotels4.p.rapidapi.com/locations/v2/search"
url_search_hotel = "https://hotels4.p.rapidapi.com/properties/list"
url_search_photo = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
