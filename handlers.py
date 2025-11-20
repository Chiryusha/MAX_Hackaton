"""Обработчики команд бота ВСЕЗНАЙКА"""
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def format_event(event: dict) -> str:
    """Форматирует мероприятие для отображения"""
    return f"📅 {event['title']}\n" \
           f"📝 {event.get('description', 'Без описания')}\n" \
           f"🗓 Дата: {event['date']}\n" \
           f"👤 Организатор: {event.get('organizer', 'Не указан')}\n" \
           f"🆔 ID: {event['id']}"


def get_command(text: str) -> str:
    """Извлекает команду из текста, убирая @username и параметры"""
    if not text or not text.startswith('/'):
        return None
    
    # Убираем @username бота если есть
    text = text.split('@')[0] if '@' in text else text
    
    # Берем только команду без параметров
    command = text.split()[0] if text.split() else text
    
    return command.strip()


def register_handlers(bot, db, notification_service=None):
    """Регистрирует все обработчики команд"""
    
    notification_started = False
    
    @bot.on_message()
    async def handle_message(message):
        """Главный обработчик всех сообщений"""
        nonlocal notification_started
        
        # Запускаем сервис напоминаний при первом сообщении
        if notification_service and not notification_started:
            notification_started = True
            try:
                loop = asyncio.get_running_loop()
                notification_service.bot_loop = loop
                asyncio.create_task(notification_service.start())
                logger.info("✅ Сервис напоминаний запущен в event loop бота")
            except Exception as e:
                logger.error(f"Ошибка запуска сервиса напоминаний: {e}", exc_info=True)
        
        # Упрощенная обработка без лишних проверок
        try:
            # Получаем текст сообщения - в aiomax это message.body.text или message.content
            text = None
            try:
                if hasattr(message, 'body') and message.body:
                    if hasattr(message.body, 'text'):
                        text = message.body.text
                elif hasattr(message, 'content'):
                    text = message.content
                elif hasattr(message, 'text'):
                    text = message.text
            except Exception as e:
                logger.debug(f"Ошибка получения текста: {e}")
            
            if not text:
                return
            
            text = str(text).strip()
            
            # Получаем user_id - в aiomax это message.user_id или message.sender.user_id
            user_id = None
            
            # Вариант 1: message.user_id (прямое свойство)
            try:
                if hasattr(message, 'user_id'):
                    user_id = str(message.user_id)
            except Exception as e:
                logger.debug(f"Ошибка получения user_id: {e}")
            
            # Вариант 2: message.sender.user_id
            if not user_id:
                try:
                    if hasattr(message, 'sender') and message.sender:
                        if hasattr(message.sender, 'user_id'):
                            user_id = str(message.sender.user_id)
                except Exception as e:
                    logger.debug(f"Ошибка получения sender.user_id: {e}")
            
            if not user_id:
                logger.warning("Не удалось получить user_id из сообщения")
                return
            
            # Извлекаем команду
            command = get_command(text)
            
            logger.info(f"Сообщение от {user_id}: '{text}' -> команда: '{command}'")
            
            # Обработка команды /start
            if command == '/start':
                await handle_start(message, db, user_id)
                return
            
            # Обработка команды /register
            if command == '/register':
                await handle_register(message, db, user_id)
                return
            
            # Обработка команды /calendar
            if command == '/calendar':
                await handle_calendar(message, db, user_id)
                return
            
            # Обработка команды /event (список или конкретное мероприятие)
            if command == '/event':
                # Если просто /event без номера - показываем список
                parts = text.split()
                if len(parts) == 1:
                    await handle_show_all_events(message, db, user_id)
                else:
                    await handle_event_info(message, db, user_id, text)
                return
            
            # Обработка команды /my_events
            if command == '/my_events':
                await handle_my_events(message, db, user_id)
                return
            
            # Обработка команды /subscribe <номер> или просто "подписаться"
            if command == '/subscribe' or text.lower() in ['подписаться', 'subscribe']:
                # Если просто "подписаться" без номера, показываем список
                if text.lower() in ['подписаться', 'subscribe']:
                    await handle_show_events_for_subscribe(message, db, user_id)
                else:
                    await handle_subscribe(message, db, user_id, text)
                return
            
            # Обработка команды /unsubscribe <ID>
            if command == '/unsubscribe':
                await handle_unsubscribe(message, db, user_id, text)
                return
            
            # Обработка команды /help
            if command == '/help':
                await handle_help(message)
                return
            
            # Неизвестная команда
            if command and command.startswith('/'):
                await message.reply("❌ Неизвестная команда. Используйте /help для списка команд")
        
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)
            # Не выводим ошибку пользователю, просто логируем
    
    logger.info("✅ Все обработчики зарегистрированы")


