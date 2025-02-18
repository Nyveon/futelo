from credentials import BOT_TOKEN
from telegram import Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ChatJoinRequestHandler
import sqlite3
from dataclasses import dataclass
from typing import Optional
from unidecode import unidecode
import random

#                    A B C D E F G H I J K L M N Ñ O P Q R S T U V W X Y Z 6 *
STARTING_LETTERS = ("1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0")



LVL_UP = [1]

for i in range(29):
    LVL_UP.append((i+1) * 5)



ADD_LETTER = [29]

for i in range(29):
    ADD_LETTER.append(ADD_LETTER[-1] + 5)

letters = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ6*"

letter_map = {letter: i for i, letter in enumerate(letters)}

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

    def add_letters(self, amount: int):
        letter_list = self.letter_limits_list
        possible = []
        for i in range(29):
            for _ in range(letter_list[i],6):
                possible.append(i)

        random.shuffle(possible)

        for i in range(amount):
            letter_list[possible[i]] += 1

        print(letter_list)
        
        self.letter_limits = ",".join( list(map(str, letter_list)) )

        return possible[:amount]

    
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
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (user_id, letter_limits, messages_sent) VALUES (?, ?, ?)", (user_id, STARTING_LETTERS, 0))
    conn.commit()
    conn.close()
    return User(user_id, STARTING_LETTERS, 0)


def new_chat_members(update: Update, context: CallbackContext):
    new_members = 0
    for member in update.message.new_chat_members:
        if not load(member.id):
            new_members += 1
            create_user(member.id)
    
    if new_members == 1:
        update.message.reply_text("¡Bienvenido! Si no sabes como funciona futelo, manda /reglas al dm")
    elif new_members > 1:
        chat = update.message.chat
        chat.send_message('¡Hola gamers! Soy Futelo-Bot y vine a futelar esta conversación 😎\
                                Iniciando, solo pueden usar las letras "A, H, L, O" 1 vez por mensaje\
                                No pueden usar ninguna otra letra, pueden decir "hola" :)\
                                Se iran desbloqueando más letras mientras hablen\
                                Pueden ver las reglas por dm con el comando /reglas\
                                Como dijo una gran persona en algun momento: ¡A futelar!')
        
def start(update: Update, context: CallbackContext):
    # add all chat members to the database
    for member in update.message.chat.get_members():
        if not load(member.id):
            create_user(member.id)
    
    update.message.chat.send_message('¡Hola gamers! Soy Futelo-Bot y vine a futelar esta conversación 😎\
                                Iniciando, solo pueden usar las letras "A, H, L, O" 1 vez por mensaje\
                                No pueden usar ninguna otra letra, pueden decir "hola" :)\
                                Se iran desbloqueando más letras mientras hablen\
                                Pueden ver las reglas por dm con el comando /reglas\
                                Como dijo una gran persona en algun momento: ¡A futelar!')

def filter_message(message: str, letter_limits: list):
    used_letters = [ 0 for _ in range(29) ]
    message = unidecode(message).upper()
    for letter in message:
        if letter.isalpha():
            letter_index = letter_map[letter]
        elif letter.isdigit():
            letter_index = 27
        elif letter.isspace():
            letter_index = -1
        else:
            letter_index = 28
        
        if letter_index != -1:
            used_letters[letter_index] += 1
    for i in range(29):
        if used_letters[i] > letter_limits[i]:
            return False
    
    return True


def rules(update: Update, context: CallbackContext):
    if update.message.chat.type == "private":
        update.message.reply_text("WIP")
    else:
        update.message.reply_text("Te enviare las reglas por dm")
        update.message.from_user.send_message("WIP")
    

def new_message(update: Update, context: CallbackContext):
    user = load(update.message.from_user.id)
    if not user:
        user = create_user(update.message.from_user.id)
    
    if filter_message(update.message.text, user.letter_limits_list):
        user.add_message()

        current_lvl = 0
        for lvl in LVL_UP:
            if user.messages_sent >= lvl:
                current_lvl+=1
            else:
                break

        print(current_lvl)
        print(LVL_UP)
        print(ADD_LETTER)
        
        current_letters = sum(user.letter_limits_list)

        supposed_letters = ADD_LETTER[current_lvl]

        if current_letters < supposed_letters:
            added_letters = user.add_letters(supposed_letters - current_letters)
            update.message.reply_text(f"¡Subiste de nivel! Consegusite las letras: {', '.join(letters[i] for i in added_letters)}")
            
        save(user)
    else:
        # delete message
        update.message.delete()



def main() -> None:

    init_db()

    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_chat_members))

    # dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(CommandHandler("reglas", rules))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, new_message))

    updater.start_polling()

    updater.idle()
    

if __name__ == '__main__':
    main()