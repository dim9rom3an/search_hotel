from peewee import SqliteDatabase, Model
from peewee import AutoField, DateTimeField, TextField, SmallIntegerField

from log import logger

db = SqliteDatabase('Hotels.db')


class BaseModel(Model):
    class Meta:
        database = db


class History(BaseModel):
    """
    Создает поля у базы данных.
    * id - обязательное поле. Нормируется по порядку.
    * user_id - id пользователя.
    * command - команда вводимая пользователем.
    * city - город, в каком проводился поиск.
    * hotel - отели, полученные в результате.
    * price - цена за ночь в отеле.
    """
    id = AutoField(null=False)
    user_id = SmallIntegerField()
    date_time = DateTimeField()
    command = TextField()
    city = TextField()
    hotel = TextField()
    price = TextField()


@logger.catch()
def add_command(user_id: int, data: str, command: str, city: str, hotel: str, price: str) -> None:
    """
    Добавляет запись в базу данных.
    """
    History.create(user_id=user_id, date_time=data, command=command, city=city, hotel=hotel, price=price)


@logger.catch()
def find_hotel(user_id: int):
    """
    Выбирает записи из базы данных по id пользователю.
    """
    return History.select().where(History.user_id == user_id)


History.create_table()