from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_topic_keyboard(topics: list) -> InlineKeyboardMarkup:
    keyboard = []
    for topic in topics:
        keyboard.append([InlineKeyboardButton(text=topic, callback_data=f"select_topic:{topic}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)