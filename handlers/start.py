from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart
from keyboards.main_menu import main_menu_keyboard
from states import Form
from utils.storage import load_users
from aiogram.types import ReplyKeyboardRemove


router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    username = message.from_user.username
    users = load_users()

    if str(user_id) in users:
        # Если анкета есть, показываем главное меню
        await message.answer(f"Добро пожаловать, {message.from_user.full_name}!", reply_markup=main_menu_keyboard)
    else:
        # Если анкеты нет, начинаем регистрацию
        await message.answer(f"Добро пожаловать, {message.from_user.full_name}! Давайте начнем регистрацию.", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.name)  # Переходим в состояние "name"
        await message.answer("Как вас зовут?")

