from sqlalchemy import select, update, delete, insert
from sqlalchemy.sql import ClauseElement
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import EmailStr

from migration.models import User
from database import async_session_maker

from typing import Generic, TypeVar, Type


T = TypeVar("T")


class BaseDAO(Generic[T]):
    """Базовый класс взаимодействия с данными."""
    
    model: Type[T]
    
    @classmethod
    async def _find_data_where(cls, *conditions: ClauseElement) -> T | None:
        """
        Находит данные в базе данных.

        Args:
            conditions: условия для поиска данных.
        
        Returns:
            Объект данных или None, если объект не найден.
        """

        async with async_session_maker() as session:
            query = select(cls.model).where(*conditions)
            result = await session.execute(query)

            return result.scalars().first()

    @classmethod
    async def _add_data(cls, **values) -> None:
        """
        Добавляет данные в базу данных.

        Args:
            values: словарь с данными для добавления.
                    
                    Ключи должны соответствовать атрибутам ORM-модели.
                    Допустимый набор полей определяется конкретным DAO.
        
        Raises:
            IntegrityError - если добавляются данные, которые уже есть в базе.
            SQLAlchemyError - если возникла ошибка при добавлении.
        """

        async with async_session_maker() as session:
            query = insert(cls.model).values(**values)
            try:
                await session.execute(query)
                await session.commit()
            except IntegrityError as error:
                await session.rollback()
                raise error
            except SQLAlchemyError as error:
                await session.rollback()
                raise error

    @classmethod
    async def _update_data_where(
        cls, 
        *conditions: ClauseElement, 
        **values
    ) -> None:
        """
        Обновляет данные в базе данных.

        Args:
            conditions: набор условий.
            values: словарь с полями и значениями для обновления.
                    
                    Ключи должны соответствовать атрибутам ORM-модели.
                    Допустимый набор полей определяется конкретным DAO.

        Raises:
            SQLAlchemyError - если возникла ошибка при обновлении.
        """

        async with async_session_maker() as session:
            query = update(cls.model).where(*conditions).values(**values)
            try:
                await session.execute(query)
                await session.commit()
            except SQLAlchemyError as error:
                await session.rollback()
                raise error

    @classmethod
    async def _delete_data_where(cls, *conditions: ClauseElement) -> None:
        """
        Удаляет данные из базы данных.

        Args:
            conditions: набор условий.
        
        Raises:
            SQLAlchemyError - если возникла ошибка при удалении.
        """

        async with async_session_maker() as session:
            query = delete(cls.model).where(*conditions)
            try:
                await session.execute(query)
                await session.commit()
            except SQLAlchemyError as error:
                await session.rollback()
                raise error
        
        
class UsersDAO(BaseDAO[User]):
    """Класс взаимодействия с данными таблицы users.""" 

    model = User

    @classmethod
    async def add_user(
        cls, 
        username: str, 
        password: str, 
        email: EmailStr
    ) -> None:
        """
        Добавляет пользователя в базу данных.

        Args:
            username: имя пользователя.
            password: хэшированный пароль пользователя.
            email: электронная почта пользователя.

        Raises:
            IntegrityError - если добавляются данные, которые уже есть в базе.
            SQLAlchemyError - если возникла ошибка при добавлении. 
        """

        await super()._add_data(
            username=username,
            email=email,
            password=password,
        )

    @classmethod
    async def find_user(cls, email: EmailStr) -> User | None:
        """
        Находит пользователя в базе данных.

        Args: 
            email: электронная почта пользователя.
        
        Returns:
            Объект пользователя или None, если пользователь не найден.
        """

        return await super()._find_data_where(cls.model.email == email)
    
    @classmethod
    async def delete_user(cls, email: EmailStr) -> None:
        """
        Удаляют пользователя из базы данных.

        Args:
            email: электронная почта пользователя.
        
        Raises:
            SQLAlchemyError - если при удалении возникла ошибка.
        """
        
        await super()._delete_data_where(cls.model.email == email)