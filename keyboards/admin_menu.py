from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👥 Количество участников")],
        [KeyboardButton(text="📨 Отправить сообщение всем")],
        [KeyboardButton(text="📩 Запустить рассылку с выбором тем")],  # Новая кнопка
        [KeyboardButton(text="📝 Управление темами")],
        [KeyboardButton(text="🎯 Запустить подбор пар")],
        [KeyboardButton(text="🤝 Подбор пар ФУБ и пользователь")],
        [KeyboardButton(text="👀 Просмотреть все анкеты")],
        [KeyboardButton(text="🔙 Вернуться в главное меню")]
    ],
    resize_keyboard=True
)