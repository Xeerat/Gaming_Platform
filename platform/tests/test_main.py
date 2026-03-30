from fastapi.testclient import TestClient
import pytest

from app.main import app


client = TestClient(app)


def test_load_page_register_no_error():
    """Проверка, что страница регистрации содержит все необходимое."""

    # Arrange
    reg_form = '<form action="/auth/register/" method="post">'
    inp_name = '<input type="text" id="username" name="username"'
    inp_email = '<input type="email" id="email" name="email"'
    inp_password = '<input type="password" id="password" name="password"'
    inp_conf_pass = '<input type="password" id="confirm_password" ' \
                    'name="confirm_password"'
    button = '<button type="submit" class="btn">Зарегистрироваться</button>'
    link_terms = '<a href="/auth/register/terms">'
    link_login = '<a href="/auth/login/">'

    # Act
    response = client.get("/auth/register/")

    # Assert
    assert response.status_code == 200
    assert reg_form in response.text
    assert inp_name in response.text
    assert inp_email in response.text
    assert inp_password in response.text
    assert inp_conf_pass in response.text
    assert button in response.text
    assert link_terms in response.text
    assert link_login in response.text


def test_load_page_register_with_error():
    """Проверка отображения ошибки на странице регистрации."""
    
    # Arrange
    error_message = "Почта уже существует"

    # Act
    response = client.get(f"/auth/register/?error={error_message}")

    # Assert
    assert response.status_code == 200
    assert error_message in response.text


def test_load_page_login_no_error():
    """Проверка, что страница авторизации содержит все необходимое."""

    # Arrange
    log_form = '<form action="/auth/login/" method="post">'
    inp_email = '<input type="text" id="email" name="email"'
    inp_password = '<input type="password" id="password" name="password"'
    enter_button = '<button type="submit" class="btn">Войти</button>'
    link_forgot = '<a href="/auth/forgot_password/">Забыли пароль?</a>'
    link_reg = '<a href="/auth/register/">Зарегистрироваться</a>'

    # Act
    response = client.get("/auth/login/") 

    # Assert
    assert response.status_code == 200
    assert log_form in response.text
    assert inp_email in response.text
    assert inp_password in response.text
    assert enter_button in response.text
    assert link_forgot in response.text
    assert link_reg in response.text


def test_load_page_login_with_error():
    """Проверка отображения ошибки на странице авторизации."""

    # Arrange
    error_message = "Неверная почта или пароль." 

    # Act 
    response = client.get(f"/auth/login/?error={error_message}")

    # Assert
    assert response.status_code == 200
    assert error_message in response.text


def test_load_page_login_with_success():
    """Проверка отображения успеха на странице авторизации."""

    # Arrange
    success_message = "Вы успешно вошли." 

    # Act 
    response = client.get(f"/auth/login/?success={success_message}")

    # Assert
    assert response.status_code == 200
    assert success_message in response.text


def test_load_page_terms():
    """
    Проверка, что страница с условиями использования содержит все необходимое.
    """

    # Arrange
    link_reg = '<a href="/auth/register/">На главную</a>'

    # Act
    response = client.get("/auth/register/terms")

    # Assert
    assert response.status_code == 200 
    assert link_reg in response.text


def test_load_page_verify_no_args():
    """
    Проверка, что страница для ожидания подтверждения email содержит 
    все необходимое.
    """

    # Arrange
    token_form = '<form action="/auth/verify-email" ' \
    'method="post" id="verify-email">'
    inp_token = '<input type="hidden" name="token" value='

    # Act 
    response = client.get("/auth/verify-email")

    # Assert
    assert response.status_code == 200
    assert token_form in response.text
    assert inp_token in response.text


def test_load_page_verify_with_token():
    """Проверка взаимодействия с токеном на странице верификации."""

    # Arrange
    token = "hdsfsdfsdfsdf"
    doc_token = "document.getElementById('verify-email').submit();"

    # Act 
    response = client.get(f"/auth/verify-email/?token={token}")

    # Assert 
    assert response.status_code == 200
    assert doc_token in response.text


def test_load_page_main_no_args():
    """Проверка, что главная страница содержит все необходимое."""

    # Arrange
    del_form = '<form id="deleteForm" action="/auth/del/" method="post">'
    del_button = '<button type="button" onclick="confirmDelete()">'
    const_form = '<form id="constructor" action="/main/constructor" ' \
    'method="get">'
    const_button = '<button type="button" onclick="confirmConstructor()">'
    exit_button = '<button onclick="confirmLogout()"'
    func_logout = 'function confirmLogout() {'
    link_logout = 'window.location.href = "/auth/logout/";'
    func_del = 'function confirmDelete() {'
    link_del = "document.getElementById('deleteForm').submit();"
    func_const = 'function confirmConstructor() {'
    link_const = "document.getElementById('constructor').submit();"

    # Act
    response = client.get("/main/")

    # Assert
    assert response.status_code == 200
    assert del_form in response.text
    assert del_button in response.text
    assert const_form in response.text
    assert const_button in response.text
    assert exit_button in response.text
    assert func_logout in response.text
    assert link_logout in response.text
    assert func_del in response.text
    assert link_del in response.text
    assert func_const in response.text
    assert link_const in response.text


