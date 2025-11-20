FROM python:3.9-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем директорию для данных
RUN mkdir -p /data && chmod 755 /data

# Устанавливаем переменные окружения по умолчанию
ENV DATABASE_DIR=/data
ENV DATABASE_FILE=/data/database.json

# Запускаем бота
CMD ["python", "bot.py"]
