import pytest
from sqlalchemy import pool, select, text, insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from os import getenv
from dotenv import load_dotenv

import app.migration.models as mig_models
import app.dao.dao_models as dao_models


load_dotenv()

def get_async_url():
    """
    Формирует URL для асинхронного соединения с базой данных.
     
    Returns:
        Строка-url для асинхронного соединения с базой данных.
    """

    user = getenv("DB_USER")
    password = getenv("DB_PASSWORD")
    host = getenv("DB_HOST")
    port = getenv("DB_PORT")
    name = getenv("DB_NAME")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"


@pytest.fixture(scope="function")
async def async_session():
    """Фикстура, создающая сессию для работы с базой данных."""

    TEST_ASYNC_DB_URL = get_async_url()
    engine = create_async_engine(
        TEST_ASYNC_DB_URL, 
        poolclass=pool.NullPool
    )
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE users RESTART IDENTITY CASCADE;"))
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_add_user(async_session):
    """Проверка dao-функции для добавления пользователя в базу данных."""

    # Arrange
    username = "xxxxxxxxxxxx"
    email = "dmdmd@mail.ru"
    password = "12356645"

    # Act
    await dao_models.UsersDAO.add_user(
        username=username,
        email=email,
        password=password,
    )

    # Assert
    result = await async_session.execute(select(mig_models.User))
    db_user = result.scalar_one_or_none()

    assert db_user is not None
    assert db_user.username == username
    assert db_user.email == email
    assert db_user.password == password
    assert db_user.id is not None
    assert db_user.register_at is not None 


@pytest.mark.asyncio
async def test_find_exist_user(async_session):
    """
    Проверка dao-функции при поиске существующего пользователя в базе данных.
    """

    # Arrange
    username = "xxxxxxxxxxxx"
    email = "dmdmd@mail.ru"
    password = "12356645"
    
    query = insert(mig_models.User).values(
        username=username,
        password=password,
        email=email,
    )
    await async_session.execute(query)
    await async_session.commit()

    # Act
    db_user = await dao_models.UsersDAO.find_user(email=email)

    # Assert
    assert db_user is not None
    assert db_user.username == username
    assert db_user.email == email
    assert db_user.password == password
    assert db_user.id is not None
    assert db_user.register_at is not None 


@pytest.mark.asyncio
async def test_find_not_exist_user():
    """
    Проверка dao-функции при поиске несуществующего пользователя в базе данных.
    """
    
    # Arrange
    email = "ddddd@mail.ru"

    # Act
    db_user = await dao_models.UsersDAO.find_user(email=email)

    # Assert
    assert db_user is None


@pytest.mark.asyncio
async def test_delete_exist_user(async_session):
    """
    Проверка на удаление существующего пользователя из базы данных.
    """

    # Arrange
    username = "xxxxxxxxxxxx"
    email = "dmdmd@mail.ru"
    password = "12356645"
    
    query = insert(mig_models.User).values(
        username=username,
        password=password,
        email=email,
    )
    await async_session.execute(query)
    await async_session.commit()

    # Act
    flag = await dao_models.UsersDAO.delete_user(email=email)

    # Assert
    assert flag == True

    result = await async_session.execute(select(mig_models.User))
    db_user = result.scalar_one_or_none()

    assert db_user is None


@pytest.mark.asyncio
async def test_delete_not_exist_user(async_session):
    """
    Проверка на удаление несуществующего пользователя из базы данных.
    """

    # Arrange
    email = "dmdmd@mail.ru"

    # Act
    flag = await dao_models.UsersDAO.delete_user(email=email)

    # Assert
    assert flag == False

    result = await async_session.execute(select(mig_models.User))
    db_user = result.scalar_one_or_none()

    assert db_user is None


@pytest.mark.asyncio
async def test_model_user_class():
    """Проверка, что UserDAO отвечает за модель User."""

    # Arrange + Act
    users = dao_models.UsersDAO()

    # Assert
    assert users.model == mig_models.User


