"""Скрипт для добавления тестовых мероприятий"""
from database import Database
from datetime import datetime, timedelta

db = Database()

# Добавляем несколько тестовых мероприятий
events = [
    {
        'title': 'Хакатон MAX 2024',
        'description': 'Ежегодный хакатон для разработчиков',
        'date': (datetime.now() + timedelta(days=1)).isoformat(),
        'organizer': 'Организационный комитет'
    },
    {
        'title': 'Лекция по Python',
        'description': 'Введение в программирование на Python',
        'date': (datetime.now() + timedelta(hours=2)).isoformat(),
        'organizer': 'Кафедра информатики'
    },
    {
        'title': 'Спортивное мероприятие',
        'description': 'Турнир по волейболу',
        'date': (datetime.now() + timedelta(days=7)).isoformat(),
        'organizer': 'Спортивный клуб'
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

print(f"\nВсего мероприятий: {len(db.get_events())}")

