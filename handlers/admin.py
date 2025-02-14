from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID
from keyboards.admin_menu import admin_menu_keyboard
from keyboards.main_menu import main_menu_keyboard
from utils.storage import load_users
from states import BroadcastState  # Импортируем новое состояние
import logging
import asyncio

router = Router()

# Проверка, является ли пользователь администратором
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
        await state.set_state(BroadcastState.broadcast_message)  # Используем новое состояние
        logging.info(f"Состояние установлено: BroadcastState.broadcast_message для пользователя {message.from_user.id}")
    else:
        await message.answer("У вас нет доступа к этой команде.", reply_markup=main_menu_keyboard)

@router.message(F.text, BroadcastState.broadcast_message)  # Используем новое состояние
async def process_broadcast_message(message: Message, state: FSMContext):
    logging.info(f"Обработка сообщения в состоянии BroadcastState.broadcast_message: {message.text}")
    users = load_users()
    success_count = 0
    fail_count = 0

    try:
        for user_id_str in users.keys():
            try:
                user_id = int(user_id_str)  # Преобразуем user_id в целое число
                await message.send_copy(chat_id=user_id)  # Отправляем копию сообщения
                success_count += 1
                await asyncio.sleep(0.1)  # Небольшая пауза между отправками
            except Exception as e:
                logging.error(f"Не удалось отправить сообщение пользователю {user_id_str}: {e}")
                fail_count += 1

        # Отправляем отчет администратору
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