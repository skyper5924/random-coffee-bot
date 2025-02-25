from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from keyboards.main_menu import main_menu_keyboard
from keyboards.profile_menu import profile_menu_keyboard
from utils.storage import load_users, save_user, load_topics
from states import Form
import re
from datetime import datetime

router = Router()

# Обработчик для состояния "name"
@router.message(Form.name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Form.age)
    await message.answer("Укажите дату рождения в формате ДД.ММ.ГГГГ")

# Обработчик для состояния "age"
@router.message(Form.age)
async def process_age(message: Message, state: FSMContext) -> None:
    date_format = re.compile(r'^\d{2}\.\d{2}\.\d{4}$')
    if not date_format.match(message.text):
        await message.answer("Неверный формат даты. Пожалуйста, укажите дату в формате ДД.ММ.ГГГГ.")
        return

    try:
        birth_date = datetime.strptime(message.text, '%d.%m.%Y')
    except ValueError:
        await message.answer("Неверная дата. Пожалуйста, укажите корректную дату в формате ДД.ММ.ГГГГ.")
        return

    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    if age < 1 or age > 100:
        await message.answer("Возраст должен быть в диапазоне от 1 до 100 лет.")
        return

    await state.update_data(age=str(age))
    await state.set_state(Form.city)
    await message.answer("Из какого вы города?")

# Обработчик для состояния "city"
@router.message(Form.city)
async def process_city(message: Message, state: FSMContext) -> None:
    await state.update_data(city=message.text)
    await state.set_state(Form.about_me)
    await message.answer("Расскажите немного о себе.")

# Обработчик для состояния "about_me"
@router.message(Form.about_me)
async def process_about_me(message: Message, state: FSMContext):
    await state.update_data(about_me=message.text)
    topics = load_topics()

    if topics:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=topic)] for topic in topics],
            resize_keyboard=True
        )
        await message.answer("Какая тема тебе ближе всего?", reply_markup=keyboard)
        await state.set_state(Form.topic)
    else:
        await message.answer("Темы не найдены. Пожалуйста, свяжитесь с администратором.", reply_markup=main_menu_keyboard)
        await state.clear()

# Обработчик для состояния "topic"
@router.message(Form.topic)
async def process_topic(message: Message, state: FSMContext):
    topics = load_topics()
    selected_topic = message.text

    if selected_topic in topics:
        await state.update_data(topic=selected_topic)
        data = await state.get_data()

        # Сохраняем данные пользователя
        user_id = message.from_user.id
        user_data = {
            'name': data['name'],
            'age': data['age'],
            'city': data['city'],
            'bio': data['about_me'],
            'topic': selected_topic,
            'username': message.from_user.username,
            'status': 'active'
        }
        save_user(str(user_id), user_data)

        await message.answer("Спасибо! Анкета заполнена.", reply_markup=main_menu_keyboard)
        await state.clear()
    else:
        await message.answer("Пожалуйста, выберите тему из списка.")

# Обработчик для команды "Моя анкета"
@router.message(F.text == "📄 Моя анкета")
async def show_my_profile(message: Message, state: FSMContext):
    user_id = message.from_user.id
    users = load_users()

    if str(user_id) in users:
        user_data = users[str(user_id)]
        profile_text = (
            f"Ваша анкета:\n"
            f"Имя: {user_data['name']}\n"
            f"Возраст: {user_data['age']}\n"
            f"Город: {user_data['city']}\n"
            f"О себе: {user_data['bio']}\n"
            f"Тема: {user_data.get('topic', 'не выбрана')}"
        )
        await message.answer(profile_text, reply_markup=profile_menu_keyboard)
    else:
        await message.answer("Вы еще не заполнили анкету. Давайте начнем регистрацию!", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.name)
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
            age=user_data['age'],
            city=user_data['city'],
            about_me=user_data['bio']
        )
        await message.answer("Давайте изменим вашу анкету. Как вас зовут?", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.name)
    else:
        await message.answer("У вас еще нет анкеты. Давайте начнем регистрацию!", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.name)
        await message.answer("Как вас зовут?")