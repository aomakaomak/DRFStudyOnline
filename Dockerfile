FROM python:3.13-slim

# Рабочая директория
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
#  УСТАНОВКА POETRY
# -----------------------------
ENV POETRY_VERSION=1.8.3
ENV POETRY_HOME=/opt/poetry
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 -

# Poetry не создаёт виртуальное окружение внутри контейнера
RUN poetry config virtualenvs.create false

# -----------------------------
#  КОПИРУЕМ ФАЙЛЫ ПОЭТРИ
# -----------------------------
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости (prod + dev при необходимости)
RUN poetry install --no-root

# -----------------------------
#  КОПИРУЕМ ВСЁ ПРИЛОЖЕНИЕ
# -----------------------------
COPY . .

# Открываем Django порт
EXPOSE 8000

# Команда по умолчанию (будет переопределена в docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
