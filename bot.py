"""Чат-бот ВСЕЗНАЙКА для помощи студентам"""
import aiomax
import asyncio
import logging
from database import Database
from notifications import NotificationService
from handlers import register_handlers

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = 'f9LHodD0cOK0MXgEgBGykdNp_UoBc0rTQrRsEBumJJbAsbNDQlwYPtMn5rgCOAYZVrdWJmhZh5sMC97PwzVt'

# Создаем экземпляр бота и базу данных
bot = aiomax.Bot(TOKEN)
db = Database()
notification_service = NotificationService(bot, db)


def run_bot_with_notifications():
    """Запускает бота и сервис напоминаний в одном event loop"""
    # Регистрируем все обработчики
    register_handlers(bot, db, notification_service)
    
    # Запускаем бота (блокирующий вызов)
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Остановка бота...")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)


async def main():
    """Главная функция запуска бота"""
    logger.info("🤖 Запуск бота ВСЕЗНАЙКА...")
    
    # Запускаем бота в отдельном потоке с его собственным event loop
    import threading
    
    bot_thread = threading.Thread(target=run_bot_with_notifications, daemon=True)
    bot_thread.start()
    
    # Держим основной цикл запущенным
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Остановка бота...")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске: {e}", exc_info=True)
