"""Скрипт для добавления тестовых мероприятий в базу данных"""
from database import Database
from datetime import datetime, timedelta

db = Database()

# Добавляем несколько тестовых мероприятий
events = [
    {
        'title': 'Хакатон MAX 2024',
        'description': 'Ежегодный хакатон для разработчиков. Примите участие в создании инновационных решений!',
        'date': (datetime.now() + timedelta(days=1)).isoformat(),
        'organizer': 'Организационный комитет MAX'
    },
    {
        'title': 'Лекция по Python',
        'description': 'Введение в программирование на Python. Подходит для начинающих.',
        'date': (datetime.now() + timedelta(hours=2)).isoformat(),
        'organizer': 'Кафедра информатики'
    },
    {
        'title': 'Спортивное мероприятие - Турнир по волейболу',
        'description': 'Турнир по волейболу среди студентов. Регистрация обязательна.',
        'date': (datetime.now() + timedelta(days=7)).isoformat(),
        'organizer': 'Спортивный клуб'
    },
    {
        'title': 'Мастер-класс по дизайну',
        'description': 'Узнайте основы графического дизайна и создайте свой первый проект.',
        'date': (datetime.now() + timedelta(days=3)).isoformat(),
        'organizer': 'Факультет дизайна'
    },
    {
        'title': 'Встреча с выпускниками',
        'description': 'Неформальная встреча с успешными выпускниками. Обмен опытом и советами.',
        'date': (datetime.now() + timedelta(days=5)).isoformat(),
        'organizer': 'Ассоциация выпускников'
    }
]

print("Добавление тестовых мероприятий...")
for event in events:
    event_id = db.add_event(
        title=event['title'],
        description=event['description'],
        date=event['date'],
        organizer=event['organizer']
    )
    print(f"✅ Добавлено мероприятие: {event['title']} (ID: {event_id})")

print(f"\n✅ Всего мероприятий в базе: {len(db.get_events())}")
print("\nТеперь вы можете:")
print("1. Запустить бота: python bot.py")
print("2. Зарегистрироваться: /register")
print("3. Посмотреть календарь: /calendar")
print("4. Подписаться на мероприятие: /subscribe <ID>")

