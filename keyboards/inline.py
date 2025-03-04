from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_topic_keyboard(topics: list) -> InlineKeyboardMarkup:
    keyboard = []
    for topic in topics:
        # Убедись, что callback_data не содержит пробелов или спецсимволов
        callback_data = f"select_topic:{topic.replace(' ', '_')}"  # Заменяем пробелы на "_"
        keyboard.append([InlineKeyboardButton(text=topic, callback_data=callback_data)])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)