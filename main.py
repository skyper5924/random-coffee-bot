from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.triggers.cron import CronTrigger

from config import TOKEN
from handlers import router
from utils.matching import match_users, notify_users
from utils.matching_tasks import weekly_matching
from pytz import timezone


# Настройка логирования
import logging

from utils.storage import load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
config = load_config()

# Установка часового пояса Москвы
moscow_tz = timezone("Europe/Moscow")  # Укажи свой часовой пояс

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключение роутеров
dp.include_router(router)

# Планировщик задач
scheduler = AsyncIOScheduler()

async def weekly_matching(bot):
    """
    Задача для подбора пар и отправки уведомлений.
    """
    logging.info("Запуск подбора пар...")
    pairs = match_users()
    await notify_users(bot, pairs)
    logging.info("Подбор пар завершён.")


async def main():
    # Запуск планировщика
    scheduler.add_job(
        weekly_matching,
        CronTrigger(
            day_of_week=config["matching_day"],
            hour=int(config["matching_time"].split(":")[0]),
            minute=int(config["matching_time"].split(":")[1]),
            timezone=moscow_tz
        ),
        args=[bot]  # Передаём bot в функцию
    )
    scheduler.start()

    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())