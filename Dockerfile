FROM python:3.9-slim

WORKDIR /app

# Создаем непривилегированного пользователя для запуска приложения
RUN useradd -m -u 1000 botuser

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения
COPY . .

# Устанавливаем права на всю директорию /app для botuser
RUN chown -R botuser:botuser /app



# Путь к файлу базы данных (можно переопределить переменной окружения)
DATABASE_DIR=/data
DATABASE_FILE=/data/database.json

# Переключаемся на непривилегированного пользователя
USER botuser



# Запускаем бота
CMD ["python", "bot.py"]