async def handle_start(message, db, user_id):
    """Обработчик команды /start"""
    try:
        if db.is_user_registered(user_id):
            await message.reply(
                f"👋 Добро пожаловать обратно!\n\n"
                f"Используйте команды для навигации:\n"
                f"📅 /event - Список всех мероприятий\n"
                f"📅 /calendar - Календарь мероприятий\n"
                f"📋 /my_events - Мои мероприятия\n"
                f"ℹ️ /help - Помощь"
            )
        else:
            await message.reply(
                f"👋 Добро пожаловать в чат-бот ВСЕЗНАЙКА!\n\n"
                f"Я помогу вам с:\n"
                f"• Регистрацией на мероприятия\n"
                f"• Напоминаниями о событиях\n"
                f"• Календарем внеучебных событий\n\n"
                f"📌 Для регистрации отправьте команду:\n"
                f"/register"
            )
    except Exception as e:
        logger.error(f"Ошибка в handle_start: {e}", exc_info=True)


async def handle_register(message, db, user_id):
    """Обработчик регистрации пользователя"""
    try:
        if db.is_user_registered(user_id):
            await message.reply("✅ Вы уже зарегистрированы!")
            return
        
        # Регистрируем пользователя
        username = None
        full_name = None
        
        # Получаем данные из message.sender (в aiomax)
        if hasattr(message, 'sender') and message.sender:
            if hasattr(message.sender, 'name'):
                full_name = message.sender.name
            if hasattr(message.sender, 'username'):
                username = message.sender.username
        
        db.register_user(user_id, username, full_name)
        
        await message.reply(
            f"✅ Регистрация успешна!\n\n"
            f"Теперь вы можете:\n"
            f"• Просматривать мероприятия: /event\n"
            f"• Просматривать календарь: /calendar\n"
            f"• Подписываться на события: /subscribe <номер>\n"
            f"• Просматривать свои мероприятия: /my_events\n\n"
            f"Начните с просмотра мероприятий: /event"
        )
        logger.info(f"Пользователь {user_id} успешно зарегистрирован")
    except Exception as e:
        logger.error(f"Ошибка в handle_register: {e}", exc_info=True)


async def handle_calendar(message, db, user_id):
    """Обработчик календаря внеучебных событий"""
    try:
        if not db.is_user_registered(user_id):
            await message.reply("❌ Вы не зарегистрированы. Используйте /start и /register")
            return
        
        events = db.get_events()
        
        if not events:
            await message.reply(
                "📅 Календарь мероприятий пуст.\n\n"
                "Пока нет доступных внеучебных событий."
            )
            return
        
        # Группируем мероприятия по датам
        events_by_date = {}
        for event in events:
            try:
                event_date = datetime.fromisoformat(event['date'])
                date_key = event_date.strftime('%d.%m.%Y')
                if date_key not in events_by_date:
                    events_by_date[date_key] = []
                events_by_date[date_key].append(event)
            except:
                if 'Без даты' not in events_by_date:
                    events_by_date['Без даты'] = []
                events_by_date['Без даты'].append(event)
        
        # Формируем календарь
        calendar_text = "📅 Календарь внеучебных мероприятий:\n\n"
        
        # Сортируем даты
        sorted_dates = sorted(
            [d for d in events_by_date.keys() if d != 'Без даты'],
            key=lambda x: datetime.strptime(x, '%d.%m.%Y')
        )
        if 'Без даты' in events_by_date:
            sorted_dates.append('Без даты')
        
        for date_key in sorted_dates:
            calendar_text += f"🗓 {date_key}:\n"
            for event in events_by_date[date_key]:
                try:
                    event_date = datetime.fromisoformat(event['date'])
                    time_str = event_date.strftime('%H:%M')
                    calendar_text += f"  ⏰ {time_str} - {event['title']} (№{event['id']})\n"
                except:
                    calendar_text += f"  📌 {event['title']} (№{event['id']})\n"
            calendar_text += "\n"
        
        calendar_text += "Для подписки: /subscribe <номер>\n"
        calendar_text += "Подробнее: /event <номер>"
        
        await message.reply(calendar_text)
    except Exception as e:
        logger.error(f"Ошибка в handle_calendar: {e}", exc_info=True)


