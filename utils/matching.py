import random
from typing import Dict, List, Tuple
from utils.storage import load_users

def match_users() -> List[Tuple[str, str]]:
    """
    Подбирает пары пользователей.
    Возвращает список кортежей (user_id1, user_id2).
    """
    users = load_users()
    user_ids = list(users.keys())

    # Перемешиваем список пользователей
    random.shuffle(user_ids)

    # Создаем пары
    pairs = []
    for i in range(0, len(user_ids) - 1, 2):
        pairs.append((user_ids[i], user_ids[i + 1]))

    # Если количество пользователей нечетное, последний пользователь остается без пары
    if len(user_ids) % 2 != 0:
        pairs.append((user_ids[-1], None))

    return pairs

async def notify_users(bot, pairs: List[Tuple[str, str]]):
    """
    Отправляет уведомления пользователям о их парах и анкету напарника.
    """
    users = load_users()

    for user_id1, user_id2 in pairs:
        if user_id2 is not None:
            # Получаем данные пользователей
            user1 = users[user_id1]
            user2 = users[user_id2]

            # Формируем анкету для user1
            user2_profile = (
                f"📄 Анкета вашего напарника:\n"
                f"Имя: {user2['name']}\n"
                f"Возраст: {user2['age']}\n"
                f"Город: {user2['city']}\n"
                f"О себе: {user2['bio']}\n"
                f"Связь: @{user2.get('username', 'username_не_указан')}"
            )

            # Формируем анкету для user2
            user1_profile = (
                f"📄 Анкета вашего напарника:\n"
                f"Имя: {user1['name']}\n"
                f"Возраст: {user1['age']}\n"
                f"Город: {user1['city']}\n"
                f"О себе: {user1['bio']}\n"
                f"Связь: @{user1.get('username', 'username_не_указан')}"
            )

            # Отправляем сообщение первому пользователю
            await bot.send_message(
                chat_id=user_id1,
                text=f"🎉 Ваша пара на эту неделю: {user2['name']}!\n"
                     f"Напишите своему партнеру: @{user2.get('username', 'username_не_указан')}\n"
                     f"Договоритесь о встрече!"
            )
            await bot.send_message(chat_id=user_id1, text=user2_profile)  # Отправляем анкету

            # Отправляем сообщение второму пользователю
            await bot.send_message(
                chat_id=user_id2,
                text=f"🎉 Ваша пара на эту неделю: {user1['name']}!\n"
                     f"Напишите своему партнеру: @{user1.get('username', 'username_не_указан')}\n"
                     f"Договоритесь о встрече!"
            )
            await bot.send_message(chat_id=user_id2, text=user1_profile)  # Отправляем анкету
        else:
            # Если пользователь остался без пары
            await bot.send_message(
                chat_id=user_id1,
                text="😔 К сожалению, на этой неделе мы не смогли найти вам пару. Попробуем в следующий раз!"
            )