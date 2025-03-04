import logging
import random
from typing import List, Tuple
from utils.storage import load_users
from config import ADMIN_ID

def match_users() -> List[Tuple[str, str]]:
    users = load_users()
    pairs = []

    # Группируем пользователей по выбранным темам
    topics_dict = {}
    for user_id, user_data in users.items():
        if user_data.get('status', 'active') == 'active':
            topic = user_data.get("topic")
            if topic:
                if topic not in topics_dict:
                    topics_dict[topic] = []
                topics_dict[topic].append(user_id)

    # Подбираем пары внутри каждой группы
    for topic, user_ids in topics_dict.items():
        random.shuffle(user_ids)
        for i in range(0, len(user_ids) - 1, 2):
            pairs.append((user_ids[i], user_ids[i + 1]))
            logging.info(f"Пара: {user_ids[i]} ↔ {user_ids[i + 1]} (тема: {topic})")

        # Если в группе нечётное количество пользователей, оставляем последнего без пары
        if len(user_ids) % 2 != 0:
            leftover_user = user_ids[-1]
            logging.info(f"Пользователь {leftover_user} остался без пары (тема: {topic})")

    return pairs

async def notify_users(bot, pairs: List[Tuple[str, str]]):
    """
    Отправляет уведомления пользователям об их парах и теме.
    Добавляет информацию о работе и хобби.
    """
    users = load_users()
    success_count = 0
    fail_count = 0

    # Отправляем уведомления пользователям с парами
    for user_id1, user_id2 in pairs:
        if user_id2 is not None:
            # Получаем данные пользователей
            user1 = users[user_id1]
            user2 = users[user_id2]

            # Формируем сообщение для user1
            await bot.send_message(
                chat_id=user_id1,
                text=(
                    f"🎉 Ваша пара на эту неделю: {user2['name']}!\n"
                    f"Тема: {user2.get('topic', 'без темы')}\n"
                    f"💼 Работа: {user2.get('work_place', 'не указано')}\n"
                    f"📝 Описание работы: {user2.get('work_description', 'не указано')}\n"
                    f"🎯 Хобби: {user2.get('hobbies', 'не указано')}\n"
                    f"Напишите своему партнеру: @{user2.get('username', 'username_не_указан')}\n"
                    f"Договоритесь о встрече!"
                )
            )
            logging.info(f"Сообщение отправлено пользователю {user_id1}")

            # Формируем сообщение для user2
            await bot.send_message(
                chat_id=user_id2,
                text=(
                    f"🎉 Ваша пара на эту неделю: {user1['name']}!\n"
                    f"Тема: {user1.get('topic', 'без темы')}\n"
                    f"💼 Работа: {user1.get('work_place', 'не указано')}\n"
                    f"📝 Описание работы: {user1.get('work_description', 'не указано')}\n"
                    f"🎯 Хобби: {user1.get('hobbies', 'не указано')}\n"
                    f"Напишите своему партнеру: @{user1.get('username', 'username_не_указан')}\n"
                    f"Договоритесь о встрече!"
                )
            )
            logging.info(f"Сообщение отправлено пользователю {user_id2}")

            success_count += 1

    # Отправляем уведомления пользователям без пары
    all_users = set(users.keys())
    paired_users = set()

    for user_id1, user_id2 in pairs:
        paired_users.add(user_id1)
        if user_id2 is not None:
            paired_users.add(user_id2)

    leftover_users = all_users - paired_users

    for user_id in leftover_users:
        await bot.send_message(
            chat_id=user_id,
            text="😔 К сожалению, на этой неделе мы не смогли найти вам пару. Попробуем в следующий раз!"
        )
        logging.info(f"Пользователь {user_id} остался без пары")
        fail_count += 1

    # Отправляем отчет администратору
    if ADMIN_ID:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Подбор пар завершён:\nУспешно: {success_count}\nНе удалось: {fail_count}"
        )
        logging.info(f"Отчёт отправлен администратору {ADMIN_ID}")