@pytest.mark.asyncio
async def test_update_password_for_exist_user(async_session):
    """Проверка обновления пароля у существующего пользователя."""

    # Arrange
    username = "xxxxxxxxxxxx"
    email = "dmdmd@mail.ru"
    password = "12356645"
    
    query = insert(mig_models.User).values(
        username=username,
        password=password,
        email=email,
    )
    await async_session.execute(query)
    await async_session.commit()

    # Act
    new_password = "sdfsdfsdf334"
    flag = await dao_models.UsersDAO.update_user_password(
        email=email,
        password=new_password,
    )

    # Assert
    assert flag == True

    result = await async_session.execute(select(mig_models.User))
    db_user = result.scalar_one_or_none()

    assert db_user.password == new_password


@pytest.mark.asyncio
async def test_update_password_for_not_exist_user(async_session):
    """Проверка обновления пароля у несуществующего пользователя."""

    # Arrange
    email = "hello@mail.ru"

    # Act
    new_password = "sdfsdfsdf334"
    flag = await dao_models.UsersDAO.update_user_password(
        email=email,
        password=new_password,
    )

    # Assert
    assert flag == False

    result = await async_session.execute(select(mig_models.User))
    db_user = result.scalar_one_or_none()

    assert db_user is None


@pytest.mark.asyncio
async def test_add_user_with_one_email(async_session):
    """
    Проверка появления ошибки IntegrityError после добавления пользователей с 
    одинаковым email.
    """

    # Arrange
    email = "halllo@mail.ru"

    query = insert(mig_models.User).values(
        username="dddddddd",
        password="1234",
        email=email,
    )
    await async_session.execute(query)
    await async_session.commit()

    # Act + Assert
    with pytest.raises(IntegrityError):
        await dao_models.UsersDAO.add_user(
            username="Bob",
            password="456",
            email=email, 
        )


@pytest.mark.asyncio
async def test_add_user_with_one_username(async_session):
    """
    Проверка появления ошибки IntegrityError после добавления пользователей с 
    одинаковым username.
    """

    # Arrange
    username = "hello"

    query = insert(mig_models.User).values(
        username=username,
        password="1234",
        email="dhddd@mail.ru",
    )
    await async_session.execute(query)
    await async_session.commit()

    # Act + Assert
    with pytest.raises(IntegrityError):
        await dao_models.UsersDAO.add_user(
            username=username,
            password="456",
            email="ewwwww@mail.ru", 
        )


@pytest.mark.asyncio
async def test_add_user_typeerror():
    """
    Проверка появления ошибки TypeError после добавления пользователя
    с лишним полем.
    """
    
    # Arrange
    username = "dfsdfsdf"
    email = "dsfsdf@mail.ru"
    password = "12345"

    # Act + Assert
    with pytest.raises(TypeError):
        await dao_models.UsersDAO.add_user(
            username=username,
            email=email,
            password=password,
            wrong_field="hello im fake",
        )


@pytest.mark.asyncio
async def test_add_user_sqlalchemyerror():
    """
    Проверка появления ошибки SQLAlchemyError после добавления пользователя
    c неправильным типом поля.
    """
    
    # Arrange
    username = 1123
    email = "dsfsdf@mail.ru"
    password = "12345"

    # Act + Assert
    with pytest.raises(SQLAlchemyError):
        await dao_models.UsersDAO.add_user(
            username=username,
            email=email,
            password=password,
        )


@pytest.mark.asyncio
async def test_update_user_password_sqlalchemyerror():
    """
    Проверка появления ошибки SQLAlchemyError после обновления пароля
    пользователя с неправильным типом нового пароля.
    """

    # Arrange
    email = "fsdfs@mail.ru"
    password = 12345

    # Act + Assert
    with pytest.raises(SQLAlchemyError):
        await dao_models.UsersDAO.update_user_password(
            email=email,
            password=password,
        )


@pytest.mark.asyncio
async def test_delete_user_sqlalchemyerror():
    """
    Проверка появления ошибки SQLAlchemyError после удаления пользователя 
    с неправильным типом поля.
    """

    # Arrange
    email = 12345

    # Act + Assert
    with pytest.raises(SQLAlchemyError):
        await dao_models.UsersDAO.delete_user(
            email=email,
        )