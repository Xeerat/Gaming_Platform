from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from users.router import router as router_users

from typing import Optional


app = FastAPI()
app.include_router(router_users)

app.mount('/static', StaticFiles(directory="site/static"), name="static")
templates = Jinja2Templates(directory="site/templates")


@app.get("/auth/register/", response_class=HTMLResponse)
def load_page_register(request: Request, error: Optional[str] = None):
    """
    Загружает страницу регистрации.

    Args:
        error: сообщение об ошибке, передаваемое в ссылке RedirectResponse.
    """

    return templates.TemplateResponse(
        'register.html', 
        {
            "request": request,
            "error": error,
        },
    )


@app.get("/auth/login/", response_class=HTMLResponse)
def load_page_login(
    request: Request, 
    success: Optional[str] = None, 
    error: Optional[str] = None,
):
    """
    Загружает страницу аутентификации.

    Args:
        success: сообщение об успехе, передаваемое в ссылке RedirectResponse. 
        error: сообщение об ошибке, передаваемое в ссылке RedirectResponse.
    """

    return templates.TemplateResponse(
        'login.html', 
        {
            "request": request,
            "success": success,
            "error": error,
        },
    )


@app.get("/auth/register/terms", response_class=HTMLResponse)
def load_page_terms(request: Request):
    """Загружает страницу с условиями использования."""

    return templates.TemplateResponse(
        'terms_use.html', 
        {
            "request": request,
        },
    )


@app.get("/auth/verify-email", response_class=HTMLResponse)
def load_page_verify_email(request: Request, token: str = None):
    """Загружает страницу подтверждения email."""

    return templates.TemplateResponse(
        'verify_email.html', 
        {
            "request": request, 
            "token": token,
        },
    )


@app.get("/main/", response_class=HTMLResponse)
def load_page_main(request: Request, success: Optional[str] = None):
    """
    Загружает основную страницу после входа в профиль.
    
    Args:
        success: сообщение об успехе передаваемое в ссылке RedirectResponse.
    """

    return templates.TemplateResponse(
        'main_page.html', 
        {
            "request": request,
            "success": success,
        },
    )


@app.get("/main/constructor", response_class=HTMLResponse)
def load_page_constructor(request: Request):
    """Загружает страницу конструктора."""
    
    return templates.TemplateResponse(
        'constructor.html', 
        {
            "request": request,
        },
    )


@app.get("/auth/forgot_password/", response_class=HTMLResponse)
def load_first_page_forgot_password(
    request: Request,
    success: Optional[str] = None,
    error: Optional[str] = None,
    token: Optional[str] = None,
):
    """Загружает первую страницу вкладки 'Забыли пароль?'"""

    return templates.TemplateResponse(
        'forgot_password1.html',
        {
            "request": request,
            "success": success,
            "error": error,
            "token": token,
        }
    )


@app.get("/auth/update_password/", response_class=HTMLResponse)
def load_second_page_forgot_password(
    request: Request, 
    error: Optional[str] = None,
    token: Optional[str] = None,
):
    """Загружает вторую страницу вкладки 'Забыли пароль?'"""

    return templates.TemplateResponse(
        "forgot_password2.html",
        {
            "request": request,
            "error": error,
            "token": token,
        }
    )