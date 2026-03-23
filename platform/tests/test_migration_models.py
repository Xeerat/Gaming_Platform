import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.exc import IntegrityError

from os import getenv
from dotenv import load_dotenv

import app.migration.models as mig_models


def test_base_class_init():
    """Проверка существования базового класса."""

    # Act
    base_class = mig_models.Base()

    # Assert
    assert base_class.__abstract__ == True


def test_base_class_inheritance():
    """Проверка, что базовый класс имеет нужных родителей."""

    assert issubclass(mig_models.Base, DeclarativeBase) == True
    assert issubclass(mig_models.Base, AsyncAttrs) == True


def test_user_class_init():
    """Проверка, что класс user существует."""

    # Arrange
    username = "hello"
    email = "hello@mail.ru"
    password = "12345"

    # Act
    user = mig_models.User(
        username=username,
        email=email,
        password=password,
    )

    # Assert
    assert user.username == username
    assert user.email == email
    assert user.password == password
    assert user.__tablename__ == "users"
    assert user.extend_existing == True


def test_user_class_inheritance():
    """Проверка, что класс user имеет нужных родителей."""

    assert issubclass(mig_models.User, mig_models.Base)


load_dotenv()


def get_test_db_url() -> str:
    """
    Создает url для тестового соединения с базой данных.
    
    Returns:
        Строку-url для тестовой синхронной связи с базой данных.
    """

    user = getenv("DB_USER")
    password = getenv("DB_PASSWORD")
    host = getenv("DB_HOST")
    port = getenv("DB_PORT")
    name = getenv("DB_NAME")
    
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


@pytest.fixture(scope="function")
def test_session():
    """Фикстура сессии для бд, для проверки работы orm моделей."""
    
    TEST_DB_URL = get_test_db_url()
    engine = create_engine(TEST_DB_URL)
    mig_models.Base.metadata.create_all(engine)

    connection = engine.connect()
    # Транзакция нужна для того чтобы в конце откатить изменения
    transaction = connection.begin()

    test_session_maker = sessionmaker(bind=connection)
    session = test_session_maker()
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


def test_save_user(test_session):
    """Проверка корректности сохранения пользователя в базе данных."""

    # Arrange
    username = "hello"
    email = "hello@mail.ru"
    password = "12345"

    user = mig_models.User(
        username=username,
        email=email,
        password=password,
    )

    # Act
    test_session.add(user)
    test_session.commit()

    # Assert
    db_user = test_session.query(mig_models.User).first()

    assert db_user is not None
    assert db_user.username == username
    assert db_user.email == email
    assert db_user.password == password 
    assert db_user.id is not None
    assert db_user.register_at is not None


def test_unique_usernames(test_session):
    """Проверяет, что username уникальна."""

    # Arrange
    username = "hello"

    user1 = mig_models.User(
        username=username, 
        email="abc@mail.ru",
        password="1234556",
    )
    user2 = mig_models.User(
        username=username,
        email="bds@mail.ru",
        password="244444",
    )

    # Act
    test_session.add_all([user1, user2])

    # Assert 
    with pytest.raises(IntegrityError):
        test_session.commit()


def test_unique_email(test_session):
    """Проверяет, что email уникальна."""

    # Arrange
    email = "hello@mail.ru"

    user1 = mig_models.User(
        username="helloddddd", 
        email=email,
        password="1234556",
    )
    user2 = mig_models.User(
        username="dhdhdhdhd",
        email=email,
        password="244444",
    )

    # Act 
    test_session.add_all([user1, user2])

    # Assert 
    with pytest.raises(IntegrityError):
        test_session.commit()