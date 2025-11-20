FROM python:3.9-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВСЕ файлы включая database.json
COPY . .

# Создаем директорию для данных
RUN mkdir -p /data && chmod 755 /data

# Копируем database.json в рабочую директорию (на всякий случай)
COPY database.json /app/database.json

# Устанавливаем переменные окружения
ENV DATABASE_DIR=/data
ENV DATABASE_FILE=/data/database.json
ENV PYTHONUNBUFFERED=1

# Запускаем бота
CMD ["python", "bot.py"]

