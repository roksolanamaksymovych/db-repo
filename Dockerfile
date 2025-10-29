# Використовуємо офіційний Python образ
FROM python:3.11-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Встановлюємо системні залежності для MySQL
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо файл залежностей
COPY requirements.txt .

# Встановлюємо Python залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код додатку
COPY . .

# Відкриваємо порт
EXPOSE 5000

# Встановлюємо змінні середовища
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Запускаємо додаток через gunicorn для production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]

