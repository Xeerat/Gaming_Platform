from pydantic import ValidationError, BaseModel
import pytest

import app.users.validation as validation


def test_register_correct_all():
    """Проверка валидатора регистрации с полностью корректными данными."""

    # Arrange
    email = "dddd@mail.ru"
    username = "hellohid"
    password = "1234567890"
    confirm_password = "1234567890"

    # Act
    user = validation.SUserRegister(
        email=email,
        username=username,
        password=password,
        confirm_password=confirm_password,
    )
    
    # Assert 
    assert user.email == email
    assert user.username == username
    assert user.password == password
    assert user.confirm_password == confirm_password


def test_register_incorrect_email():
    """Проверка валидатора регистрации с некорректным email."""

    # Arrange
    email = "d.ru"
    username = "hellohid"
    password = "1234567890"
    confirm_password = "1234567890"

    # Act + Assert
    with pytest.raises(ValidationError):
        validation.SUserRegister(
            email=email,
            username=username,
            password=password,
            confirm_password=confirm_password,
        )


@pytest.mark.parametrize("username", ["h", "hhhhhhhhhhhhhhhhhhhhhhhhhhhh"])
def test_register_incorrect_username(username: str):
    """Проверка валидатора регистрации с некорректным username."""

    # Arrange
    email = "dddd@mail.ru"
    password = "1234567890"
    confirm_password = "1234567890"

    # Act + Assert
    with pytest.raises(ValidationError):
        validation.SUserRegister(
            email=email,
            username=username,
            password=password,
            confirm_password=confirm_password,
        )


@pytest.mark.parametrize("password, confirm_password", [
    ("1234", "1234"),
    ("hello_hi_1234567890", "hello_hi_1234567890"),
])
def test_register_incorrect_password_and_confirm_password(
    password: str,
    confirm_password: str,
):
    """Проверка валидатора регистрации с некорректным password и confirm."""

    # Arrange
    email = "dddd@mail.ru"
    username = "hellohid"

    # Act + Assert
    with pytest.raises(ValidationError):
        validation.SUserRegister(
            email=email,
            username=username,
            password=password,
            confirm_password=confirm_password,
        )


@pytest.mark.parametrize("password, confirm_password", [
    ("1234567890", "0987654321"),
    ("hellohihih", "hihiholleh"),
    ("hsfljdfjsj", "sdfuhrugdfgdsf")
])
def test_register_not_match_passwords(password: str, confirm_password: str):
    """Проверка валидатора регистрации с несовпадающими паролями."""

    # Arrange
    email = "dddd@mail.ru"
    username = "hellohid"

    # Act + Assert
    with pytest.raises(ValidationError):
        validation.SUserRegister(
            email=email,
            username=username,
            password=password,
            confirm_password=confirm_password,
        )


def test_auth_correct_all():
    """Проверка валидатора авторизации с полностью корректными данными."""

    # Arrange
    email = "hello@mail.ru"
    password = "1234567890"

    # Act
    user = validation.SUserAuth(email=email, password=password)

    # Assert
    assert user.email == email
    assert user.password == password


def test_auth_incorrect_email():
    """Проверка валидатора авторизации с некорректным email."""

    # Arrange
    email = "d.ru"
    password = "1234567890"

    # Act + Assert
    with pytest.raises(ValidationError):
        validation.SUserAuth(email=email, password=password)


@pytest.mark.parametrize("password", ["111", "1234567889908884834343"]) 
def test_auth_incorrect_password(password: str):
    """Проверка валидатора авторизации с некорректным password."""

    email = "Hello@mail.ru"
    
    with pytest.raises(ValidationError):
        validation.SUserAuth(email=email, password=password)


def test_forgot_password_correct_all():
    """
    Проверка валидатора первой страницы "забыли пароль?" с корректными данными.
    """

    # Arrange
    email = "hello@mail.ru"

    # Act
    user = validation.SUserForgotPassword(email=email)

    # Assert 
    assert user.email == email


def test_forgot_password_incorrect_email():
    """
    Проверка валидатора первой страницы "забыли пароль?" с некорректным email.
    """

    # Arrange
    email = "h.ru"

    # Act + Assert
    with pytest.raises(ValidationError):
        validation.SUserForgotPassword(email=email)


@pytest.mark.parametrize("data", [
    {
        "password": "hellohihoh", 
        "confirm_password": "hellohihoh", 
        "token": "hh"
    },
    {
        "password": "hellohihoh", 
        "confirm_password": "hellohihoh", 
    }
])
def test_update_password_correct_all(data: dict[str, str]):
    """
    Проверка валидатора второй страницы "забыли пароль?" с корректными данными.
    """
    
    # Act
    user = validation.SUserUpdatePassword(**data)

    # Assert
    assert user.password == data.get("password")
    assert user.confirm_password == data.get("confirm_password")

    if "token" not in data:
        assert user.token == None
    else:
        assert user.token == data.get("token")


@pytest.mark.parametrize("password, confirm_password", [
    ("123", "123"),
    ("1234567890098765", "1234567890098765"),
])
def test_update_password_incorrect_password_and_confirm_password(
    password: str, 
    confirm_password: str,
):
    """
    Проверка валидатора второй страницы "забыли пароль?" с корректными данными.
    """

    # Act + Assert
    with pytest.raises(ValidationError):
        validation.SUserUpdatePassword(
            password=password,
            confirm_password=confirm_password,
        )


@pytest.mark.parametrize("password, confirm_password", [
    ("1234567890", "0987654321"),
    ("hellohihih", "hihiholleh"),
    ("hsfljdfjsj", "sdfuhrugdfgdsf"),
])
def test_update_password_not_match_passwords(
    password: str, 
    confirm_password: str,
):
    """
    Проверка валидатора второй страницы "забыли пароль?" при разных паролях.
    """

    # Act + Assert
    with pytest.raises(ValidationError):
        validation.SUserUpdatePassword(
            password=password,
            confirm_password=confirm_password,
        )


def test_all_validator_inheritance():
    """Проверка, что все валидаторы наследуются от нужного класса."""

    assert issubclass(validation.SUserRegister, BaseModel) == True
    assert issubclass(validation.SUserAuth, BaseModel) == True
    assert issubclass(validation.SUserForgotPassword, BaseModel) == True
    assert issubclass(validation.SUserUpdatePassword, BaseModel) == True
