from private_info import BOT_TOKEN, LAST_USER_DATA, MINI_APP_LINK
from telegram import Update
from telegram.ext import CommandHandler, filters, MessageHandler, CallbackContext, Application
from config import LEVELS, MIN_MESSAGES_FOR_LEVEL
from utils import filter_message, letters_by_messages, current_letters, choose_letters_to_add, index_to_character, current_level
from collections import Counter
from db import init_db, load, create_user, save, User
import json

async def start(update: Update, context: CallbackContext):

    if update.message.chat.type == "private":
        await update.message.reply_text('¡Futelo es mas divertido con amigos! ¡Agregame a un grupo!')
    else:
        #todo: might not be necessary with latest ptb version
        # bot_member = await update.message.chat.get_member(context.bot.id)
        # breakpoint()
        # if not bot_member.can_delete_messages:
        #     await update.message.reply_text("¡Para funcionar debo poder eliminar mensajes!")
        # else:
        await update.message.chat.send_message('¡Hola gamers! Soy Futelo-Bot y vine a futelar esta conversación 😎\
                                        Iniciando, solo pueden usar las letras "A, H, L, O" 1 vez por mensaje\
                                        No pueden usar ninguna otra letra, pueden decir "hola" :)\
                                        Se iran desbloqueando más letras mientras hablen\
                                        Pueden ver las reglas por dm con el comando /reglas\
                                        Como dijo una gran persona en algun momento: ¡A futelar!'
        )
        mini_app_message = await update.message.chat.send_message(f'Revisa tu mensaje antes de enviarlo con la mini app\
                                                                  {MINI_APP_LINK}')

        await mini_app_message.pin()


async def rules(update: Update, context: CallbackContext):
    REGLAS = ("Futelini \\= Futelo pero gamer, con inventario, progresion y mas\\.\n"
            "\\- Cada jugador tiene su inventario que limita sus mensajes 😳\n"
            "\\- Se parte con cuatro letras: H, O, L, A\\.\n"
            "\\- Consigues nuevas letras subiendo de nivel\n"
            "\\- La primera vez consigues 25 letras, las siguientes 5\n"
            "\\- ¡Subir de nivel es cada vez mas dificil\\!\n"
            "\\- Primero subes mandando 1 mensaje, luego mandando 2, luego 3, y así\\.\\.\\.\n"
            "\\- Ojo que no puedes mandar mensajes consecutivos\\!"
            )
    if update.message.chat.type == "private":
        await update.message.reply_text(REGLAS, parse_mode="MarkdownV2")
    else:
        await update.message.reply_text("Te enviare las reglas por dm")
        await update.message.from_user.send_message(REGLAS)
    
def parse_lvl_up_message(letters_to_add: list):
    agg_letters = Counter(letters_to_add)
    message = "Desbloqueaste las siguientes letras: "
    for letter, amount in agg_letters.items():
        message += f"{amount} {index_to_character(letter)}, "
    return message


async def new_message(update: Update, context: CallbackContext):

    user = load(update.message.from_user.id)

    if not user:
        user = create_user(update.message.from_user.id)

    if update.message.chat.type == "private":
        
        if not filter_message(update.message.text, user.letter_limits_list):
            
            await update.message.reply_text("Tu mensaje no futela")

    else:

        if update.message.from_user.id != last_user and filter_message(update.message.text, user.letter_limits_list):
            user.add_message()

            letter_difference = max(letters_by_messages(user.messages_sent) - current_letters(user.letter_limits_list), 0)

            if letter_difference:
                letters_to_add = choose_letters_to_add(user.letter_limits_list, letter_difference)
                user.add_letters(letters_to_add)
                await update.message.reply_text(parse_lvl_up_message(letters_to_add))


            save(user)

            save_last_user(update.message.from_user.id)

        else:

            await update.message.delete()


def get_stats(user: User):

    mensaje = f"Has enviado {user.messages_sent} mensajes\n"
    mensaje += "Letras desbloqueadas: \n"
    for i, letter in enumerate(user.letter_limits_list):
        mensaje += f"{index_to_character(i)}: {letter}\n"
    if current_level(user.messages_sent) == LEVELS - 1:
        mensaje += "¡Has desbloqueado todas las letras!"
    else:
        mensaje += f"Te faltan {MIN_MESSAGES_FOR_LEVEL[current_level(user.messages_sent)+1] - user.messages_sent} mensajes para subir de nivel"

    return mensaje


async def stats(update: Update, context: CallbackContext):
    user = load(update.message.from_user.id)

    if not user:
        user = create_user(update.message.from_user.id)
    
    if update.message.chat.type == "private":
        await update.message.reply_text(get_stats(user))
    else:
        await update.message.reply_text("Te enviare tus stats por dm")
        await update.message.from_user.send_message(get_stats(user))

def load_last_user():
    global last_user
    try:
        with open(LAST_USER_DATA, 'r') as file:
            last_user = json.load(file)
    except FileNotFoundError:
        last_user = None

def save_last_user(user_id: int):
    global last_user
    last_user = user_id
    with open(LAST_USER_DATA, 'w') as file:
        json.dump(last_user, file)

def main() -> None:

    init_db()
    load_last_user()

    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reglas", rules))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, new_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
    

if __name__ == '__main__':
    main()