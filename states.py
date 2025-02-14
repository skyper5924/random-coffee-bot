from aiogram.fsm.state import StatesGroup, State

class Form(StatesGroup):
    name = State()
    age = State()
    city = State()
    about_me = State()
    answer_yes = State()

class BroadcastState(StatesGroup):
    broadcast_message = State()  # Новое состояние для рассылки сообщений