async def handle_show_all_events(message, db, user_id):
    """Показывает список всех мероприятий"""
    try:
        if not db.is_user_registered(user_id):
            await message.reply("❌ Вы не зарегистрированы. Используйте /start и /register")
            return
        
        events = db.get_events()
        if not events:
            await message.reply("📅 Пока нет доступных мероприятий")
            return
        
        events_text = "📅 Доступные мероприятия:\n\n"
        for event in events:
            try:
                event_date = datetime.fromisoformat(event['date'])
                date_str = event_date.strftime('%d.%m.%Y %H:%M')
            except:
                date_str = event['date']
            
            events_text += f"{event['id']}. {event['title']}\n"
            events_text += f"   📅 {date_str}\n"
            events_text += f"   👤 {event.get('organizer', 'Не указан')}\n\n"
        
        events_text += "Для подписки используйте: /subscribe <номер>\n"
        events_text += "Для подробной информации: /event <номер>\n"
        events_text += "Например: /event 0"
        
        await message.reply(events_text)
    except Exception as e:
        logger.error(f"Ошибка в handle_show_all_events: {e}", exc_info=True)


async def handle_event_info(message, db, user_id, text):
    """Обработчик получения информации о конкретном мероприятии"""
    try:
        parts = text.split()
        if len(parts) < 2:
            await message.reply("❌ Укажите номер мероприятия: /event <номер>\n\nИспользуйте /event для просмотра списка")
            return
        
        try:
            event_id = int(parts[1])
            event = db.get_event(event_id)
            
            if not event:
                await message.reply(f"❌ Мероприятие с номером {event_id} не найдено")
                return
            
            event_text = format_event(event)
            
            user = db.get_user(user_id)
            is_subscribed = event_id in user.get('subscribed_events', []) if user else False
            
            event_text += f"\n\n{'✅ Вы подписаны на это мероприятие' if is_subscribed else '❌ Вы не подписаны'}"
            if not is_subscribed:
                event_text += f"\n\nДля подписки используйте: /subscribe {event_id}"
            else:
                event_text += f"\n\nДля отписки используйте: /unsubscribe {event_id}"
            
            await message.reply(event_text)
        
        except ValueError:
            await message.reply("❌ Неверный формат. Используйте число, например: /event 0")
    except Exception as e:
        logger.error(f"Ошибка в handle_event_info: {e}", exc_info=True)


async def handle_my_events(message, db, user_id):
    """Обработчик просмотра своих мероприятий"""
    try:
        if not db.is_user_registered(user_id):
            await message.reply("❌ Вы не зарегистрированы. Используйте /start и /register")
            return
        
        user_events = db.get_user_events(user_id)
        if not user_events:
            await message.reply("📅 Вы не подписаны ни на одно мероприятие")
            return
        
        events_text = "📅 Ваши мероприятия:\n\n"
        for event in user_events:
            events_text += f"{format_event(event)}\n\n"
        
        events_text += "Используйте /unsubscribe <ID> для отписки"
        await message.reply(events_text)
    except Exception as e:
        logger.error(f"Ошибка в handle_my_events: {e}", exc_info=True)


