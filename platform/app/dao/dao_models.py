from sqlalchemy import select, update, delete, insert
from sqlalchemy.sql import ClauseElement
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import EmailStr

from app.migration.models import User, Map, Sprite, SpriteLogic
from app.database import async_session_maker

from typing import Generic, TypeVar, Type, List, Optional, Any, Dict


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
    async def _find_all_data_where(
        cls, *conditions: ClauseElement
    ) -> List[T] | None:
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
    async def delete_user(cls, email: EmailStr) -> bool:
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
    ) -> bool:
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
    """Класс взаимодействия с таблицей maps."""

    model = Map

    @classmethod
    async def add_map(
        cls, 
        user_id: int, 
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
            TypeError - если были переданы некорректные значения.
        """

        await super()._add_data(
            user_id=user_id,
            mapname=mapname,
            data=data
        )

    @classmethod
    async def delete_map(
        cls, 
        map_id: int, 
    ) -> bool:
        """
        Удаляют карту из базы данных.

        Args:
            map_id: id карты, которую нужно удалить
    
        Returns:
            True - если получилось удалить карту, иначе False.
            
        Raises:
            SQLAlchemyError - если при удалении возникла ошибка.
        """
        return await super()._delete_data_where(
            cls.model.id == map_id,
        )
    
    @classmethod
    async def update_map(
        cls, 
        user_id: int, 
        mapname: str, 
        new_data: List[List[int]],
    ) -> bool:
        """
        Обновляет карту в базе данных.

        Args:
            email: email пользователя.
            mapname: название карты.
            new_data: новая карта.

        Returns:
            True - если карта была обновлена. False - иначе   
            
        Raises:
            SQLAlchemyError - если возникла ошибка обновлении.
        """
        
        await super()._update_data_where(
            cls.model.user_id == user_id,
            cls.model.mapname == mapname,
            data = new_data
        )

    @classmethod
    async def find_all_maps(
        cls,
        user_id: int
    ) -> List[Map] | None:
        """
        Находит все карты пользователя в базе данных.

        Args: 
            email: электронная почта пользователя.
        
        Returns:
            Список карт пользователя или None, если карты не найдены.

        Raises:
            LookupError - если пользователя нет в базе даннных.
        """

        return await super()._find_all_data_where(
            cls.model.user_id == user_id
        )


class SpriteDAO(BaseDAO[Sprite]):
    """Класс взаимодействия с таблицей sprites."""

    model = Sprite

    @classmethod
    async def add_sprite(
        cls, 
        user_id: int, 
        sprite_name: str,
        sprite_type: str,
        data: List[List[Dict[str, Any]]],
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
            TypeError - если были переданы некорректные значения.
        """
                
        await super()._add_data(
            user_id=user_id,
            sprite_name=sprite_name,
            sprite_type=sprite_type,
            data=data
        )

    @classmethod
    async def delete_sprite(
        cls, 
        sprite_id: int, 
    ) -> bool:
        """
        Удаляет спрайт из базы данных.

        Args:
            sprite_id: id спрайта.
    
        Returns:
            True - если получилось удалить спрайта, иначе False.
            
        Raises:
            SQLAlchemyError - если при удалении возникла ошибка.
        """
        
        return await super()._delete_data_where(
            cls.model.id == sprite_id,
        )
    
    @classmethod
    async def update_sprite(
        cls, 
        user_id: int, 
        sprite_name: str,
        new_data: List[List[Dict[str, Any]]],
    ) -> bool:
        """
        Обновляет спрайт в базе данных.

        Args:
            email: email пользователя.
            sprite_name: название спрайта.
            new_data: новый спрайт.

        Returns:
            True - если была обновлена хотя бы одна строка. False - иначе.

        Raises:
            SQLAlchemyError - если возникла ошибка при добавлении.
        """

        await super()._update_data_where(
            cls.model.user_id == user_id,
            cls.model.sprite_name == sprite_name,
            data = new_data
        )
    
    @classmethod
    async def find_sprite(
        cls,
        user_id: int,
        sprite_name: str,
    ) -> Sprite | None:
        """
        Находит спрайт в базе данных.

        Args: 
            email: электронная почта пользователя.
            sprite_name: название спрайта.

        Returns:
            Спрайт или None, если спрайт не найден.

        Raises:
            LookupError - если пользователя нет в базе данных.
        """

        return await super()._find_data_where(
            cls.model.user_id == user_id,
            cls.model.sprite_name == sprite_name
        )
    
    @classmethod
    async def find_all_sprites(
        cls,
        user_id: int
    ) -> List[Sprite] | None:
        """
        Находит все спрайты пользователя в базе данных.

        Args: 
            email: электронная почта пользователя.
        
        Returns:
            Список бъектов спрайта или None, если спрайт не найден.
        
        Raises:
            LookupError - если пользователя нет в базе данных.
        """

        return await super()._find_all_data_where(
            cls.model.user_id == user_id
        )
    

class SpriteLogicDAO(BaseDAO[SpriteLogic]):
    """Класс взаимодействия с таблицей sprite_logic."""

    model = SpriteLogic

    @classmethod
    async def add_sprite_logic(
        cls,
        sprite_id: int,
        name: str,
        trigger_config: Optional[dict[str, Any]] = None,
        dialog_config: Optional[dict[str, Any]] = None,
        dialog_role: Optional[str] = None
    ) -> None:
        """
        Добавляет новый блок логики для спрайта в базу данных.

        Args:
            sprite_id: id спрайта, к которому привязывается логика.
            name: название блока логики 
            trigger_config: json конфигурации триггеров.
            dialog_config: json конфигурации диалога.
            dialog_role: роль спрайта в диалоге.

        Raises:
            IntegrityError - если добавляются данные, которые уже есть в базе.
            SQLAlchemyError - если возникла ошибка при добавлении.
            TypeError - если были переданы некорректные значения.
        """
        await super()._add_data(
            sprite_id=sprite_id,
            name=name,
            trigger_config=trigger_config,
            dialog_config=dialog_config,
            dialog_role=dialog_role
        )

    @classmethod
    async def update_sprite_logic(
        cls,
        logic_id: int,
        trigger_config: Optional[dict[str, Any]] = None,
        dialog_config: Optional[dict[str, Any]] = None,
        dialog_role: Optional[str] = None
    ) -> bool:
        """
        Обновляет существующий блок логики в базе данных.

        Args:
            logic_id: id конкретного блока логики для обновления.
            trigger_config: новая json конфигурация триггеров.
            dialog_config: новая json конфигурация диалога.
            dialog_role: новая роль спрайта в диалоге.

        Returns:
            True - если была обновлена хотя бы одна строка. False - иначе.

        Raises:
            SQLAlchemyError - если возникла ошибка при обновлении.
        """
        values = {}
        if trigger_config is not None:
            values["trigger_config"] = trigger_config
        if dialog_config is not None:
            values["dialog_config"] = dialog_config
        if dialog_role is not None:
            values["dialog_role"] = dialog_role

        if not values:
            return False

        return await super()._update_data_where(
            cls.model.id == logic_id,
            **values
        )

    @classmethod
    async def find_sprite_logic_block(
        cls,
        sprite_id: int,
        logic_block_name: str
    ) -> SpriteLogic | None:
        """
        Находит блок логики для указанного спрайта.

        Args:
            sprite_id: id спрайта.
            logic_block_name: название блока

        Returns:
            Объект блока логики или None, если блок не найден.

        Raises:
            SQLAlchemyError - если возникла ошибка при поиске.
        """
        return await super()._find_data_where(
            cls.model.sprite_id == sprite_id,
            cls.model.name == logic_block_name
        )

    @classmethod
    async def find_all_sprite_logic_by_sprite(
        cls,
        sprite_id: int
    ) -> List[SpriteLogic] | None:
        """
        Находит все блоки логики для указанного спрайта.

        Args:
            sprite_id: id спрайта.

        Returns:
            Список объектов блоков логики или None, если блоки не найдены.

        Raises:
            SQLAlchemyError - если возникла ошибка при поиске.
        """
        return await super()._find_all_data_where(
            cls.model.sprite_id == sprite_id
        )

    @classmethod
    async def delete_sprite_logic(
        cls,
        logic_id: int
    ) -> bool:
        """
        Удаляет конкретный блок логики из базы данных.

        Args:
            logic_id: id блока логики для удаления.

        Returns:
            True - если получилось удалить блок логики, иначе False.

        Raises:
            SQLAlchemyError - если при удалении возникла ошибка.
        """
        return await super()._delete_data_where(
            cls.model.id == logic_id,
        )