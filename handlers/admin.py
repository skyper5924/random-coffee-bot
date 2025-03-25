import random
from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID
from keyboards.admin_menu import admin_menu_keyboard
from keyboards.main_menu import main_menu_keyboard
from utils.matching_tasks import weekly_matching
from utils.storage import load_users, save_topic, load_topics, delete_topic
from states import BroadcastState
from aiogram.fsm.state import State, StatesGroup
import logging
import asyncio
from keyboards.inline import create_topic_keyboard

class AdminStates(StatesGroup):
    add_topic = State()
    delete_topic = State()
    set_matching_day = State()
    set_matching_time = State()
    confirm_topic_selection = State()  # Новое состояние для подтверждения рассылки


router = Router()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

@router.message(F.text == "⚙️ Админ-меню")
async def admin_menu(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("Добро пожаловать в админ-меню!", reply_markup=admin_menu_keyboard)
    else:
        await message.answer("У вас нет доступа к этому меню.", reply_markup=main_menu_keyboard)

@router.message(F.text == "👥 Количество участников")
async def show_participants_count(message: Message):
    if is_admin(message.from_user.id):
        users = load_users()
        topics = load_topics()

        # Общее количество участников
        total_users = len(users)

        # Количество активных и неактивных участников
        active_users = sum(1 for user in users.values() if user.get('status') == 'active')
        inactive_users = total_users - active_users

        # Количество участников по темам
        topics_count = {topic: 0 for topic in topics}
        users_without_topic = 0

        for user in users.values():
            if user.get('topic'):
                topics_count[user['topic']] += 1
            else:
                users_without_topic += 1

        # Формируем текст статистики
        stats_text = (
            f"📊 Статистика участников:\n"
            f"👤 Всего участников: {total_users}\n"
            f"✅ Активных: {active_users}\n"
            f"❌ Неактивных: {inactive_users}\n"
            f"🏷️ Участников по темам:\n"
        )

        # Добавляем статистику по темам
        for topic, count in topics_count.items():
            stats_text += f"  - {topic}: {count}\n"

        # Добавляем участников без темы
        stats_text += f"🚫 Без темы: {users_without_topic}\n"

        await message.answer(stats_text, reply_markup=admin_menu_keyboard)
    else:
        await message.answer("У вас нет доступа к этой команде.", reply_markup=main_menu_keyboard)

@router.message(F.text == "📨 Отправить сообщение всем")
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

@router.message(F.text == "📝 Управление темами")
async def manage_topics(message: Message):
    if is_admin(message.from_user.id):
        topics = load_topics()
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="➕ Добавить тему")],
                [KeyboardButton(text="➖ Удалить тему")],
                [KeyboardButton(text="🔙 Вернуться в главное меню")]
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

@router.message(F.text == "➕ Добавить тему")
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
        save_topic(new_topic)
        await message.answer(f"Тема '{new_topic}' добавлена.", reply_markup=admin_menu_keyboard)
    else:
        await message.answer("Такая тема уже существует.", reply_markup=admin_menu_keyboard)

    await state.clear()

@router.message(F.text == "➖ Удалить тему")
async def delete_topic_handler(message: Message, state: FSMContext):
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
        delete_topic(topic_to_delete)
        await message.answer(f"Тема '{topic_to_delete}' удалена.", reply_markup=admin_menu_keyboard)
    else:
        await message.answer("Тема не найдена.", reply_markup=admin_menu_keyboard)

    await state.clear()

@router.message(F.text == "👀 Просмотреть все анкеты")
async def view_all_profiles(message: Message):
    if is_admin(message.from_user.id):
        users = load_users()

        if not users:
            await message.answer("Анкет пока нет.", reply_markup=admin_menu_keyboard)
            return

        # Разбиваем анкеты на части по 5 штук
        users_list = list(users.items())
        chunk_size = 5
        chunks = [users_list[i:i + chunk_size] for i in range(0, len(users_list), chunk_size)]

        for chunk in chunks:
            profiles_text = "Список анкет:\n\n"
            for user_id, user_data in chunk:
                profile_text = (
                    f"👤 Имя: {user_data['name']}\n"
                    f"💼 Работа: {user_data['work_place']}\n"
                    f"📝 Описание работы: {user_data['work_description']}\n"
                    f"🎯 Хобби: {user_data['hobbies']}\n"
                    f"🏷️ Тема: {user_data.get('topic', 'не выбрана')}\n"
                    f"🔗 Username: @{user_data.get('username', 'не указан')}\n"
                    f"📊 Статус: {'Активен' if user_data.get('status', 'active') == 'active' else 'Не активен'}\n"
                    f"---\n"
                )
                profiles_text += profile_text

            # Отправляем часть анкет
            await message.answer(profiles_text, reply_markup=admin_menu_keyboard)

    else:
        await message.answer("У вас нет доступа к этой команде.", reply_markup=main_menu_keyboard)

@router.message(F.text == "🎯 Запустить подбор пар")
async def manual_matching(message: Message, bot: Bot):
    if is_admin(message.from_user.id):
        await message.answer("Запуск подбора пар...", reply_markup=ReplyKeyboardRemove())
        pairs = await weekly_matching(bot)
        await message.answer(
            f"Подбор пар завершён. Найдено пар: {len(pairs)}.",
            reply_markup=admin_menu_keyboard
        )
    else:
        await message.answer("У вас нет доступа к этой команде.", reply_markup=main_menu_keyboard)

