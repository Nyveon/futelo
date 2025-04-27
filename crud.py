from sqlmodel import Session, select
from models import User, last_user_message
import json
import time
from typing import Optional, Dict

# --- User Operations ---

def get_user(session: Session, telegram_user_id: int, telegram_group_id: int) -> Optional[User]:
    """Fetches a user by their Telegram ID."""
    statement = select(User).where(User.telegram_user_id == telegram_user_id, User.telegram_group_id == telegram_group_id)
    user = session.exec(statement).first()
    return user

def get_or_create_user(session: Session, telegram_user_id: int, telegram_group_id: int) -> User:
    """Gets a user by Telegram ID, or creates them if they don't exist."""
    user = get_user(session, telegram_user_id, telegram_group_id)
    if not user:
        print(f"Creating new user entry for ID: {telegram_user_id} in group {telegram_group_id}.")
        user = User(telegram_user_id=telegram_user_id, telegram_group_id=telegram_group_id)
        session.add(user)
        session.commit()
        session.refresh(user) # Load defaults like limits from DB
        print(f"User {telegram_user_id} created.")
    return user


# --- Helper Functions for Logic (can be moved to a separate 'logic.py' later) ---


def get_last_user_message(session: Session, telegram_group_id: int) -> last_user_message:
    statement = select(last_user_message).where(last_user_message.telegram_group_id == telegram_group_id)
    last_message = session.exec(statement).first()
    return last_message

def get_or_create_last_user_message(session: Session, telegram_group_id: int) -> last_user_message:
    """Gets the last user message entry for a group, or creates it if it doesn't exist."""
    last_message = get_last_user_message(session, telegram_group_id)
    if not last_message:
        print(f"Creating new last user message entry for group ID: {telegram_group_id}.")
        last_message = last_user_message(telegram_group_id=telegram_group_id)
        session.add(last_message)
        session.commit()
        session.refresh(last_message)
        print(f"Last user message entry for group {telegram_group_id} created.")
    return last_message

def update_user_after_message(session: Session, user: User, group_last_message: last_user_message, needed_currency: int) -> User:
    """Updates user stats after processing a message."""
    user.number_of_messages_sent += 1
    user.currency_balance -= needed_currency
    if group_last_message.telegram_user_id == user.telegram_user_id:
        group_last_message.count += 1
    else:
        group_last_message.telegram_user_id = user.telegram_user_id
        group_last_message.count = 1
    session.add(user)
    session.add(group_last_message)
    session.commit()
    session.refresh(user)
    session.refresh(group_last_message)
    return user

def update_user_currency(session: Session, user: User, change: int) -> User:
    """Updates user's currency balance."""
    user.currency_balance += change
    session.add(user)
    session.commit()
    session.refresh(user)
    return user