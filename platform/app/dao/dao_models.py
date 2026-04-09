from sqlalchemy import select, update, delete, insert
from sqlalchemy.sql import ClauseElement
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import EmailStr

from app.migration.models import User, Map, Sprite
from app.database import async_session_maker

from typing import Generic, TypeVar, Type, List


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
    async def _find_all_data_where(cls, *conditions: ClauseElement) -> list[T] | None:
        """
        Находит все данные в базе данных подходящие запросу.

        Args:
            conditions: условия для поиска данных.
        
        Returns:
            Список объектов данных или None, если объекты не найдены.
        """

        async with async_session_maker() as session:
            query = select(cls.model).where(*conditions)
            result = await session.execute(query)

            return result.scalars().all()

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
            TypeError - если были переданы некорректные значения.
        """

        async with async_session_maker() as session:
            query = insert(cls.model).values(**values)
            try:
                await session.execute(query)
                await session.commit()
            except (TypeError, IntegrityError, SQLAlchemyError) as error:
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

        Returns:
            True - если была обновлена хотя бы одна строка. False - иначе.

        Raises:
            SQLAlchemyError - если возникла ошибка при обновлении.
        """

        async with async_session_maker() as session:
            query = update(cls.model).where(*conditions).values(**values)
            try:
                result = await session.execute(query)
                await session.commit()
            except SQLAlchemyError as error:
                await session.rollback()
                raise error

            return result.rowcount > 0

    @classmethod
    async def _delete_data_where(cls, *conditions: ClauseElement) -> bool:
        """
        Удаляет данные из базы данных.

        Args:
            conditions: набор условий.
        
        Returns:
            True - если данные получилось удалить, иначе False.
        
        Raises:
            SQLAlchemyError - если возникла ошибка при удалении.
        """

        async with async_session_maker() as session:
            query = delete(cls.model).where(*conditions)
            try:
                result = await session.execute(query)
                await session.commit()
            except SQLAlchemyError as error:
                await session.rollback()
                raise error
            
            return result.rowcount > 0
        
        
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
    
        Returns:
            True - если получилось удалить пользователя, иначе False.
            
        Raises:
            SQLAlchemyError - если при удалении возникла ошибка.
        """
        
        return await super()._delete_data_where(cls.model.email == email)
    
    @classmethod
    async def update_user_password(
        cls,
        email: EmailStr,
        password: str
    ) -> None:
        """
        Меняет пароль в базе данных.

        Args:
            email: электронная почта пользователя.
            password: новый пароль.

        Returns:
            True - если была обновлена хотя бы одна строка. False - иначе.
            
        Raises:
            SQLAlchemyError - если возникла ошибка при обновлении.
        """

        return await super()._update_data_where(
            cls.model.email == email, 
            password=password
        )

class MapDAO(BaseDAO[Map]):
    """Класс взаимодействия с таблицей map"""

    model = Map

    @classmethod
    async def add_map(
        cls, 
        email: EmailStr, 
        mapname: str, 
        data: List[List[int]],
    ) -> None:
        """
        Добавляет карту в базу данных.

        Args:
            email: email пользователя.
            mapname: название карты.
            data: сама карта в виде матрицы.

        Raises:
            IntegrityError - если добавляются данные, которые уже есть в базе.
            SQLAlchemyError - если возникла ошибка при добавлении.
        """


        user = await UsersDAO.find_user(email)
        if not user :
            return
                
        await super()._add_data(
            user_id=user.id,
            mapname=mapname,
            data=data
        )

    @classmethod
    async def delete_map(
        cls, 
        email: EmailStr, 
        mapname: str, 
    ) -> None:
        """
        Удаляют карту из базы данных.

        Args:
            email: электронная почта пользователя.
            mapname: название карты, которую нужно удалить
    
        Returns:
            True - если получилось удалить карту, иначе False.
            
        Raises:
            SQLAlchemyError - если при удалении возникла ошибка.
        """

        user = await UsersDAO.find_user(email)

        if not user:
            return 
        
        return await super()._delete_data_where(
            cls.model.user_id == user.id,
            cls.model.mapname == mapname
        )
    
    @classmethod
    async def update_map(
        cls, 
        email: EmailStr, 
        mapname: str, 
        new_data: List[List[int]],
    ) -> None:
        """
        Обновляет карту в базе данных.

        Args:
            email: email пользователя.
            mapname: название карты.
            new_data: новая карта

        Raises:
            SQLAlchemyError - если возникла ошибка при добавлении.
        """

        user = await UsersDAO.find_user(email)

        if not user:
            return
        
        await super()._update_data_where(
            cls.model.user_id == user.id,
            cls.model.mapname == mapname,
            data = new_data
        )

    @classmethod
    async def find_all_maps(
        cls,
        email: EmailStr
    ) -> list[Sprite]:
        """
        Находит всех спрайтов пользователя в базе данных.

        Args: 
            email: электронная почта пользователя.
        
        Returns:
            Список бъектов спрайта или None, если спрайт не найден.

        Raises: 
            LookupError: ошибка что пользователь не найден
        """

        user = await UsersDAO.find_user(email)

        if not user:
            raise LookupError()

        return await super()._find_all_data_where(
            cls.model.user_id == user.id
        )

class SpriteDAO(BaseDAO[Sprite]):
    """Класс взаимодействия с таблицей sprites"""

    model = Sprite

    @classmethod
    async def add_sprite(
        cls, 
        email: EmailStr, 
        sprite_name: str,
        data: List[List[int]],
    ) -> None:
        """
        Добавляет спрайт в базу данных.

        Args:
            email: email пользователя.
            sprite_name: название спрайта.
            data: сам спрайт в виде матрицы.

        Raises:
            IntegrityError - если добавляются данные, которые уже есть в базе.
            SQLAlchemyError - если возникла ошибка при добавлении.
        """


        user = await UsersDAO.find_user(email)
        if not user :
            return
                
        await super()._add_data(
            user_id=user.id,
            sprite_name=sprite_name,
            data=data
        )

    @classmethod
    async def delete_sprite(
        cls, 
        email: EmailStr, 
        sprite_name: str, 
    ) -> None:
        """
        Удаляют спрайт из базы данных.

        Args:
            email: электронная почта пользователя.
            sprite_name: название спрайта, которого нужно удалить
    
        Returns:
            True - если получилось удалить спрайта, иначе False.
            
        Raises:
            SQLAlchemyError - если при удалении возникла ошибка.
        """

        user = await UsersDAO.find_user(email)

        if not user:
            return 
        
        return await super()._delete_data_where(
            cls.model.user_id == user.id,
            cls.model.sprite_name == sprite_name
        )
    
    @classmethod
    async def update_sprite(
        cls, 
        email: EmailStr, 
        sprite_name: str, 
        new_data: List[List[int]],
    ) -> None:
        """
        Обновляет спрайта в базе данных.

        Args:
            email: email пользователя.
            sprite_name: название спрайта.
            new_data: новый спрайт

        Raises:
            SQLAlchemyError - если возникла ошибка при добавлении.
        """

        user = await UsersDAO.find_user(email)

        if not user:
            return
        
        await super()._update_data_where(
            cls.model.user_id == user.id,
            cls.model.sprite_name == sprite_name,
            data = new_data
        )
    
    @classmethod
    async def find_sprite(
        cls,
        email: EmailStr,
        sprite_name: str,
    ) -> Sprite | None:
        """
        Находит спрайта в базе данных.

        Args: 
            email: электронная почта пользователя.
            sprite_name: название спрайта.

        
        Returns:
            Объект спрайта или None, если спрайт не найден.
        """

        user = await UsersDAO.find_user(email)

        if not user:
            return

        return await super()._find_data_where(
            cls.model.email == email,
            cls.model.sprite_name == sprite_name
        )
    
    @classmethod
    async def find_all_sprites(
        cls,
        email: EmailStr
    ) -> list[Sprite]:
        """
        Находит всех спрайтов пользователя в базе данных.

        Args: 
            email: электронная почта пользователя.
        
        Returns:
            Список бъектов спрайта или None, если спрайт не найден.

        Raises:
            LookupError: ошибка что пользователь не найден
        """

        user = await UsersDAO.find_user(email)

        if not user:
            raise LookupError()

        return await super()._find_all_data_where(
            cls.model.user_id == user.id
        )