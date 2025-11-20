@echo off
echo Создание виртуального окружения...
python -m venv myenv

echo Активация виртуального окружения...
call myenv\Scripts\activate.bat

echo Установка библиотеки aiomax...
pip install -r requirements.txt

echo.
echo Установка завершена!
echo Для запуска бота выполните:
echo   myenv\Scripts\activate
echo   python bot.py

