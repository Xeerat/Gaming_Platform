from pathlib import Path
from sys import path
# Добавляем корень проекта в пути, для нормальной работы импортов
path_to_root = str(Path(__file__).parent.parent)
path.append(path_to_root)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.users.router import router as router_users

#=========================================================
# Проверка валидности при регистрации
#=========================================================

# Создаем объект для работы с http-запросами
app = FastAPI()
# Подключаем все маршруты пользователя к главному объекту 
app.include_router(router_users)
# Добавляем статические файлы на сайт
app.mount('/static', StaticFiles(directory="site/static"), name="static")
# Показываем где искать HTML файлы
templates = Jinja2Templates(directory="site/templates")

#=========================================================
# Страница регистрации
#=========================================================

@app.get("/auth/register/", response_class=HTMLResponse)
async def register(request: Request, error: str = None):
    return templates.TemplateResponse('register.html', {
        "request": request,
        "error": error
    })

#=========================================================
# Страница авторизации
#=========================================================

@app.get("/auth/login/", response_class=HTMLResponse)
async def login(request: Request, success: str = None, error: str = None):
    return templates.TemplateResponse('login.html', {
        "request": request,
        "success": success,
        "error": error
    })

#=========================================================
# Страница с условиями использования
#=========================================================

@app.get("/auth/register/terms", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse('terms_use.html', {"request": request})

#=========================================================
# Страница подтверждения почты
#=========================================================

@app.get("/auth/verify-email", response_class=HTMLResponse)
async def verify_email(request: Request, token: str = None):
    return templates.TemplateResponse('verify_email.html', {
        "request": request, 
        "token": token
    })

#=========================================================
# Основная страница после входа
#=========================================================

@app.get("/main/", response_class=HTMLResponse)
async def main_paper(request: Request, success: str = None):
    return templates.TemplateResponse('main_page.html', {
        "request": request,
        "success": success
    })

#=========================================================
# Страница с конструктором
#=========================================================

@app.get("/main/constructor", response_class=HTMLResponse)
async def constructor(request: Request):
    return templates.TemplateResponse('constructor.html', {"request": request})