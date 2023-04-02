# Homework_bot

Учебный проект 7 спринта.

# Описание работы бота

Это Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнает статус вашей домашней работы: взята ли ваша домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.

## Как запустить локально

 1. Клонировать репозиторий:

    ```python
    git clone https://github.com/Evkasonka/homework_bot
    ```

 2. Перейти в папку с проектом:

    ```python
    cd homework_bot/
    ```

 3. Установите виртуальное окружение 
    ```python
    python -m venv venv
    ```

 4. Активируйте виртуальное окружение 
    ```python
    # для OS Lunix и MacOS
    source venv/bin/activate
    # для OS Windows
    source venv/Scripts/activate
    ```

 5. Установите зависимости из файла requirements.txt 
    ```python
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
    ```
    
 6. Запустить проект локально:

    ```python
    # для OS Lunix и MacOS
    python homework_bot.py
    # для OS Windows
    python3 homework_bot.py
    ```


