from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

profile_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Изменить анкету")],
        [KeyboardButton(text="Вернуться в главное меню")]
    ],
    resize_keyboard=True
)