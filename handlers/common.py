from aiogram import Router, F
from aiogram.types import Message
from keyboards.main_menu import main_menu_keyboard

router = Router()

@router.message(F.text == "Вернуться в главное меню")
async def back_to_main_menu(message: Message):
    await message.answer("Главное меню:", reply_markup=main_menu_keyboard)