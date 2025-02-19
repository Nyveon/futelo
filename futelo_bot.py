from credentials import BOT_TOKEN
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import sqlite3
from dataclasses import dataclass
from typing import Optional
from config import STARTING_LETTERS
from utils import filter_message, letters_by_messages, current_letters, choose_letters_to_add, index_to_character
from collections import Counter

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
        
def start(update: Update, context: CallbackContext):

    if update.message.chat.type == "private":
        update.message.reply_text('¡Futelo es mas divertido con amigos! ¡Agregame a un grupo!')
    else:
        bot_member = update.message.chat.get_member(context.bot.id)
        if not bot_member.can_delete_messages:
            update.message.reply_text("¡Para funcionar debo poder eliminar mensajes!")
        else:
            update.message.chat.send_message('¡Hola gamers! Soy Futelo-Bot y vine a futelar esta conversación 😎\
                                            Iniciando, solo pueden usar las letras "A, H, L, O" 1 vez por mensaje\
                                            No pueden usar ninguna otra letra, pueden decir "hola" :)\
                                            Se iran desbloqueando más letras mientras hablen\
                                            Pueden ver las reglas por dm con el comando /reglas\
                                            Como dijo una gran persona en algun momento: ¡A futelar!')


def rules(update: Update, context: CallbackContext):
    if update.message.chat.type == "private":
        update.message.reply_text("WIP")
    else:
        update.message.reply_text("Te enviare las reglas por dm")
        update.message.from_user.send_message("WIP")
    
def parse_lvl_up_message(letters_to_add: list):
    agg_letters = Counter(letters_to_add)
    message = "Desbloqueaste las siguientes letras: "
    for letter, amount in agg_letters.items():
        message += f"{amount} {index_to_character(letter)}, "
    return message


def new_message(update: Update, context: CallbackContext):

    user = load(update.message.from_user.id)

    if not user:
        user = create_user(update.message.from_user.id)

    if filter_message(update.message.text, user.letter_limits_list):
        user.add_message()

        letter_difference = max(letters_by_messages(user.messages_sent) - current_letters(user.letter_limits_list), 0)

        if letter_difference:
            letters_to_add = choose_letters_to_add(user.letter_limits_list, letter_difference)
            user.add_letters(letters_to_add)
            update.message.reply_text(parse_lvl_up_message(letters_to_add))


        save(user)

    else:

        update.message.delete()



def main() -> None:

    init_db()

    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("reglas", rules))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, new_message))

    updater.start_polling()

    updater.idle()
    

if __name__ == '__main__':
    main()