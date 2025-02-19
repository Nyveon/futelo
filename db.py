import sqlite3
from dataclasses import dataclass
from typing import Optional
from config import STARTING_LETTERS

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    letter_limits TEXT,
                    messages_sent INTEGER
                 )''')
    conn.commit()
    conn.close()

@dataclass
class User:
    user_id: int
    letter_limits: str
    messages_sent: int

    @property
    def letter_limits_list(self):
        return list(map(int, self.letter_limits.split(",")))
    
    def add_message(self):
        self.messages_sent += 1

    def add_letters(self, letters: list):
        letter_list = self.letter_limits_list
        for letter in letters:
            letter_list[letter] += 1
        self.letter_limits = ",".join(map(str, letter_list))
    
def save(user: User):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET letter_limits = ?, messages_sent = ? WHERE user_id = ?", (user.letter_limits, user.messages_sent, user.user_id))
    conn.commit()
    conn.close()

def load(user_id: int) -> Optional[User]:
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        return User(user_id, user_data[1], user_data[2])
    return None

def create_user(user_id: int) -> User:
    print(f"Creating user {user_id}")
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (user_id, letter_limits, messages_sent) VALUES (?, ?, ?)", (user_id, STARTING_LETTERS, 0))
    conn.commit()
    conn.close()
    return User(user_id, STARTING_LETTERS, 0)