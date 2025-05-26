from typing import Optional

from telegram import (
    Chat,
    ChatMember,
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import crud
from api_routes import process_buy_lootbox, process_message, process_open_lootbox
from config import BOT_TOKEN
from database import get_session


# function stolen from https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/chatmemberbot.py
# hehehe
def extract_status_change(
    chat_member_update: ChatMemberUpdated,
) -> Optional[tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get(
        "is_member", (None, None)
    )

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def join_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.my_chat_member is None or update.effective_chat is None:
        return
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result
    chat = update.effective_chat
    if (
        chat.type in [Chat.GROUP, Chat.SUPERGROUP]
        and was_member is False
        and is_member is True
    ):
        await update.effective_chat.send_message(
            "MENSAJE DE LLEGADA recuerda darme permisos de admin blabla"
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None or update.message is None:
        return
    if update.effective_chat.type not in [Chat.GROUP, Chat.SUPERGROUP]:
        await update.message.reply_text(
            "Este bot solo funciona en grupos. Úsalo en un grupo o supergrupo."
        )
        return
    bot_member = await context.bot.get_chat_member(
        chat_id=update.effective_chat.id, user_id=context.bot.id
    )
    if bot_member.status not in [
        ChatMember.ADMINISTRATOR,
        ChatMember.OWNER,
    ]:
        await update.message.reply_text(
            "¡Hola! Para usar este bot, por favor, asegúrate de darme permisos de administrador."
        )
        return
    else:
        # quizas podriamos hacer algo para que el bot no funcione si no es admin
        welcome_message = await update.message.reply_text(
            "¡Hola! REGLAS MENSAJE DE BIENVENIDA Y LINK A MINI APP"
        )
        await welcome_message.pin()


async def greet_chat_members(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.chat_member is None or update.effective_chat is None:
        return
    result = extract_status_change(update.chat_member)
    if result is None:
        return
    was_member, is_member = result
    chat = update.effective_chat
    if (
        chat.type in [Chat.GROUP, Chat.SUPERGROUP]
        and was_member is False
        and is_member is True
    ):
        await update.chat_member.from_user.send_message("MENSAJE DE BIENVENIDA")


async def receive_message(update: Update, context: CallbackContext) -> None:
    if (
        update.message is None
        or update.message.text is None
        or update.message.from_user is None
    ):
        return
    if update.message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        process_response = await process_message(
            update.message.from_user.id, update.message.chat.id, update.message.text
        )
        if process_response.success:
            if process_response.lost_currency:
                await update.message.from_user.send_message(
                    "ADVERTENCIA DE PERDER MONEDAS"
                )
        else:
            await update.message.from_user.send_message(
                f"MENSAJE DE ERROR: {process_response.message}"
            )
            await update.message.delete()
    else:
        await update.message.from_user.send_message(
            "Este bot solo funciona en grupos. Úsalo en un grupo o supergrupo."
        )


async def buy_lootbox(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None:
        return
    if update.message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        buy_response = await process_buy_lootbox(
            update.message.from_user.id, update.message.chat.id
        )
        if buy_response.success:
            await update.message.chat.send_message(
                f"¡Has conseguido una lootbox de rareza {buy_response.rarity}!\n",
                reply_markup=InlineKeyboardMarkup(
                    [
                        InlineKeyboardButton(
                            "Abrir lootbox",
                            callback_data=f"open_lootbox_{buy_response.lootbox_id}",
                        ),
                    ]
                ),
            )
        else:
            await update.message.from_user.send_message(
                f"MENSAJE DE ERROR: {buy_response.message}"
            )
        await update.message.delete()
    else:
        await update.message.from_user.send_message(
            "Este bot solo funciona en grupos. Úsalo en un grupo o supergrupo."
        )


async def open_lootbox(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (
        update.callback_query is None
        or update.callback_query.from_user is None
        or update.callback_query.data is None
        or update.callback_query.message is None
    ):
        return
    if update.callback_query.data.startswith("open_lootbox_"):
        lootbox_id = int(update.callback_query.data.split("_")[2])
        open_response = await process_open_lootbox(
            update.callback_query.from_user.id,
            update.callback_query.message.chat.id,
            lootbox_id,
        )
        await update.callback_query.answer()
        if open_response.success:
            await update.callback_query.chat_instance.send_message(
                f"¡Has abierto la lootbox y has conseguido: {', '.join(open_response.new_letters)}!"
            )
            await update.callback_query.message.delete()
        else:
            await update.callback_query.from_user.send_message(
                f"MENSAJE DE ERROR: {open_response.message}"
            )


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None:
        return
    await update.message.from_user.send_message("REGLAS DEL GRUPO")
    await update.message.delete()


# for testing purposes
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None:
        return
    if update.message.chat.type not in [Chat.GROUP, Chat.SUPERGROUP]:
        await update.message.from_user.send_message(
            "Este bot solo funciona en grupos. Úsalo en un grupo o supergrupo."
        )
        return
    session = get_session()
    user = crud.get_or_create_user(
        session, update.message.from_user.id, update.message.chat.id
    )
    await update.message.from_user.send_message(
        f"ID: {user.telegram_user_id}\n"
        f"Grupo: {user.telegram_group_id}\n"
        f"Monedas: {user.currency_balance}\n"
        f"Mensajes enviados: {user.number_of_messages_sent}\n"
        f"Letras: {', '.join(user.letters)}\n"
    )
    session.close()
    await update.message.delete()


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(
        ChatMemberHandler(join_chat, ChatMemberHandler.MY_CHAT_MEMBER)
    )
    application.add_handler(
        ChatMemberHandler(greet_chat_members, ChatMemberHandler.CHAT_MEMBER)
    )
    application.add_handler(CommandHandler("comprar_lootbox", buy_lootbox))
    application.add_handler(
        CallbackQueryHandler(open_lootbox, pattern=r"^open_lootbox_")
    )
    application.add_handler(CommandHandler("reglas", rules))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message)
    )
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("start", start))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
