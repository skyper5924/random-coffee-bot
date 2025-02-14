from aiogram import Router, F
from aiogram.types import Message
from keyboards.main_menu import main_menu_keyboard

router = Router()

@router.message(F.text == "Мой статус")
async def show_my_status(message: Message):
    await message.answer("Ваш статус: активен.", reply_markup=main_menu_keyboard)