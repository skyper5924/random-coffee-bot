from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from keyboards.main_menu import main_menu_keyboard
from keyboards.profile_menu import profile_menu_keyboard
from utils.storage import load_users, save_user, load_topics, save_user_topic  # Добавили save_user_topic
from states import Form
import logging
from aiogram.fsm.context import FSMContext  # Добавляем импорт


# Определяем router
router = Router()

# Обработчик для состояния "name"
@router.message(Form.name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)  # Сохраняем имя
    await state.set_state(Form.work_place)  # Переходим к вопросу о месте работы
    await message.answer("Где и кем ты работаешь?")

# Обработчик для состояния "work_place"
@router.message(Form.work_place)
async def process_work_place(message: Message, state: FSMContext) -> None:
    await state.update_data(work_place=message.text)  # Сохраняем место работы
    await state.set_state(Form.work_description)  # Переходим к вопросу о работе
    await message.answer("Чем занимаешься по работе?")

# Обработчик для состояния "work_description"
@router.message(Form.work_description)
async def process_work_description(message: Message, state: FSMContext) -> None:
    await state.update_data(work_description=message.text)  # Сохраняем описание работы
    await state.set_state(Form.hobbies)  # Переходим к вопросу о хобби
    await message.answer("Чем увлекаешься в свободное время?")

# Обработчик для состояния "hobbies"
@router.message(Form.hobbies)
async def process_hobbies(message: Message, state: FSMContext):
    await state.update_data(hobbies=message.text)  # Сохраняем хобби

    # Получаем данные из состояния
    data = await state.get_data()

    # Сохраняем данные пользователя
    user_id = message.from_user.id
    user_data = {
        'name': data['name'],
        'work_place': data['work_place'],
        'work_description': data['work_description'],
        'hobbies': data['hobbies'],
        'topic': '',  # Тема пока пустая
        'username': message.from_user.username,
        'status': 'active'
    }
    save_user(str(user_id), user_data)

    await message.answer("Спасибо! Анкета заполнена.", reply_markup=main_menu_keyboard)
    await state.clear()  # Очищаем состояние


# Обработчик для команды "Моя анкета"
@router.message(F.text == "📄 Моя анкета")
async def show_my_profile(message: Message, state: FSMContext):  # Добавляем state
    user_id = message.from_user.id
    users = load_users()

    if str(user_id) in users:
        user_data = users[str(user_id)]
        profile_text = (
            f"Ваша анкета:\n"
            f"Имя: {user_data['name']}\n"
            f"Место работы: {user_data['work_place']}\n"
            f"Чем занимаешься: {user_data['work_description']}\n"
            f"Хобби: {user_data['hobbies']}\n"
        )
        # Добавляем тему, если она есть
        if user_data.get('topic'):
            profile_text += f"Тема: {user_data['topic']}\n"

        await message.answer(profile_text, reply_markup=profile_menu_keyboard)
    else:
        await message.answer("Вы еще не заполнили анкету. Давайте начнем регистрацию!",
                             reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.name)  # Теперь state доступен
        await message.answer("Как вас зовут?")



# Обработчик для команды "Изменить анкету"
@router.message(F.text == "✏️ Изменить анкету")
async def edit_profile(message: Message, state: FSMContext):
    user_id = message.from_user.id
    users = load_users()

    if str(user_id) in users:
        user_data = users[str(user_id)]
        await state.update_data(
            name=user_data['name'],
            work_place=user_data['work_place'],
            work_description=user_data['work_description'],
            hobbies=user_data['hobbies']
        )
        await message.answer("Давайте изменим вашу анкету. Как вас зовут?", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.name)  # Переходим в состояние "name"
    else:
        await message.answer("У вас еще нет анкеты. Давайте начнем регистрацию!", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.name)
        await message.answer("Как вас зовут?")

# Обработчик для выбора темы через инлайн-клавиатуру
@router.callback_query(F.data.startswith("select_topic:"))
async def process_topic_selection(callback: CallbackQuery, state: FSMContext):
    topic = callback.data.split(":")[1]
    user_id = str(callback.from_user.id)
    users = load_users()

    if user_id in users:
        # Обновляем тему в профиле пользователя
        user_data = users[user_id]
        user_data['topic'] = topic  # Обновляем тему
        save_user(user_id, user_data)  # Сохраняем обновленные данные

        # Сохраняем выбор темы в историю
        save_user_topic(user_id, topic)

        # Редактируем сообщение, чтобы скрыть кнопки и изменить текст
        await callback.message.edit_text(
            f"Вы выбрали тему: {topic}.",
            reply_markup=None  # Убираем инлайн-кнопки
        )
        await callback.answer()
    else:
        await callback.message.answer("Вы еще не заполнили анкету.")
        await callback.answer()