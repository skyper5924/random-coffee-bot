from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Количество участников")],
        [KeyboardButton(text="Отправить сообщение всем")],
        [KeyboardButton(text="Управление темами")],
        [KeyboardButton(text="Запустить подбор пар")],  # Остаётся только эта кнопка
        [KeyboardButton(text="Вернуться в главное меню")]
    ],
    resize_keyboard=True
)