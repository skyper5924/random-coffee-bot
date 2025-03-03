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
        user_data = users[user_id]  # Получаем данные конкретного пользователя
        user_data['status'] = 'active'  # Меняем статус на активный
        save_user(user_id, user_data)  # Передаём user_id и user_data
        await message.answer("Ваш статус изменён на: Активен.", reply_markup=main_menu_keyboard)
    else:
        await message.answer("Вы еще не заполнили анкету.", reply_markup=main_menu_keyboard)

@router.message(F.text == "❌ Стать неактивным")
async def set_inactive_status(message: Message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id in users:
        user_data = users[user_id]  # Получаем данные конкретного пользователя
        user_data['status'] = 'inactive'  # Меняем статус на неактивный
        save_user(user_id, user_data)  # Передаём user_id и user_data
        await message.answer("Ваш статус изменён на: Не активен.", reply_markup=main_menu_keyboard)
    else:
        await message.answer("Вы еще не заполнили анкету.", reply_markup=main_menu_keyboard)