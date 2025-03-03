import sqlite3

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Создаем таблицу пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            work_place TEXT NOT NULL,  -- Место работы
            work_description TEXT NOT NULL,  -- Описание работы
            hobbies TEXT NOT NULL,  -- Хобби
            topic TEXT NOT NULL,
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

    conn.commit()
    conn.close()

# Загрузка всех пользователей
def load_users():
    conn = sqlite3.connect('database.db')
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
def save_user(user_id, user_data):
    conn = sqlite3.connect('database.db')
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
        user_data['topic'],
        user_data.get('username'),
        user_data.get('status', 'active')
    ))
    conn.commit()
    conn.close()

# Загрузка всех тем
def load_topics():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT topic FROM topics')
    topics = cursor.fetchall()
    conn.close()
    return [topic[0] for topic in topics]

# Сохранение темы
def save_topic(topic):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO topics (topic) VALUES (?)', (topic,))
    conn.commit()
    conn.close()

# Удаление темы
def delete_topic(topic):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM topics WHERE topic = ?', (topic,))
    conn.commit()
    conn.close()

# Инициализация базы данных при импорте
init_db()