"""Скрипт для создания директории data и настройки прав доступа"""
import os
import json
import shutil

def setup_data_directory():
    """Создает директорию data и копирует database.json если нужно"""
    data_dir = "data"
    
    # Создаем директорию data, если её нет
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, mode=0o755, exist_ok=True)
        print(f"✅ Создана директория {data_dir}")
    else:
        print(f"✅ Директория {data_dir} уже существует")
    
    # Проверяем, есть ли database.json в корне
    root_db = "database.json"
    data_db = os.path.join(data_dir, "database.json")
    
    # Если database.json есть в корне, но нет в data - копируем
    if os.path.exists(root_db) and not os.path.exists(data_db):
        shutil.copy2(root_db, data_db)
        print(f"✅ Скопирован {root_db} в {data_db}")
    elif os.path.exists(data_db):
        print(f"✅ Файл {data_db} уже существует")
    else:
        # Создаем новый пустой database.json
        default_data = {
            "users": {},
            "events": []
        }
        with open(data_db, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Создан новый {data_db}")
    
    # Устанавливаем права доступа (на Unix-подобных системах)
    if os.name != 'nt':  # Не Windows
        try:
            os.chmod(data_dir, 0o755)
            if os.path.exists(data_db):
                os.chmod(data_db, 0o644)
            print("✅ Права доступа установлены")
        except Exception as e:
            print(f"⚠️ Не удалось установить права доступа: {e}")
    
    print("\n✅ Настройка директории data завершена!")

if __name__ == "__main__":
    setup_data_directory()

