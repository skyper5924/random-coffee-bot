import json

def load_users():
    try:
        with open('users.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open('users.json', 'w', encoding='utf-8') as file:
        json.dump(users, file, indent=4, ensure_ascii=False)

def load_topics():
    try:
        with open('topics.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_topics(topics):
    with open('topics.json', 'w', encoding='utf-8') as file:
        json.dump(topics, file, indent=4, ensure_ascii=False)

