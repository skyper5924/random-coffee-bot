from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from utils.storage import load_users, save_user
from keyboards.main_menu import main_menu_keyboard

router = Router()

@router.message(F.text == "📊 Мой статус")
async def show_my_status(message: Message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id in users:
        current_status = users[user_id].get('status', 'active')
        status_text = "Активен" if current_status == 'active' else "Не активен"

        # Создаем клавиатуру для изменения статуса
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✅ Стать активным")],
                [KeyboardButton(text="❌ Стать неактивным")],
                [KeyboardButton(text="🔙 Вернуться в главное меню")]
            ],
            resize_keyboard=True
        )

        await message.answer(f"Ваш текущий статус: {status_text}.", reply_markup=keyboard)
    else:
        await message.answer("Вы еще не заполнили анкету.", reply_markup=main_menu_keyboard)

@router.message(F.text == "✅ Стать активным")
async def set_active_status(message: Message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id in users:
        users[user_id]['status'] = 'active'
        save_user(users)
        await message.answer("Ваш статус изменён на: Активен.", reply_markup=main_menu_keyboard)
    else:
        await message.answer("Вы еще не заполнили анкету.", reply_markup=main_menu_keyboard)

@router.message(F.text == "❌ Стать неактивным")
async def set_inactive_status(message: Message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id in users:
        users[user_id]['status'] = 'inactive'
        save_user(users)
        await message.answer("Ваш статус изменён на: Не активен.", reply_markup=main_menu_keyboard)
    else:
        await message.answer("Вы еще не заполнили анкету.", reply_markup=main_menu_keyboard)