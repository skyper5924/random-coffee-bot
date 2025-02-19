import logging
from aiogram import Bot
from utils.matching import match_users, notify_users

async def weekly_matching(bot: Bot):
    """
    Задача для подбора пар и отправки уведомлений.
    """
    logging.info("Запуск подбора пар...")
    pairs = match_users()
    await notify_users(bot, pairs)
    logging.info("Подбор пар завершён.")