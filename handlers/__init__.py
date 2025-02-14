from aiogram import Router
from .start import router as start_router
from .profile import router as profile_router
from .status import router as status_router
from .common import router as common_router
from .admin import router as admin_router  # Импортируем роутер администратора

router = Router()

# Подключение всех роутеров
router.include_router(start_router)
router.include_router(profile_router)
router.include_router(status_router)
router.include_router(common_router)
router.include_router(admin_router)  # Подключаем роутер администратора