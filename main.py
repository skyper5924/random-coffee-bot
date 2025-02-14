from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from handlers import router
from utils.matching import match_users, notify_users
from pytz import timezone


# Настройка логирования
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

local_tz = timezone("Europe/Moscow")  # Укажи свой часовой пояс

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключение роутеров
dp.include_router(router)

# Планировщик задач
scheduler = AsyncIOScheduler()

async def weekly_matching():
    """
    Задача для подбора пар и отправки уведомлений.
    """
    pairs = match_users()
    await notify_users(bot, pairs)

async def main():
    # Запуск планировщика
    #scheduler.add_job(weekly_matching, 'cron', day_of_week='mon', hour=10, minute=0)  # Каждый понедельник в 10:00
    scheduler.add_job(weekly_matching, 'cron', day_of_week='wed', hour=21, minute=35, timezone=local_tz)
    scheduler.start()

    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())