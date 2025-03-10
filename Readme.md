# Random Coffee Bot

Telegram-бот для организации неформальных встреч. Бот автоматически подбирает пары пользователей раз в неделю и отправляет им анкеты друг друга.

---

## Основные функции

- **Регистрация пользователей**: Пользователи заполняют анкету (имя, возраст, город, информация о себе).
- **Подбор пар**: Каждый понедельник бот подбирает пары и отправляет уведомления.
- **Меню администратора**: Администратор может узнать количество участников и отправить сообщение всем пользователям.

---

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/skyper5924/random-coffee-bot.git
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
4. Создайте файл config.py в корне проекта и добавьте туда токен бота и ID администратора:
   ```bash
   TOKEN = "ВАШ_ТОКЕН_БОТА"     
   ADMIN_ID = 123456789  # Замените на ваш ID Telegram   

5.    ```bash
      python main.py

## Установка через Docker 

1. Убедитесь, что у вас установлены [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/).

2. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/ваш-логин/random-coffee-bot.git
   cd random-coffee-bot
3. Создайте файл .env в корне проекта и добавьте туда токен бота и ID администратора:
   ```bash
   TOKEN=ВАШ_ТОКЕН_БОТА
   ADMIN_ID=123456789
4. Соберите и запустите контейнер:
   ```bash
   docker-compose up -d
5. Проверьте логи, чтобы убедиться, что бот запустился:
   ```bash
   docker logs random_coffee_bot
6. Чтобы данные SQLite сохранялись после остановки контейнера, смонтируйте директорию с базой данных в контейнер:\
   ```bash
   docker run -d --name random-coffee-bot -v $(pwd)/data:/app/data random-coffee-bot