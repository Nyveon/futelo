from unidecode import unidecode
from typing import Dict, Optional

def check_letter_limits(text: str, limits: Dict[str, int]) -> tuple[bool, Optional[str]]:
    """Checks if the text adheres to the letter limits."""
    counts = {chr(ord('A') + i): 0 for i in range(26)}
    counts['9'] = 0 # For numbers, if needed
    counts['*'] = 0 # For special characters
    text_upper = text.upper()
    counts['Ñ'] = text_upper.count('Ñ')
    text_upper = text_upper.replace('Ñ', '') # Remove Ñ for further counting
    text_upper = unidecode(text_upper).upper()

    for char in text_upper:
        if 'A' <= char <= 'Z':
            counts[char] += 1
        elif char.isdigit():
            counts['9'] += 1
        elif not char.isspace():
            counts['*'] += 1

    for letter, count in counts.items():
        if count > limits.get(letter, 0):
            return False, f"Too many '{letter}'s"

    return True, None
