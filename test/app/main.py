from pathlib import Path
from sys import path

# Добавляем корень проекта в пути, для нормальной работы импо
path_to_root = str(Path(__file__).parent.parent)
path.append(path_to_root)

from fastapi import FastAPI
# Файл где определены маршруты для работы с пользователями
# Маршрут это связь между url и функцией
# Он отвечает за то какая функция будет выполняться, после перехода по url
from users.router import router as router_users

# Создаем объект для работы с http-запросами
app = FastAPI()

# Подключаем все маршруты пользователя к главному объекту 
app.include_router(router_users)