async def handle_show_events_for_subscribe(message, db, user_id):
    """Показывает список мероприятий для подписки"""
    try:
        if not db.is_user_registered(user_id):
            await message.reply("❌ Вы не зарегистрированы. Используйте /start и /register")
            return
        
        events = db.get_events()
        if not events:
            await message.reply("📅 Пока нет доступных мероприятий")
            return
        
        events_text = "📅 Список мероприятий для подписки:\n\n"
        for event in events:
            try:
                event_date = datetime.fromisoformat(event['date'])
                date_str = event_date.strftime('%d.%m.%Y %H:%M')
            except:
                date_str = event['date']
            
            events_text += f"{event['id']}. {event['title']}\n"
            events_text += f"   📅 {date_str}\n"
            events_text += f"   👤 {event.get('organizer', 'Не указан')}\n\n"
        
        events_text += "Для подписки используйте: /subscribe <номер>\n"
        events_text += "Например: /subscribe 0"
        
        await message.reply(events_text)
    except Exception as e:
        logger.error(f"Ошибка в handle_show_events_for_subscribe: {e}", exc_info=True)


async def handle_subscribe(message, db, user_id, text):
    """Обработчик подписки на мероприятие"""
    try:
        if not db.is_user_registered(user_id):
            await message.reply("❌ Вы не зарегистрированы. Используйте /start и /register")
            return
        
        parts = text.split()
        if len(parts) < 2:
            await message.reply("❌ Укажите номер мероприятия: /subscribe <номер>\n\nИспользуйте /subscribe без номера для просмотра списка")
            return
        
        try:
            event_id = int(parts[1])
            event = db.get_event(event_id)
            if event:
                if db.subscribe_to_event(user_id, event_id):
                    await message.reply(
                        f"✅ Вы подписались на мероприятие:\n"
                        f"📅 {event['title']}\n"
                        f"🗓 {event['date']}\n\n"
                        f"Вы будете получать напоминания о нем!"
                    )
                else:
                    await message.reply("❌ Ошибка при подписке")
            else:
                await message.reply(f"❌ Мероприятие с номером {event_id} не найдено")
        except ValueError:
            await message.reply("❌ Неверный формат. Используйте число, например: /subscribe 0")
    except Exception as e:
        logger.error(f"Ошибка в handle_subscribe: {e}", exc_info=True)


async def handle_unsubscribe(message, db, user_id, text):
    """Обработчик отписки от мероприятия"""
    try:
        parts = text.split()
        if len(parts) < 2:
            await message.reply("❌ Укажите ID мероприятия: /unsubscribe <ID>")
            return
        
        try:
            event_id = int(parts[1])
            if db.unsubscribe_from_event(user_id, event_id):
                await message.reply(f"✅ Вы отписались от мероприятия #{event_id}")
            else:
                await message.reply("❌ Мероприятие не найдено")
        except ValueError:
            await message.reply("❌ Неверный формат ID. Используйте число")
    except Exception as e:
        logger.error(f"Ошибка в handle_unsubscribe: {e}", exc_info=True)


async def handle_help(message):
    """Обработчик команды /help"""
    try:
        help_text = (
            "📚 Доступные команды:\n\n"
            "🚀 Начало работы:\n"
            "/start - Начать работу с ботом\n"
            "/register - Зарегистрироваться\n\n"
            "📅 Календарь и мероприятия:\n"
            "/calendar - Календарь внеучебных событий\n"
            "/event <ID> - Информация о мероприятии\n"
            "/my_events - Мои мероприятия\n"
            "/subscribe <ID> - Подписаться на мероприятие\n"
            "/unsubscribe <ID> - Отписаться от мероприятия\n\n"
            "ℹ️ Помощь:\n"
            "/help - Список команд"
        )
        await message.reply(help_text)
    except Exception as e:
        logger.error(f"Ошибка в handle_help: {e}", exc_info=True)


