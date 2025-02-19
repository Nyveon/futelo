from credentials import BOT_TOKEN
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from utils import filter_message, letters_by_messages, current_letters, choose_letters_to_add, index_to_character
from collections import Counter
from db import init_db, load, create_user, save
        
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