from config import BOT_TOKEN, MINI_APP_LINK
from telegram.ext import Application, ChatMemberHandler, ContextTypes, MessageHandler, filters, CallbackContext
from telegram import Update, ChatMember, ChatMemberUpdated
from typing import Optional

# function stolen from https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/chatmemberbot.py
# hehehe
def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

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

async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def greet_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def process_message(update: Update, context: CallbackContext) -> None:
    pass

def main() -> None:

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(ChatMemberHandler(greet_chat_members, ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