def test_load_page_main_with_success():
    """Проверка, что сообщение об успехе на главной странице отображается."""

    # Arrange
    success_message = "Вы успешно зарегистрированы."

    # Act
    response = client.get(f"/main/?success={success_message}")

    # Assert
    assert response.status_code == 200
    assert success_message in response.text


def test_load_page_constructor():
    """Проверка, что страница конструктора содержит все необходимое."""

    # Act
    response = client.get("/main/constructor") 

    # Assert
    assert response.status_code == 200


def test_load_first_page_forgot_password_no_args():
    """
    Проверка, что первая страница вкладки "Забыли пароль?" содержит 
    все необходимое.
    """

    # Arrange
    main_form = '<form action="/auth/forgot_password/" method="POST"'
    inp_email = '<input type="email" id="email" name="email"'
    enter_button = '<button type="submit" class="btn">'
    messageBox = '<div id="messageBox" class="message hidden"></div>'
    url_params = 'const params = new URLSearchParams(window.location.search);'

    # Act
    response = client.get("/auth/forgot_password/")

    # Assert
    assert response.status_code == 200
    assert main_form in response.text
    assert inp_email in response.text
    assert enter_button in response.text
    assert messageBox in response.text
    assert url_params in response.text


def test_load_first_page_forgot_password_with_token():
    """
    Проверка отображения токена на первой странице вкладки "Забыли пароль?".
    """
    
    # Arrange
    token = "dddddddd"
    got_token = 'const token = params.get("token");'
    link_token = 'window.location.href = `/auth/update_password/?token=$'

    # Act 
    response = client.get(f"/auth/forgot_password/?token={token}")

    # Assert
    assert response.status_code == 200
    assert got_token in response.text
    assert link_token in response.text


def test_load_first_page_forgot_password_with_success():
    """
    Проверка отображения успеха на первой странице вкладки "Забыли пароль?".
    """
    
    # Arrange
    success = "dddddddd"
    got_success = 'const success = params.get("success");'

    # Act 
    response = client.get(f"/auth/forgot_password/?success={success}")

    # Assert
    assert response.status_code == 200
    assert got_success in response.text


def test_load_first_page_forgot_password_with_error():
    """
    Проверка отображения ошибки на первой странице вкладки "Забыли пароль?".
    """
    
    # Arrange
    error = "dddddddd"
    got_error = 'const error = params.get("error"); '

    # Act 
    response = client.get(f"/auth/forgot_password/?error={error}")

    # Assert
    assert response.status_code == 200
    assert got_error in response.text


def test_load_second_page_forgot_password_no_args():
    """
    Проверка, что вторая страница вкладки "Забыли пароль?" содержит 
    все необходимое.
    """

    # Arrange
    messageBox = '<div id="messageBox" class="message hidden"></div>'
    main_form = '<form action="/auth/update_password/" method="POST">'
    inp_pass = '<input type="password" id="password" name="password"'
    inp_token = '<input type="hidden" name="token" id="token">'
    inp_conf_pass = '<input type="password" id="confirm_password" ' \
    'name="confirm_password"'
    enter_button = '<button type="submit" class="btn">'
    url_params = 'const params = new URLSearchParams(window.location.search);'

    # Act
    response = client.get("/auth/update_password/")

    # Assert
    assert response.status_code == 200
    assert messageBox in response.text
    assert main_form in response.text
    assert inp_pass in response.text
    assert inp_token in response.text
    assert inp_conf_pass in response.text
    assert enter_button in response.text
    assert url_params in response.text


def test_load_second_page_forgot_password_with_error():
    """
    Проверка отображения ошибки на второй странице вкладки "Забыли пароль?".
    """

    # Arrange
    error = "dddddddd"
    got_error = 'const error = params.get("error"); '

    # Act 
    response = client.get(f"/auth/update_password/?error={error}")

    # Assert
    assert response.status_code == 200
    assert got_error in response.text


def test_load_second_page_forgot_password_with_token():
    """
    Проверка отображения токена на второй странице вкладки "Забыли пароль?".
    """

    # Arrange
    token = "dddddddd"
    got_token = 'const token = params.get("token");'
    link_token = 'document.getElementById("token").value = token;'

    # Act 
    response = client.get(f"/auth/update_password/?token={token}")

    # Assert
    assert response.status_code == 200
    assert got_token in response.text
    assert link_token in response.text
