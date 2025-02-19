from unidecode import unidecode
import random
from config import MIN_MESSAGES_FOR_LEVEL, LEVELS, LETTERS_AT_LEVEL, CHARACTER_LIMITS, MAX_LIMIT

CHARACTERS = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"

def character_to_index(character: str) -> int:
    if character.isalpha():
        return CHARACTERS.index(character)
    elif character.isdigit():
        return 27
    elif character.isspace():
        return -1
    else:
        return 28

def index_to_character(index: int) -> str:
    if index < 27:
        return CHARACTERS[index]
    elif index == 27:
        return "numbers"
    else:
        return "special characters"


def letters_used(message: str) -> list:
    used_letters = [ 0 for _ in range(CHARACTER_LIMITS) ]
    message = unidecode(message).upper()
    for letter in message:
        letter_index = character_to_index(letter)
        if letter_index != -1:
            used_letters[letter_index] += 1
    return used_letters


def filter_message(message: str, letter_limits: list):
    used_letters = letters_used(message)
    for i in range(CHARACTER_LIMITS):
        if used_letters[i] > letter_limits[i]:
            return False
    return True

def current_level(messages_sent: int) -> int:
    for i in range(LEVELS):
        if messages_sent < MIN_MESSAGES_FOR_LEVEL[i]:
            return i - 1
    return LEVELS - 1

def letters_by_messages(messages_sent: int) -> int:
    return LETTERS_AT_LEVEL[current_level(messages_sent)]

def current_letters(letter_limits: list) -> int:
    return sum(letter_limits)

def missing_letters(letter_limits: list) -> list:
    missing = []
    for i in range(CHARACTER_LIMITS):
        for j in range(letter_limits[i],MAX_LIMIT):
            missing.append(i)
    return missing

def choose_letters_to_add(letter_limits: list, amount: int) -> list:
    missing = missing_letters(letter_limits)
    random.shuffle(missing)
    return missing[:amount]