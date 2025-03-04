import sqlite3
import logging

logger = logging.getLogger(__name__)

def init_db():
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()

        # Создаем таблицу пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                work_place TEXT NOT NULL,
                work_description TEXT NOT NULL,
                hobbies TEXT NOT NULL,
                topic TEXT,
                username TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')

        # Создаем таблицу тем
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT UNIQUE NOT NULL
            )
        ''')

        # Создаем таблицу для истории выбранных тем
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_topics_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                selected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("База данных инициализирована.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")

# Загрузка всех пользователей
def load_users():
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return {user[1]: {
        'name': user[2],
        'work_place': user[3],
        'work_description': user[4],
        'hobbies': user[5],
        'topic': user[6],
        'username': user[7],
        'status': user[8]
    } for user in users}

# Сохранение пользователя
def save_user(user_id: str, user_data: dict):
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, name, work_place, work_description, hobbies, topic, username, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        user_data['name'],
        user_data['work_place'],
        user_data['work_description'],
        user_data['hobbies'],
        user_data.get('topic', ''),  # Обновляем тему
        user_data.get('username', ''),
        user_data.get('status', 'active')
    ))
    conn.commit()
    conn.close()

# Загрузка всех тем
def load_topics():
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT topic FROM topics')
    topics = cursor.fetchall()
    conn.close()
    return [topic[0] for topic in topics]

# Сохранение темы
def save_topic(topic):
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO topics (topic) VALUES (?)', (topic,))
    conn.commit()
    conn.close()

# Удаление темы
def delete_topic(topic):
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM topics WHERE topic = ?', (topic,))
    conn.commit()
    conn.close()

def save_user_topic(user_id: str, topic: str):
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_topics_history (user_id, topic)
        VALUES (?, ?)
    ''', (user_id, topic))
    conn.commit()
    conn.close()

# Инициализация базы данных при импорте
init_db()