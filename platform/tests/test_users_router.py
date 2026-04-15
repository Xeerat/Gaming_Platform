from fastapi.testclient import TestClient
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from jose.exceptions import ExpiredSignatureError, JWTError
import pytest 

from unittest.mock import patch, AsyncMock

from app.main import app
import app.users.router as users_router


client = TestClient(app)


def test_redirect_message_error():
    """Проверка redirect_message с переданной ошибкой."""

    # Arrange + Act
    response = users_router.redirect_message(
        url="/test",
        message="ошибка",
        error=True
    )

    # Assert
    assert isinstance(response, RedirectResponse)
    assert response.status_code == 303
    assert "error=" in response.headers["location"]


def test_redirect_message_encoding_message():
    """Проверка кодирования текста в redirect_message."""

    # Arrange + Act
    response = users_router.redirect_message(
        url="/test",
        message="hello world",
        error=True
    )

    # Assert 
    assert "hello%20world" in response.headers["location"]


def test_redirect_message_success():
    """Проверка redirect_message с переданным успехом."""

    # Arrange + Act
    response = users_router.redirect_message(
        url="/test",
        message="ok",
        success=True
    )

    # Assert
    assert "success=" in response.headers["location"]
    assert "error=" not in response.headers["location"]


def test_redirect_message_with_token():
    """Проверка redirect_message с переданным токеном."""

    # Arrange + Act
    response = users_router.redirect_message(
        url="/test",
        message="ok",
        success=True,
        token="abc123"
    )

    # Assert 
    assert "token=abc123" in response.headers["location"]


def test_redirect_message_full_url():
    """
    Проверка полного url, который должен получится после redirect_message.
    """

    # Arrange + Act
    response = users_router.redirect_message(
        url="/test",
        message="hello world",
        error=True,
        token="123"
    )

    # Assert
    expected = "/test?error=hello%20world&token=123"
    assert response.headers["location"] == expected


