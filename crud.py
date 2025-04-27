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

def update_user_currency(session: Session, user: User, change: int) -> User:
    """Updates user's currency balance."""
    user.currency_balance += change
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def update_user_limits(session: Session, user: User, new_limits: Dict[str, int]) -> User:
    """Updates the user's letter limits."""
    user.letter_limits = new_limits # Uses the setter property
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def update_user_message_stats(session: Session, user: User, is_valid_message: bool, consecutive_count_override: Optional[int] = None) -> User:
    """Updates message counts and anti-spam state."""
    current_time = time.time()
    
    # Define anti-spam timeout (e.g., 10 seconds)
    SPAM_TIMEOUT = 10.0 

    if user.last_message_timestamp is None or (current_time - user.last_message_timestamp > SPAM_TIMEOUT):
         user.consecutive_message_count = 1 # Reset sequence
    elif consecutive_count_override is not None:
         user.consecutive_message_count = consecutive_count_override
    else:
        user.consecutive_message_count += 1

    user.last_message_timestamp = current_time

    if is_valid_message: # Only increment total count for valid messages processed
        user.total_valid_messages_sent += 1

        # --- Placeholder: Logic to increase limits based on total messages ---
        # Example: Increase all limits by 1 every 50 valid messages
        LIMIT_INCREASE_THRESHOLD = 50
        if user.total_valid_messages_sent > 0 and user.total_valid_messages_sent % LIMIT_INCREASE_THRESHOLD == 0:
            print(f"User {user.telegram_user_id} reached {user.total_valid_messages_sent} messages. Increasing limits.")
            current_limits = user.letter_limits
            new_limits = {letter: limit + 1 for letter, limit in current_limits.items()}
            user.letter_limits = new_limits # Use property setter

    session.add(user)
    session.commit()
    session.refresh(user)
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


def calculate_spam_consequence(consecutive_count: int) -> tuple[str, int]:
    """Determines the currency consequence based on consecutive message count."""
    # Pattern: 1st=earn, 2nd=nothing, 3rd=cost, 4th=earn, etc.
    MODULO = 3
    EARN_AMOUNT = 5 # Example currency amount
    COST_AMOUNT = 10 # Example currency cost

    remainder = consecutive_count % MODULO
    
    if remainder == 1:
        return "earn", EARN_AMOUNT
    elif remainder == 2:
        return "nothing", 0
    elif remainder == 0: # Corresponds to 3rd, 6th, 9th...
        return "cost", COST_AMOUNT
    else: # Should not happen
        return "nothing", 0