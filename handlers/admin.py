from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID
from keyboards.admin_menu import admin_menu_keyboard
from keyboards.main_menu import main_menu_keyboard
from utils.storage import load_users, save_topics, load_topics
from states import BroadcastState
from aiogram.fsm.state import State, StatesGroup
import logging
import asyncio

class AdminStates(StatesGroup):
    add_topic = State()
    delete_topic = State()

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

@router.message(F.text == "Админ-меню")
async def admin_menu(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("Добро пожаловать в админ-меню!", reply_markup=admin_menu_keyboard)
    else:
        await message.answer("У вас нет доступа к этому меню.", reply_markup=main_menu_keyboard)

@router.message(F.text == "Количество участников")
async def show_participants_count(message: Message):
    if is_admin(message.from_user.id):
        users = load_users()
        count = len(users)
        await message.answer(f"Количество участников: {count}", reply_markup=admin_menu_keyboard)
    else:
        await message.answer("У вас нет доступа к этой команде.", reply_markup=main_menu_keyboard)

@router.message(F.text == "Отправить сообщение всем")
async def broadcast_message(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("Введите сообщение для рассылки:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(BroadcastState.broadcast_message)
        logging.info(f"Состояние установлено: BroadcastState.broadcast_message для пользователя {message.from_user.id}")
    else:
        await message.answer("У вас нет доступа к этой команде.", reply_markup=main_menu_keyboard)

@router.message(F.text, BroadcastState.broadcast_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    logging.info(f"Обработка сообщения в состоянии BroadcastState.broadcast_message: {message.text}")
    users = load_users()
    success_count = 0
    fail_count = 0

    try:
        for user_id_str in users.keys():
            try:
                user_id = int(user_id_str)
                await message.send_copy(chat_id=user_id)
                success_count += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                logging.error(f"Не удалось отправить сообщение пользователю {user_id_str}: {e}")
                fail_count += 1

        await message.answer(
            f"Сообщение отправлено:\n"
            f"Успешно: {success_count}\n"
            f"Не удалось: {fail_count}",
            reply_markup=admin_menu_keyboard
        )
    except Exception as e:
        logging.error(f"Ошибка при рассылке сообщений: {e}")
        await message.answer("Произошла ошибка при рассылке сообщений.", reply_markup=admin_menu_keyboard)
    finally:
        await state.clear()
        logging.info(f"Состояние очищено для пользователя {message.from_user.id}")

@router.message(F.text == "Управление темами")
async def manage_topics(message: Message):
    if is_admin(message.from_user.id):
        topics = load_topics()
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Добавить тему")],
                [KeyboardButton(text="Удалить тему")] if topics else [],
                [KeyboardButton(text="Вернуться в админ-меню")]
            ],
            resize_keyboard=True
        )

        if topics:
            await message.answer(
                "Текущие темы:\n" + "\n".join(topics),
                reply_markup=keyboard
            )
        else:
            await message.answer("Темы не найдены. Вы можете добавить новую тему.", reply_markup=keyboard)
    else:
        await message.answer("У вас нет доступа к этой команде.", reply_markup=main_menu_keyboard)

@router.message(F.text == "Добавить тему")
async def add_topic(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("Введите новую тему:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(AdminStates.add_topic)
    else:
        await message.answer("У вас нет доступа к этой команде.", reply_markup=main_menu_keyboard)

@router.message(AdminStates.add_topic)
async def process_add_topic(message: Message, state: FSMContext):
    topics = load_topics()
    new_topic = message.text

    if new_topic not in topics:
        topics.append(new_topic)
        save_topics(topics)
        await message.answer(f"Тема '{new_topic}' добавлена.", reply_markup=admin_menu_keyboard)
    else:
        await message.answer("Такая тема уже существует.", reply_markup=admin_menu_keyboard)

    await state.clear()

@router.message(F.text == "Удалить тему")
async def delete_topic(message: Message, state: FSMContext):
    logging.info(f"Пользователь {message.from_user.id} начал удаление темы.")
    if is_admin(message.from_user.id):
        topics = load_topics()
        if topics:
            keyboard = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=topic)] for topic in topics],
                resize_keyboard=True
            )
            await message.answer("Выберите тему для удаления:", reply_markup=keyboard)
            await state.set_state(AdminStates.delete_topic)
        else:
            await message.answer("Темы не найдены.", reply_markup=admin_menu_keyboard)
    else:
        await message.answer("У вас нет доступа к этой команде.", reply_markup=main_menu_keyboard)

@router.message(F.text, AdminStates.delete_topic)
async def process_delete_topic(message: Message, state: FSMContext):
    logging.info(f"Пользователь {message.from_user.id} выбрал тему для удаления: {message.text}")
    topics = load_topics()
    topic_to_delete = message.text

    if topic_to_delete in topics:
        topics.remove(topic_to_delete)
        save_topics(topics)
        await message.answer(f"Тема '{topic_to_delete}' удалена.", reply_markup=admin_menu_keyboard)
    else:
        await message.answer("Тема не найдена.", reply_markup=admin_menu_keyboard)

    await state.clear()
