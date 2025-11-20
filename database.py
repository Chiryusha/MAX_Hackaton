"""Модуль для работы с базой данных пользователей и мероприятий"""
import json
import os
import shutil
from datetime import datetime
from typing import Optional, List, Dict

# Используем переменные окружения Railway
DB_DIR = os.environ.get('DATABASE_DIR', '/data')
DB_FILE = os.environ.get('DATABASE_FILE', os.path.join(DB_DIR, 'database.json'))

class Database:
    """Класс для работы с базой данных (JSON файл)"""
    
    def __init__(self):
        self.db_file = DB_FILE
        self.db_dir = DB_DIR
        print(f"📁 Используется база данных: {self.db_file}")
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Создает файл базы данных, если его нет"""
        try:
            os.makedirs(self.db_dir, exist_ok=True, mode=0o755)
            print(f"✅ Директория {self.db_dir} готова")
        except Exception as e:
            print(f"⚠️ Не удалось создать директорию {self.db_dir}: {e}")
        
        # Если файла БД нет, но есть database.json в корне - копируем
        if not os.path.exists(self.db_file) and os.path.exists('database.json'):
            print("🔄 Копируем database.json из корня...")
            shutil.copy2('database.json', self.db_file)
            print(f"✅ database.json скопирован в {self.db_file}")
        
        if not os.path.exists(self.db_file):
            try:
                self._save_db({
                    'users': {},
                    'events': []
                })
                print(f"✅ Создана новая база данных: {self.db_file}")
            except Exception as e:
                print(f"❌ Ошибка создания БД: {e}")
        else:
            print(f"✅ База данных уже существует: {self.db_file}")
            
            # Логируем что в БД
            db = self._load_db()
            events_count = len(db.get('events', []))
            users_count = len(db.get('users', {}))
            print(f"📊 В БД: {events_count} мероприятий, {users_count} пользователей")
    
    def _load_db(self) -> dict:
        """Загружает данные из файла"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ База данных загружена из {self.db_file}")
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ Ошибка загрузки БД, создаем новую: {e}")
            return {'users': {}, 'events': []}
    
    def _save_db(self, data: dict):
        """Сохраняет данные в файл"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ База данных сохранена в {self.db_file}")
        except Exception as e:
            print(f"❌ Ошибка сохранения БД: {e}")
    
    # остальные методы остаются без изменений...
    
    # Работа с пользователями
    def register_user(self, user_id: str, username: str = None, full_name: str = None) -> bool:
        """Регистрирует нового пользователя"""
        db = self._load_db()
        if user_id not in db['users']:
            db['users'][user_id] = {
                'username': username,
                'full_name': full_name,
                'registered_at': datetime.now().isoformat(),
                'subscribed_events': [],
                'notifications_enabled': True
            }
            self._save_db(db)
            return True
        return False
    
    def get_user(self, user_id: str) -> Optional[dict]:
        """Получает информацию о пользователе"""
        db = self._load_db()
        return db['users'].get(user_id)
    
    def is_user_registered(self, user_id: str) -> bool:
        """Проверяет, зарегистрирован ли пользователь"""
        return self.get_user(user_id) is not None
    
    def update_user(self, user_id: str, **kwargs):
        """Обновляет данные пользователя"""
        db = self._load_db()
        if user_id in db['users']:
            db['users'][user_id].update(kwargs)
            self._save_db(db)
    
    # Работа с мероприятиями
    def add_event(self, title: str, description: str, date: str, organizer: str = None) -> int:
        """Добавляет новое мероприятие"""
        db = self._load_db()
        event_id = len(db['events'])
        event = {
            'id': event_id,
            'title': title,
            'description': description,
            'date': date,
            'organizer': organizer,
            'created_at': datetime.now().isoformat(),
            'subscribers': []
        }
        db['events'].append(event)
        self._save_db(db)
        return event_id
    
    def get_events(self) -> List[dict]:
        """Получает все мероприятия"""
        db = self._load_db()
        return db['events']
    
    def get_event(self, event_id: int) -> Optional[dict]:
        """Получает мероприятие по ID"""
        db = self._load_db()
        if 0 <= event_id < len(db['events']):
            return db['events'][event_id]
        return None
    
    def subscribe_to_event(self, user_id: str, event_id: int) -> bool:
        """Подписывает пользователя на мероприятие"""
        db = self._load_db()
        if 0 <= event_id < len(db['events']):
            event = db['events'][event_id]
            if user_id not in event['subscribers']:
                event['subscribers'].append(user_id)
            if user_id in db['users']:
                if event_id not in db['users'][user_id]['subscribed_events']:
                    db['users'][user_id]['subscribed_events'].append(event_id)
            self._save_db(db)
            return True
        return False
    
    def unsubscribe_from_event(self, user_id: str, event_id: int) -> bool:
        """Отписывает пользователя от мероприятия"""
        db = self._load_db()
        if 0 <= event_id < len(db['events']):
            event = db['events'][event_id]
            if user_id in event['subscribers']:
                event['subscribers'].remove(user_id)
            if user_id in db['users']:
                if event_id in db['users'][user_id]['subscribed_events']:
                    db['users'][user_id]['subscribed_events'].remove(event_id)
            self._save_db(db)
            return True
        return False
    
    def get_user_events(self, user_id: str) -> List[dict]:
        """Получает мероприятия, на которые подписан пользователь"""
        db = self._load_db()
        user = db['users'].get(user_id)
        if not user:
            return []
        
        events = []
        for event_id in user.get('subscribed_events', []):
            event = self.get_event(event_id)
            if event:
                events.append(event)
        return events



