from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📄 Моя анкета")],
        [KeyboardButton(text="📊 Мой статус")],
        [KeyboardButton(text="⚙️ Админ-меню")]  # Добавляем эмодзи
    ],
    resize_keyboard=True
)