@router.message(F.text == "📩 Запустить рассылку с выбором тем")
async def start_topic_selection(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
        topics = load_topics()
        if topics:
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="✏️ Управление темами")],
                    [KeyboardButton(text="✅ Подтвердить")]
                ],
                resize_keyboard=True
            )
            await message.answer(
                "Доступные темы:\n" + "\n".join(topics),
                reply_markup=keyboard
            )
            await state.set_state(AdminStates.confirm_topic_selection)
        else:
            await message.answer("Темы не найдены. Сначала добавьте темы.", reply_markup=admin_menu_keyboard)
    else:
        await message.answer("У вас нет доступа к этой команде.", reply_markup=main_menu_keyboard)
@router.message(F.text == "✏️ Управление темами", AdminStates.confirm_topic_selection)
async def manage_topics_from_selection(message: Message, state: FSMContext):
    await manage_topics(message)

@router.message(F.text == "✅ Подтвердить", AdminStates.confirm_topic_selection)
async def confirm_topic_selection(message: Message, state: FSMContext, bot: Bot):
    users = load_users()
    active_users = {user_id: user_data for user_id, user_data in users.items() if user_data.get('status') == 'active'}
    topics = load_topics()

    if not topics:
        await message.answer("Темы не найдены. Сначала добавьте темы.", reply_markup=admin_menu_keyboard)
        return

    for user_id in active_users:
        try:
            await bot.send_message(
                chat_id=user_id,
                text="🌟 Пришло время выбрать тему для ближайшей встречи!\n"
                     "Выберите тему, которая вам ближе всего, и мы подберём для вас идеальную пару.",
                reply_markup=create_topic_keyboard(topics)  # Используем функцию для создания клавиатуры
            )
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

    await message.answer("Рассылка с выбором темы завершена.", reply_markup=admin_menu_keyboard)
    await state.clear()


@router.message(F.text == "🤝 Подбор пар ФУБ и пользователь")
async def match_fub_pairs(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к этой команде.", reply_markup=main_menu_keyboard)
        return

    await message.answer("Запуск подбора пар ФУБ ↔ пользователь...", reply_markup=ReplyKeyboardRemove())

    users = load_users()
    fub_members = {uid: data for uid, data in users.items()
                   if data.get('is_fub_member') == 'Да' and data.get('status') == 'active'}
    non_fub_members = {uid: data for uid, data in users.items()
                       if data.get('is_fub_member') != 'Да' and data.get('status') == 'active'}

    # Перемешиваем списки
    fub_ids = list(fub_members.keys())
    non_fub_ids = list(non_fub_members.keys())
    random.shuffle(fub_ids)
    random.shuffle(non_fub_ids)

    pairs = []
    min_pairs = min(len(fub_ids), len(non_fub_ids))

    # Формируем пары
    for i in range(min_pairs):
        pairs.append((fub_ids[i], non_fub_ids[i]))

    # Отправляем уведомления
    success_count = 0
    for fub_id, non_fub_id in pairs:
        try:
            # Сообщение члену ФУБ
            await bot.send_message(
                chat_id=fub_id,
                text=f"🎉 Ваша пара на эту неделю: {non_fub_members[non_fub_id]['name']}!\n"
                     f"💼 Работа: {non_fub_members[non_fub_id].get('work_place', 'не указано')}\n"
                     f"📝 Описание работы: {non_fub_members[non_fub_id].get('work_description', 'не указано')}\n"
                     f"🎯 Хобби: {non_fub_members[non_fub_id].get('hobbies', 'не указано')}\n"
                     f"Напишите своему партнеру: @{non_fub_members[non_fub_id].get('username', 'username_не_указан')}\n"
                     f"Договоритесь о встрече!"
            )

            # Сообщение не члену ФУБ
            await bot.send_message(
                chat_id=non_fub_id,
                text=f"🎉 Ваша пара на эту неделю: {fub_members[fub_id]['name']} (член клуба ФУБ)!\n"
                     f"💼 Работа: {fub_members[fub_id].get('work_place', 'не указано')}\n"
                     f"📝 Описание работы: {fub_members[fub_id].get('work_description', 'не указано')}\n"
                     f"🎯 Хобби: {fub_members[fub_id].get('hobbies', 'не указано')}\n"
                     f"Напишите своему партнеру: @{fub_members[fub_id].get('username', 'username_не_указан')}\n"
                     f"Договоритесь о встрече!"
            )
            success_count += 1
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения: {e}")

    # Уведомления для оставшихся без пары
    leftover_fub = len(fub_ids) - min_pairs
    leftover_non_fub = len(non_fub_ids) - min_pairs

    # Уведомляем членов ФУБ без пары
    if leftover_fub > 0:
        for i in range(min_pairs, len(fub_ids)):
            try:
                await bot.send_message(
                    chat_id=fub_ids[i],
                    text="😔 На этой неделе мы не смогли найти вам пару. Попробуем в следующий раз!"
                )
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения: {e}")

    # Уведомляем не членов ФУБ без пары
    if leftover_non_fub > 0:
        for i in range(min_pairs, len(non_fub_ids)):
            try:
                await bot.send_message(
                    chat_id=non_fub_ids[i],
                    text="😔 На этой неделе мы не смогли найти вам пару. Попробуем в следующий раз!"
                )
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения: {e}")

    # Отчет администратору
    report = (
        f"Подбор пар ФУБ ↔ пользователь завершен:\n"
        f"Успешно создано пар: {success_count}\n"
        f"Членов ФУБ без пары: {leftover_fub}\n"
        f"Пользователей без пары: {leftover_non_fub}"
    )

    await message.answer(report, reply_markup=admin_menu_keyboard)
    logging.info(report)