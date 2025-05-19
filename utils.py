from unidecode import unidecode
from typing import Dict, Optional
from models import User, last_user_message
from config import CURRENCY_AWARDED, lootboxes, lootbox_cost
import random
from math import ceil


def check_letter_limits(
    text: str, limits: Dict[str, int]
) -> tuple[bool, Optional[str]]:
    """Checks if the text adheres to the letter limits."""
    counts = {chr(ord("A") + i): 0 for i in range(26)}
    counts["9"] = 0  # For numbers, if needed
    counts["*"] = 0  # For special characters
    text_upper = text.upper()
    counts["Ñ"] = text_upper.count("Ñ")
    text_upper = text_upper.replace("Ñ", "")  # Remove Ñ for further counting
    text_upper = unidecode(text_upper).upper()

    for char in text_upper:
        if "A" <= char <= "Z":
            counts[char] += 1
        elif char.isdigit():
            counts["9"] += 1
        elif not char.isspace():
            counts["*"] += 1

    for letter, count in counts.items():
        if count > limits.get(letter, 0):
            return False, f"Too many '{letter}'s"

    return True, None


def calculate_first_message_currency():
    expected_lootbox = 0
    for lootbox in lootboxes:
        expected_lootbox += lootbox["probability"] * lootbox["reward"]
    return ceil(30 / expected_lootbox) * lootbox_cost


def check_user_concurrent_message_count(
    user: User, group_last_message: last_user_message
) -> tuple[bool, Optional[str], int]:
    """Checks the user's consecutive message count and updates it."""
    if user.telegram_user_id == group_last_message.telegram_user_id:
        consecutive_count = group_last_message.count + 1
    else:
        consecutive_count = 1

    if user.number_of_messages_sent == 0:
        needed_currency = calculate_first_message_currency()
    else:
        needed_currency = -CURRENCY_AWARDED.get(min(consecutive_count, 3))

    if user.currency_balance < needed_currency:
        return (
            False,
            f"Insufficient currency for consecutive message count. Needed: {needed_currency}, Available: {user.currency_balance}.",
            needed_currency,
        )
    return True, None, needed_currency


def choose_letters(letter_count: int, user: User) -> list[str]:
    """Chooses letters based on the user's letter limits."""
    possible_letters = []
    for letter, limit in user.letter_limits.items():
        possible_letters.extend([letter] * (6 - limit))
    return random.sample(possible_letters, min(letter_count, len(possible_letters)))
