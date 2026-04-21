FROM python:3.11-slim

WORKDIR /platform

ENV HF_HUB_DISABLE_XET=1

# Системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip setuptools wheel

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего приложения (папка app из корня в /app в контейнере)
COPY app/ app/

# Копирование alembic (если нужно для миграций)
COPY alemb/ alemb/
COPY alembic.ini .

# Копирование тестов
COPY tests/ tests/
COPY pytest.ini . 

# Команда для запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]