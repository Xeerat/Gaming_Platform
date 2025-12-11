from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from app.migration.models import User, Map, Character
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.database import DB_URL

#=========================================================
# Создание асинхронных сессий 
#=========================================================

# Создаем асинхронный движок подключенный к базе данных
engine = create_async_engine(DB_URL)
# Создаем фабрику для создания асинхронных сессий
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

#=========================================================
# Базовый класс для работы с данными
#=========================================================

class BaseDAO:
    """ Класс представляющий базовое взаимодействие с данными таблиц """
    # У базовой DAO нет модели
    model = None
    
    @classmethod
    async def find_one_or_none(cls, **filter_by):
        """ Функция для нахождения записи по критерию """
        # Создаем новую сессию
        async with async_session_maker() as session:
            # sql-запрос вида: SELECT * FROM users WHERE
            query = select(cls.model).filter_by(**filter_by)
            # Отправляем запрос в базу данных
            result = await session.execute(query)
            # Вернет либо один объект, либо None
            return result.scalar_one_or_none()
        

    @classmethod
    async def add(cls, **values):
        """ Функция для добавления нового объекта в базу данных """
        async with async_session_maker() as session:
            # Создаем модель класса с переданными параметрами
            new_instance = cls.model(**values)
            # Добавляем изменения 
            session.add(new_instance)
            # Пытаемся закомитить 
            try:
                await session.commit()
            # Иначе откат изменений 
            except SQLAlchemyError as error:
                await session.rollback()
                raise error
            # Для корректной работы id в таблице нужно возвращать объект
            return new_instance


    @classmethod
    async def update(cls, filter_by, **values):
        """ Функция для обновления значений объектов в базе данных """
        async with async_session_maker() as session:
            query = (
                # UPDATE users
                sqlalchemy_update(cls.model)
                # WHERE id=5
                .where(*[getattr(cls.model, k) == v for k, v in filter_by.items()])
                # SET username='maria', email='m@e.com'
                .values(**values)
            )
            result = await session.execute(query)
            try:
                await session.commit()
            except SQLAlchemyError as error:
                await session.rollback()
                raise error
            # Возращает количество обновленных строк
            return result.rowcount


    @classmethod
    async def delete(cls, delete_all: bool = False, **filter_by):
        """ Функция для удаления объектов из базы данных """
        if not delete_all and not filter_by:
            raise ValueError("Необходимо указать хотя бы один параметр для удаления.")

        async with async_session_maker() as session:
            # DELETE FROM users WHERE username='maria'
            query = sqlalchemy_delete(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            try:
                await session.commit()
            except SQLAlchemyError as error:
                await session.rollback()
                raise error
            return result.rowcount
        
#=========================================================
# Класс для работы с данными таблицы users
#=========================================================

class UsersDAO(BaseDAO):
    """ Класс представляющий взаимодействие с данными таблицы users """
    model = User


class MapsDAO(BaseDAO) :
    model = Map

class CharDAO(BaseDAO) :
    model = Character