@pytest.mark.asyncio
async def test_register_user_success():
    """Проверка успешной регистрации пользователя."""

    # Arrange
    form_data = {
        "username": "testuser", 
        "email": "test@test.com", 
        "password": "123", 
        "confirm_password": "123"}
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    SUserReg_path = "app.users.router.SUserRegister"
    add_user_path = "app.users.router.UsersDAO.add_user"
    get_pass_hash_path = "app.users.router.get_password_hash"
    send_ver_email_path = "app.users.router.send_verification_email"
    redirect_message_path = "app.users.router.redirect_message"

    with patch(SUserReg_path) as mock_schema, \
         patch(add_user_path, new_callable=AsyncMock) as mock_add_user, \
         patch(get_pass_hash_path, return_value="hashed_pw"), \
         patch(send_ver_email_path, new_callable=AsyncMock) as mock_email, \
         patch(redirect_message_path) as mock_redirect:

        mock_schema.return_value = mock_schema 
        mock_schema.return_value.username = form_data["username"]
        mock_schema.return_value.email = form_data["email"]
        mock_schema.return_value.password = form_data["password"]

        # Act
        await users_router.register_user(request)

        # Assert
        mock_redirect.assert_called_once_with(url="/auth/verify-email")

        mock_add_user.assert_awaited_once_with(
            username=form_data["username"],
            email=form_data["email"],
            password="hashed_pw"
        )
        mock_email.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_user_validation_error():
    """Проверка ситуации с несовпадающими паролями."""

    # Arrange
    form_data = {
        "username": "testuser", 
        "email": "test@test.com", 
        "password": "123", 
        "confirm_password": "456"}
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    redirect_message_path = "app.users.router.redirect_message"

    # Act + Assert
    with patch(redirect_message_path) as mock_redirect:
        await users_router.register_user(request)

        mock_redirect.assert_called_once_with(
            url="/auth/register/",
            message="Пароли не совпадают.",
            error=True,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("error_str,expected_msg", [
    ("email", "Пользователь с таким email уже существует."),
    ("username", "Пользователь с таким именем уже существует.")
])
async def test_register_user_integrity_error(error_str, expected_msg):
    """Проверка обработки IntegrityError в функции регистрации."""

    # Arrange
    form_data = {
        "username": "testuser", 
        "email": "test@test.com", 
        "password": "123", 
        "confirm_password": "123"
    }
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    error = IntegrityError(
        statement=None, 
        params=None,
        orig=Exception(error_str)
    )

    SUserReg_path = "app.users.router.SUserRegister"
    add_user_path = "app.users.router.UsersDAO.add_user"
    redirect_message_path = "app.users.router.redirect_message"

    # Act + Assert 
    with patch(SUserReg_path) as mock_schema, \
         patch(add_user_path, new_callable=AsyncMock, side_effect=error), \
         patch(redirect_message_path) as mock_redirect:

        mock_schema.return_value = mock_schema
        mock_schema.return_value.username = form_data["username"]
        mock_schema.return_value.email = form_data["email"]
        mock_schema.return_value.password = form_data["password"]

        await users_router.register_user(request)
        
        mock_redirect.assert_called_once_with(
            url="/auth/register/",
            message=expected_msg,
            error=True,
        )


@pytest.mark.asyncio
async def test_register_user_sqlalchemy_error():
    """Проверка обработки SQLAlchemyError в функции регистрации."""

    # Arrange
    form_data = {
        "username": "testuser", 
        "email": "test@test.com", 
        "password": "123", 
        "confirm_password": "123"
    }
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    SUserReg_path = "app.users.router.SUserRegister"
    add_user_path = "app.users.router.UsersDAO.add_user"
    redirect_message_path = "app.users.router.redirect_message"

    # Act + Assert
    with patch(SUserReg_path) as mock_schema, \
         patch(redirect_message_path) as mock_redirect, \
         patch(
            add_user_path,
            new_callable=AsyncMock, 
            side_effect=SQLAlchemyError()
         ):

        mock_schema.return_value = mock_schema
        mock_schema.return_value.username = form_data["username"]
        mock_schema.return_value.email = form_data["email"]
        mock_schema.return_value.password = form_data["password"]

        await users_router.register_user(request)

        mock_redirect.assert_called_once_with(
                url="/auth/register/",
                message="Возникла ошибка при добавлении пользователя.",
                error=True,
        )


@pytest.mark.asyncio
async def test_auth_user_success():
    """Проверка успешной аутентификации пользователя."""

    # Arrange
    form_data = {
        "email": "test@test.com",
        "password": "123"
    }
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    SUserAuth_path = "app.users.router.SUserAuth"
    find_user_path = "app.users.router.UsersDAO.find_user"
    verify_pass_path = "app.users.router.verify_password"
    create_token_path = "app.users.router.create_access_token"
    redirect_message_path = "app.users.router.redirect_message"

    mock_user = AsyncMock()
    mock_user.id = 0
    mock_user.password = "hashed_pw"

    with patch(SUserAuth_path) as mock_schema, \
         patch(verify_pass_path, return_value=True) as mock_verify, \
         patch(create_token_path, return_value="token123") as mock_token, \
         patch(redirect_message_path) as mock_redirect, \
         patch(
            find_user_path, 
            new_callable=AsyncMock, 
            return_value=mock_user
         ) as mock_find_user:

        mock_schema.return_value = mock_schema
        mock_schema.return_value.email = form_data["email"]
        mock_schema.return_value.password = form_data["password"]

        mock_response = AsyncMock()
        mock_redirect.return_value = mock_response

        # Act
        response = await users_router.auth_user(request)

        # Assert
        mock_find_user.assert_awaited_once_with(email=form_data["email"])
        mock_verify.assert_called_once_with("123", "hashed_pw")
        mock_token.assert_called_once_with(
            email=form_data["email"],
            user_id=mock_user.id
        )

        mock_redirect.assert_called_once_with(url="/main/")
        mock_response.set_cookie.assert_called_once_with(
            key="users_access_token",
            value="token123",
            httponly=True
        )

        assert response == mock_response


@pytest.mark.asyncio
async def test_auth_user_validation_error():
    """Ошибка валидации формы."""

    # Arrange
    request = AsyncMock()
    request.form = AsyncMock(return_value={"email": "bad", "password": "123"})

    redirect_message_path = "app.users.router.redirect_message"

    # Act + Assert 
    with patch(redirect_message_path) as mock_redirect:

        await users_router.auth_user(request)
        mock_redirect.assert_called_once_with(
            url="/auth/login/",
            message="Введена некорректная электронная почта.",
            error=True,
        )

    
@pytest.mark.asyncio
async def test_auth_user_user_not_found():
    """Пользователь не найден."""

    # Arrange
    form_data = {
        "email": "test@test.com",
        "password": "123"
    }
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    SUserAuth_path = "app.users.router.SUserAuth"
    find_user_path = "app.users.router.UsersDAO.find_user"
    redirect_message_path = "app.users.router.redirect_message"

    with patch(SUserAuth_path) as mock_schema, \
         patch(redirect_message_path) as mock_redirect, \
         patch(
            find_user_path, 
            new_callable=AsyncMock, 
            return_value=None
         ) as mock_find_user:

        mock_schema.return_value = mock_schema
        mock_schema.return_value.email = form_data["email"]
        mock_schema.return_value.password = form_data["password"]

        # Act
        await users_router.auth_user(request)

        # Assert
        mock_find_user.assert_awaited_once_with(email=form_data["email"])
        mock_redirect.assert_called_once_with(
            url="/auth/login/",
            message="Неверная почта или пароль",
            error=True,
        )


@pytest.mark.asyncio
async def test_auth_user_wrong_password():
    """Неверный пароль."""

    # Arrange
    form_data = {
        "email": "test@test.com",
        "password": "123"
    }
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    SUserAuth_path = "app.users.router.SUserAuth"
    find_user_path = "app.users.router.UsersDAO.find_user"
    verify_pass_path = "app.users.router.verify_password"
    redirect_message_path = "app.users.router.redirect_message"

    mock_user = AsyncMock()
    mock_user.password = "hashed_pw"

    with patch(SUserAuth_path) as mock_schema, \
         patch(verify_pass_path, return_value=False), \
         patch(redirect_message_path) as mock_redirect, \
         patch(find_user_path, new_callable=AsyncMock, return_value=mock_user):

        mock_schema.return_value = mock_schema
        mock_schema.return_value.email = form_data["email"]
        mock_schema.return_value.password = form_data["password"]

        # Act
        await users_router.auth_user(request)

        # Assert
        mock_redirect.assert_called_once_with(
            url="/auth/login/",
            message="Неверная почта или пароль",
            error=True,
        )


@pytest.mark.asyncio
async def test_logout_user_success():
    """Проверка выхода пользователя."""

    # Arrange
    redirect_message_path = "app.users.router.redirect_message"

    with patch(redirect_message_path) as mock_redirect:
        mock_response = AsyncMock()
        mock_redirect.return_value = mock_response

        # Act
        response = await users_router.logout_user()

        # Assert
        mock_redirect.assert_called_once_with(url='/auth/login/')
        mock_response.delete_cookie.assert_called_once_with(
            key="users_access_token",
        )

        assert response == mock_response

    
@pytest.mark.asyncio
async def test_delete_user_success():
    """Успешное удаление пользователя."""

    # Arrange
    request = AsyncMock()
    request.cookies = {"users_access_token": "valid_token"}

    decode_token_path = "app.users.router.decode_access_token"
    delete_user_path = "app.users.router.UsersDAO.delete_user"
    redirect_message_path = "app.users.router.redirect_message"

    with patch(redirect_message_path) as mock_redirect, \
         patch(
            decode_token_path, 
            return_value="test@test.com"
         ) as mock_decode, \
         patch(
            delete_user_path, 
            new_callable=AsyncMock, 
            return_value=True
        ) as mock_delete:

        mock_response = AsyncMock()
        mock_redirect.return_value = mock_response

        # Act
        response = await users_router.delete_user(request)

        # Assert
        mock_decode.assert_called_once_with("valid_token")
        mock_delete.assert_awaited_once_with(email="test@test.com")

        mock_redirect.assert_called_once_with(
            url="/auth/login/",
            message="Удаление прошло успешно!",
            success=True,
        )

        mock_response.delete_cookie.assert_called_once_with(
            key="users_access_token"
        )

        assert response == mock_response


@pytest.mark.asyncio
async def test_delete_user_not_found():
    """Пользователь не найден при удалении."""

    # Arrange
    request = AsyncMock()
    request.cookies.get.return_value = "valid_token"

    decode_token_path = "app.users.router.decode_access_token"
    delete_user_path = "app.users.router.UsersDAO.delete_user"
    redirect_message_path = "app.users.router.redirect_message"

    with patch(decode_token_path, return_value="test@test.com"), \
         patch(delete_user_path, new_callable=AsyncMock, return_value=False), \
         patch(redirect_message_path) as mock_redirect:

        # Act
        await users_router.delete_user(request)

        # Assert
        mock_redirect.assert_called_once_with(
            url="/auth/login/",
            message="Такой пользователь не зарегистрирован.",
            error=True,
        )


@pytest.mark.asyncio
async def test_delete_user_expired_token():
    """Истёк срок действия токена."""

    # Arrange
    request = AsyncMock()
    request.cookies.get.return_value = "expired_token"

    decode_token_path = "app.users.router.decode_access_token"
    redirect_message_path = "app.users.router.redirect_message"

    with patch(decode_token_path, side_effect=ExpiredSignatureError()), \
         patch(redirect_message_path) as mock_redirect:

        # Act
        await users_router.delete_user(request)

        # Assert
        mock_redirect.assert_called_once_with(
            url="/main/",
            message="Истек срок годности токена.",
            error=True,
        )


@pytest.mark.asyncio
async def test_delete_user_invalid_token():
    """Пользователь не авторизован (битый токен)."""

    # Arrange
    request = AsyncMock()
    request.cookies.get.return_value = "bad_token"

    decode_token_path = "app.users.router.decode_access_token"
    redirect_message_path = "app.users.router.redirect_message"

    with patch(decode_token_path, side_effect=JWTError()), \
         patch(redirect_message_path) as mock_redirect:

        # Act
        await users_router.delete_user(request)

        # Assert
        mock_redirect.assert_called_once_with(
            url="/auth/login/",
            message="Пользователь не авторизован.",
            error=True,
        )


@pytest.mark.asyncio
async def test_delete_user_db_error():
    """Ошибка базы данных при удалении."""

    # Arrange
    request = AsyncMock()
    request.cookies.get.return_value = "valid_token"

    decode_token_path = "app.users.router.decode_access_token"
    delete_user_path = "app.users.router.UsersDAO.delete_user"
    redirect_message_path = "app.users.router.redirect_message"

    with patch(decode_token_path, return_value="test@test.com"), \
         patch(redirect_message_path) as mock_redirect, \
         patch(
            delete_user_path, 
            new_callable=AsyncMock, 
            side_effect=SQLAlchemyError()
         ):

        # Act
        await users_router.delete_user(request)

        # Assert
        mock_redirect.assert_called_once_with(
            url="/main/",
            message="Возникла ошибка при удалении пользователя.",
            error=True,
        )


@pytest.mark.asyncio
async def test_verify_email_success():
    """Проверка успешного подтверждения email."""

    # Arrange
    form_data = {"token": "valid_token"}
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    decode_token_path = "app.users.router.decode_access_token"
    find_user_path = "app.users.router.UsersDAO.find_user"
    redirect_message_path = "app.users.router.redirect_message"
    create_token_path = "app.users.router.create_access_token"

    mock_user = AsyncMock()
    mock_user.id = 0

    with patch(redirect_message_path) as mock_redirect, \
         patch(
            decode_token_path, 
            return_value="test@test.com"
         ) as mock_decode, \
         patch(
            find_user_path, 
            new_callable=AsyncMock, 
            return_value=mock_user
         ) as mock_find, \
         patch(
            create_token_path, 
            return_value="token123"
         ) as mock_create_token:

        mock_response = AsyncMock()
        mock_redirect.return_value = mock_response

        # Act
        response = await users_router.verify_email(request)

        # Assert
        mock_decode.assert_called_once_with("valid_token")
        mock_find.assert_awaited_once_with(email="test@test.com")
        mock_create_token.assert_called_once_with(
            email="test@test.com",
            user_id=mock_user.id
        )

        mock_redirect.assert_called_once_with(
            url="/main/",
            message="Вы успешно зарегистрированы!",
            success=True,
        )

        mock_response.set_cookie.assert_called_once_with(
            key="users_access_token",
            value="token123",
            httponly=True,
        )

        assert response == mock_response

    
@pytest.mark.asyncio
async def test_verify_email_user_not_found():
    """Токен валиден, но пользователь не найден."""

    form_data = {"token": "valid_token"}
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    decode_token_path = "app.users.router.decode_access_token"
    find_user_path = "app.users.router.UsersDAO.find_user"
    redirect_message_path = "app.users.router.redirect_message"

    with patch(decode_token_path, return_value="test@test.com"), \
         patch(find_user_path, new_callable=AsyncMock, return_value=None), \
         patch(redirect_message_path) as mock_redirect:

        # Act
        await users_router.verify_email(request)

        # Assert
        mock_redirect.assert_called_once_with(
            url="/auth/login/",
            message="Невалидный токен.",
            error=True,
        )


@pytest.mark.asyncio
async def test_verify_email_expired_token():
    """Истёк срок действия токена."""

    form_data = {"token": "expired_token"}
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    decode_token_path = "app.users.router.decode_access_token"
    redirect_message_path = "app.users.router.redirect_message"

    with patch(decode_token_path, side_effect=ExpiredSignatureError()), \
         patch(redirect_message_path) as mock_redirect:

        # Act
        await users_router.verify_email(request)

        # Assert
        mock_redirect.assert_called_once_with(
            url="/auth/login/",
            message="Истек срок годности токена.",
            error=True,
        )


@pytest.mark.asyncio
async def test_verify_email_invalid_token():
    """Токен битый или невалидный."""

    form_data = {"token": "bad_token"}
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    decode_token_path = "app.users.router.decode_access_token"
    redirect_message_path = "app.users.router.redirect_message"

    with patch(decode_token_path, side_effect=JWTError()), \
         patch(redirect_message_path) as mock_redirect:

        # Act
        await users_router.verify_email(request)

        # Assert
        mock_redirect.assert_called_once_with(
            url="/auth/login/",
            message="Невалидный токен.",
            error=True,
        )


@pytest.mark.asyncio
async def test_forgot_password_success():
    """Успешная отправка письма для восстановления пароля."""

    # Arrange
    form_data = {"email": "test@test.com"}
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    SUserForgot_path = "app.users.router.SUserForgotPassword"
    find_user_path = "app.users.router.UsersDAO.find_user"
    send_email_path = "app.users.router.send_verification_email"
    redirect_message_path = "app.users.router.redirect_message"

    mock_user = AsyncMock()

    with patch(SUserForgot_path) as mock_schema, \
         patch(send_email_path, new_callable=AsyncMock) as mock_email, \
         patch(redirect_message_path) as mock_redirect, \
         patch(
            find_user_path, 
            new_callable=AsyncMock, 
            return_value=mock_user
         ) as mock_find:

        mock_schema.return_value = mock_schema
        mock_schema.return_value.email = form_data["email"]

        mock_response = AsyncMock()
        mock_redirect.return_value = mock_response

        # Act
        response = await users_router.forgot_password_user(request)

        # Assert
        mock_schema.assert_called_once()
        mock_find.assert_awaited_once_with(email=form_data["email"])
        mock_email.assert_awaited_once_with(
            email=form_data["email"],
            title="Смена пароля.",
            text="Перейдите по ссылке, чтобы сменить пароль:",
            url_for_token="/auth/forgot_password/",
        )
        mock_redirect.assert_called_once_with(
            url="/auth/forgot_password/",
            message="Вам на почту отправлено письмо для смены пароля.",
            success=True,
        )
        assert response == mock_response


@pytest.mark.asyncio
async def test_forgot_password_validation_error():
    """Введена некорректная электронная почта."""

    request = AsyncMock()
    request.form = AsyncMock(return_value={"email": "bad_email"})

    redirect_message_path = "app.users.router.redirect_message"

    with patch(redirect_message_path) as mock_redirect:

        # Act
        await users_router.forgot_password_user(request)

        # Assert
        mock_redirect.assert_called_once_with(
            url="/auth/forgot_password/",
            message="Введена некорректная электронная почта.",
            error=True,
        )


@pytest.mark.asyncio
async def test_forgot_password_user_not_found():
    """Пользователь с таким email не зарегистрирован."""

    form_data = {"email": "test@test.com"}
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    SUserForgot_path = "app.users.router.SUserForgotPassword"
    find_user_path = "app.users.router.UsersDAO.find_user"
    redirect_message_path = "app.users.router.redirect_message"

    with patch(SUserForgot_path) as mock_schema, \
         patch(find_user_path, new_callable=AsyncMock, return_value=None), \
         patch(redirect_message_path) as mock_redirect:

        mock_schema.return_value = mock_schema
        mock_schema.return_value.email = form_data["email"]

        # Act
        await users_router.forgot_password_user(request)

        # Assert
        mock_redirect.assert_called_once_with(
            url="/auth/forgot_password/",
            message="Такой пользователь не зарегистрирован.",
            error=True,
        )


@pytest.mark.asyncio
async def test_update_password_success():
    """Успешное обновление пароля пользователя."""

    # Arrange
    form_data = {
        "token": "valid_token", 
        "password": "newpass", 
        "confirm_password": "newpass"
    }
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    SUserUpdate_path = "app.users.router.SUserUpdatePassword"
    decode_token_path = "app.users.router.decode_access_token"
    get_hash_path = "app.users.router.get_password_hash"
    update_password_path = "app.users.router.UsersDAO.update_user_password"
    redirect_message_path = "app.users.router.redirect_message"
    create_token_path = "app.users.router.create_access_token"
    find_user_path = "app.users.router.UsersDAO.find_user" 

    mock_user = AsyncMock()
    mock_user.id = 0

    with patch(SUserUpdate_path) as mock_schema, \
         patch(
            decode_token_path, 
            return_value="test@test.com"
         ) as mock_decode, \
         patch(get_hash_path, return_value="hashed_pw") as mock_hash, \
         patch(update_password_path, new_callable=AsyncMock) as mock_update, \
         patch(redirect_message_path) as mock_redirect, \
         patch(
            find_user_path,
            new_callable=AsyncMock,
            return_value=mock_user
         ) as mock_find, \
         patch(create_token_path, return_value="token123") as mock_create:

        mock_schema.return_value = mock_schema
        mock_schema.return_value.token = form_data["token"]
        mock_schema.return_value.password = form_data["password"]

        mock_response = AsyncMock()
        mock_redirect.return_value = mock_response

        # Act
        response = await users_router.update_password_user(request)

        # Assert
        mock_schema.assert_called_once()
        mock_decode.assert_called_once_with(token="valid_token")
        mock_hash.assert_called_once_with(password="newpass")
        mock_update.assert_awaited_once_with(
            email="test@test.com", 
            password="hashed_pw"
        )

        mock_find.assert_awaited_once_with(email="test@test.com")

        mock_create.assert_called_once_with(
            email="test@test.com",
            user_id=0)

        mock_redirect.assert_called_once_with(
            url="/main/",
            message="Пароль успешно изменен.",
            success=True,
        )
        mock_response.set_cookie.assert_called_once_with(
            key="users_access_token",
            value="token123",
            httponly=True,
        )
        assert response == mock_response


@pytest.mark.asyncio
async def test_update_password_validation_error():
    """Пароли не совпадают (ValidationError)."""

    form_data = {
        "token": "valid_token", 
        "password": "123", 
        "confirm_password": "321"
    }
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    redirect_message_path = "app.users.router.redirect_message"

    with patch(redirect_message_path) as mock_redirect:

        # Act
        await users_router.update_password_user(request)

        # Assert
        mock_redirect.assert_called_once_with(
            url="/auth/update_password/",
            message="Пароли не совпадают",
            error=True,
            token=form_data["token"]
        )
    

@pytest.mark.asyncio
async def test_update_password_expired_token():
    """Истёк срок действия токена."""

    form_data = {
        "token": "expired_token", 
        "password": "passsssss", 
        "confirm_password": "passsssss"
    }
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    decode_token_path = "app.users.router.decode_access_token"
    redirect_message_path = "app.users.router.redirect_message"

    with patch(decode_token_path, side_effect=ExpiredSignatureError()), \
         patch(redirect_message_path) as mock_redirect:

        # Act
        await users_router.update_password_user(request)

        # Assert
        mock_redirect.assert_called_once_with(
            url="/auth/login/",
            message="Истек срок годности токена.",
            error=True,
        )


@pytest.mark.asyncio
async def test_update_password_invalid_token():
    """Токен битый или невалидный."""

    form_data = {
        "token": "bad_token", 
        "password": "passsssss", 
        "confirm_password": "passsssss"
    }
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    decode_token_path = "app.users.router.decode_access_token"
    redirect_message_path = "app.users.router.redirect_message"

    with patch(decode_token_path, side_effect=JWTError()), \
         patch(redirect_message_path) as mock_redirect:

        # Act
        await users_router.update_password_user(request)

        # Assert
        mock_redirect.assert_called_once_with(
            url="/auth/login/",
            message="Невалидный токен.",
            error=True,
        )

    
@pytest.mark.asyncio
async def test_update_password_db_error():
    """Ошибка БД при обновлении пароля."""

    form_data = {
        "token": "valid_token",
        "password": "pass", 
        "confirm_password": "pass"
    }
    request = AsyncMock()
    request.form = AsyncMock(return_value=form_data)

    SUserUpdate_path = "app.users.router.SUserUpdatePassword"
    decode_token_path = "app.users.router.decode_access_token"
    get_hash_path = "app.users.router.get_password_hash"
    update_password_path = "app.users.router.UsersDAO.update_user_password"
    redirect_message_path = "app.users.router.redirect_message"

    with patch(SUserUpdate_path) as mock_schema, \
         patch(decode_token_path, return_value="test@test.com"), \
         patch(get_hash_path, return_value="hashed_pw"), \
         patch(
            update_password_path, 
            new_callable=AsyncMock, 
            side_effect=SQLAlchemyError()
         ), \
         patch(redirect_message_path) as mock_redirect:

        mock_schema.return_value = mock_schema
        mock_schema.return_value.token = form_data["token"]
        mock_schema.return_value.password = form_data["password"]

        # Act
        await users_router.update_password_user(request)

        # Assert
        mock_redirect.assert_called_once_with(
            url="/auth/login/",
            message="Возникла ошибка при обновлении пароля.",
            error=True,
        )