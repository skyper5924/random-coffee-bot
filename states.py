from aiogram.fsm.state import StatesGroup, State

class Form(StatesGroup):
    name = State()  # Состояние для имени
    work_place = State()  # Состояние для места работы
    work_description = State()  # Состояние для описания работы
    hobbies = State()  # Состояние для хобби
#    topic = State()  # Состояние для выбора темы

class BroadcastState(StatesGroup):
    broadcast_message = State()  # Состояние для рассылки сообщений