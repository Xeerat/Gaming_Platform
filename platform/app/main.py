from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.users.router import router as users_router
from app.constructor.sprites_constructor_router import router as sprites_router
from app.constructor.maps_constructor_router import router as maps_router

from typing import Optional


app = FastAPI()

app.include_router(users_router)
app.include_router(sprites_router)
app.include_router(maps_router)

app.mount('/static', StaticFiles(directory="app/site/static"), name="static")
templates = Jinja2Templates(directory="app/site/templates")


@app.get("/auth/register/", response_class=HTMLResponse)
def load_page_register(request: Request, error: Optional[str] = None):
    """
    Загружает страницу регистрации.

    Args:
        error: сообщение об ошибке, передаваемое в ссылке RedirectResponse.
    """

    return templates.TemplateResponse(
        request=request,
        name='register.html', 
        context={
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
        request=request, 
        name='login.html', 
        context={
            "request": request,
            "success": success,
            "error": error,
        },
    )


@app.get("/auth/register/terms", response_class=HTMLResponse)
def load_page_terms(request: Request):
    """Загружает страницу с условиями использования."""

    return templates.TemplateResponse(
        request=request,
        name='terms_use.html', 
        context={
            "request": request,
        },
    )


@app.get("/auth/verify-email", response_class=HTMLResponse)
def load_page_verify_email(request: Request, token: str = None):
    """Загружает страницу подтверждения email."""

    return templates.TemplateResponse(
        request=request,
        name='verify_email.html', 
        context={
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
        request=request,
        name='main_page.html', 
        context={
            "request": request,
            "success": success,
        },
    )


@app.get("/main/constructor", response_class=HTMLResponse)
def load_page_constructor(request: Request):
    """Загружает страницу конструктора."""
    
    return templates.TemplateResponse(
        request=request,
        name='constructor.html', 
        context={
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
        request=request,
        name='forgot_password1.html',
        context={
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
        request=request,
        name="forgot_password2.html",
        context={
            "request": request,
            "error": error,
            "token": token,
        }
    )