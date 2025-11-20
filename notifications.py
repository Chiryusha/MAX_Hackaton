"""Модуль для отправки напоминаний о мероприятиях"""
import asyncio
import logging
from datetime import datetime, timedelta
from database import Database

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис для отправки напоминаний о мероприятиях"""
    
    def __init__(self, bot, db: Database):
        self.bot = bot
        self.db = db
        self.running = False
        self.sent_notifications = set()  # Храним уже отправленные напоминания
        self.bot_loop = None  # Event loop бота
    
    async def start(self, bot_loop=None):
        """Запускает сервис напоминаний"""
        self.running = True
        self.bot_loop = bot_loop  # Сохраняем event loop бота
        logger.info("🔔 Сервис напоминаний запускается...")
        asyncio.create_task(self._notification_loop())
    
    async def stop(self):
        """Останавливает сервис напоминаний"""
        self.running = False
        logger.info("🔔 Сервис напоминаний остановлен")
    
    async def _notification_loop(self):
        """Основной цикл проверки и отправки напоминаний"""
        logger.info("🔔 Цикл проверки напоминаний запущен")
        while self.running:
            try:
                await self._check_and_send_notifications()
                # Проверяем каждую минуту для более точных напоминаний
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Ошибка в цикле напоминаний: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    async def _check_and_send_notifications(self):
        """Проверяет мероприятия и отправляет напоминания"""
        events = self.db.get_events()
        now = datetime.now()
        
        logger.info(f"🔍 Проверка напоминаний. Всего мероприятий: {len(events)}")
        
        for event in events:
            try:
                event_id = event.get('id', 'unknown')
                event_title = event.get('title', 'Без названия')
                logger.debug(f"📋 Проверка мероприятия ID={event_id}: {event_title}")
                
                # Парсим дату мероприятия
                event_date = datetime.fromisoformat(event['date'])
                
                # Проверяем, нужно ли отправить напоминание
                time_until_event = event_date - now
                time_until_event_seconds = time_until_event.total_seconds()
                
                logger.debug(f"   Время до события ID={event_id}: {time_until_event} ({time_until_event_seconds:.0f} секунд)")
                
                # Пропускаем прошедшие события
                if time_until_event_seconds < 0:
                    logger.debug(f"   ⏭️ Событие ID={event_id} уже прошло, пропускаем")
                    continue
                
                notification_key = None
                time_text = None
                
                # Напоминание за 1 день (23-25 часов до события)
                if timedelta(hours=23) <= time_until_event <= timedelta(hours=25):
                    notification_key = f"{event_id}_1day"
                    time_text = "через 1 день"
                    logger.info(f"   ⏰ Найдено напоминание за 1 день для события ID={event_id}")
                
                # Напоминание за 1 час (50-70 минут до события)
                elif timedelta(minutes=50) <= time_until_event <= timedelta(minutes=70):
                    notification_key = f"{event_id}_1hour"
                    time_text = "через 1 час"
                    logger.info(f"   ⏰ Найдено напоминание за 1 час для события ID={event_id}")
                
                # Напоминание за 15 минут (10-20 минут до события)
                elif timedelta(minutes=10) <= time_until_event <= timedelta(minutes=20):
                    notification_key = f"{event_id}_15min"
                    time_text = "через 15 минут"
                    logger.info(f"   ⏰ Найдено напоминание за 15 минут для события ID={event_id}")
                
                # Отправляем напоминание, если нужно и еще не отправляли
                if notification_key:
                    if notification_key not in self.sent_notifications:
                        logger.info(f"   📤 Отправка напоминания для события ID={event_id} ({time_text})")
                        await self._send_notification(event, time_text, notification_key)
                    else:
                        logger.debug(f"   ✅ Напоминание для события ID={event_id} уже отправлено")
                else:
                    logger.debug(f"   ⏳ Событие ID={event_id} не в диапазоне для напоминаний")
            
            except Exception as e:
                logger.error(f"❌ Ошибка при обработке мероприятия {event.get('id', 'unknown')}: {e}", exc_info=True)
    
    async def _send_notification(self, event: dict, time_text: str, notification_key: str):
        """Отправляет напоминание о мероприятии"""
        subscribers = event.get('subscribers', [])
        
        if not subscribers:
            logger.debug(f"Нет подписчиков для мероприятия {event['id']}")
            return
        
        notification_text = (
            f"🔔 Напоминание о мероприятии!\n\n"
            f"📅 {event['title']}\n"
            f"📝 {event.get('description', 'Без описания')}\n"
            f"🗓 Дата: {event['date']}\n\n"
            f"⏰ Мероприятие начнется {time_text}!"
        )
        
        sent_count = 0
        for user_id in subscribers:
            try:
                user = self.db.get_user(user_id)
                if user and user.get('notifications_enabled', True):
                    # Пробуем отправить сообщение разными способами
                    sent = await self._try_send_message(user_id, notification_text)
                    
                    if sent:
                        sent_count += 1
                        logger.info(f"✅ Отправлено напоминание пользователю {user_id} о мероприятии {event['id']}")
                        await asyncio.sleep(0.5)  # Задержка между сообщениями
                    else:
                        logger.warning(f"⚠️ Не удалось отправить напоминание пользователю {user_id}")
                else:
                    logger.debug(f"Уведомления отключены для пользователя {user_id}")
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления пользователю {user_id}: {e}", exc_info=True)
        
        if sent_count > 0:
            # Помечаем, что напоминание отправлено
            self.sent_notifications.add(notification_key)
            logger.info(f"✅ Отправлено {sent_count} напоминаний о мероприятии {event['id']} ({time_text})")
    
    async def _try_send_message(self, user_id: str, text: str) -> bool:
        """Пробует отправить сообщение пользователю разными способами"""
        # Все вызовы должны быть в том же event loop, что и бот
        # Способ 1: send_message с chat_id как int
        try:
            await self.bot.send_message(chat_id=int(user_id), text=text)
            logger.info(f"✅ Сообщение отправлено способом 1 (chat_id=int)")
            return True
        except Exception as e1:
            logger.debug(f"Способ 1 (chat_id=int) не сработал: {type(e1).__name__}: {e1}")
        
        # Способ 2: send_message с chat_id как str
        try:
            await self.bot.send_message(chat_id=str(user_id), text=text)
            logger.info(f"✅ Сообщение отправлено способом 2 (chat_id=str)")
            return True
        except Exception as e2:
            logger.debug(f"Способ 2 (chat_id=str) не сработал: {type(e2).__name__}: {e2}")
        
        # Способ 3: send_message с user_id
        try:
            await self.bot.send_message(user_id=int(user_id), text=text)
            logger.info(f"✅ Сообщение отправлено способом 3 (user_id)")
            return True
        except Exception as e3:
            logger.debug(f"Способ 3 (user_id) не сработал: {type(e3).__name__}: {e3}")
        
        # Способ 4: позиционные аргументы
        try:
            await self.bot.send_message(int(user_id), text)
            logger.info(f"✅ Сообщение отправлено способом 4 (позиционные)")
            return True
        except Exception as e4:
            logger.debug(f"Способ 4 (позиционные) не сработал: {type(e4).__name__}: {e4}")
        
        # Способ 5: через внутренний API клиент (если доступен)
        try:
            if hasattr(self.bot, '_client') or hasattr(self.bot, 'client'):
                client = getattr(self.bot, '_client', None) or getattr(self.bot, 'client', None)
                if client and hasattr(client, 'send_message'):
                    await client.send_message(chat_id=int(user_id), text=text)
                    logger.info(f"✅ Сообщение отправлено способом 5 (через client)")
                    return True
        except Exception as e5:
            logger.debug(f"Способ 5 (через client) не сработал: {type(e5).__name__}: {e5}")
        
        logger.error(f"❌ Все способы отправки не сработали для пользователя {user_id}")
        return False

