FROM python:3.11-slim

WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего приложения (папка app из корня в /app в контейнере)
COPY app/ .

# Копирование alembic (если нужно для миграций)
COPY alemb/ ../alemb/
COPY alembic.ini ..



# Команда для запуска
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]