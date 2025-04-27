from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
import random

from database import get_session
import crud # Import CRUD functions
from models import (
    UserRead, MessageProcessRequest, ProcessResponse, LootboxBuyRequest, LootboxBuyResponse
)
from utils import check_letter_limits, check_user_concurrent_message_count

# Create an API router
router = APIRouter()

@router.post("/messages/process", response_model=ProcessResponse)
def process_message(request: MessageProcessRequest, session: Session = Depends(get_session)):
    """
    Processes a message: validates limits, applies spam rules (currency changes),
    updates counts, potentially increases limits.
    Assumes the bot might call this *after* a basic check or directly.
    """
    user = crud.get_or_create_user(session, request.telegram_user_id)

    # 1. Validate letter limits again (important!)
    is_valid_letters, reason = check_letter_limits(request.text, user.letter_limits)
    if not is_valid_letters:
        return ProcessResponse(
            success=False,
            message=f"Message failed letter limit check: {reason}.",
        )
    
    last_user_message = crud.get_or_create_last_user_message(session, request.telegram_group_id)

    is_valid_consecutive, reason, needed_currency = check_user_concurrent_message_count(user, last_user_message)
    if not is_valid_consecutive:
        return ProcessResponse(
            success=False,
            message=f"Message failed consecutive message check: {reason}.",
        )
    
    # 2. Update user stats
    user = crud.update_user_after_message(session, user, last_user_message, needed_currency)

    return ProcessResponse(success=True)

# --- Lootbox Endpoint ---

@router.post("/lootbox/buy", response_model=LootboxBuyResponse)
def buy_lootbox(request: LootboxBuyRequest, session: Session = Depends(get_session)):
    """Allows a user to buy a letter lootbox."""
    LOOTBOX_COST = 50 # Example cost
    user = crud.get_or_create_user(session, request.telegram_user_id)

    if user.currency_balance < LOOTBOX_COST:
        raise HTTPException(status_code=402, detail=f"Insufficient currency. Need {LOOTBOX_COST}, have {user.currency_balance}.")

    # Deduct cost
    user = crud.update_user_currency(session, user, -LOOTBOX_COST)

    # --- Determine Reward ---
    # Example: Increase limit for 1-3 random letters by +1
    num_letters_to_increase = random.randint(1, 3)
    letters = [chr(ord('A') + i) for i in range(26)]
    letters_to_increase = random.sample(letters, num_letters_to_increase)

    current_limits = user.letter_limits
    reward_details = []
    for letter in letters_to_increase:
        current_limits[letter] = current_limits.get(letter, 0) + 1
        reward_details.append(f"'{letter}' limit +1")

    user = crud.update_user_limits(session, user, current_limits)
    # --- End Reward Logic ---

    reward_description = ", ".join(reward_details)
    msg = f"Lootbox purchased for {LOOTBOX_COST} currency! Rewards: {reward_description}."

    updated_status = UserRead(
         telegram_user_id=user.telegram_user_id,
         currency_balance=user.currency_balance,
         letter_limits=user.letter_limits,
         total_valid_messages_sent=user.total_valid_messages_sent,
         last_message_timestamp=user.last_message_timestamp,
         consecutive_message_count=user.consecutive_message_count
    )

    return LootboxBuyResponse(success=True, message=msg, reward_description=reward_description, updated_user_status=updated_status)

@router.get("/users/{telegram_group_id}/{telegram_user_id}", response_model=UserRead)
def get_user(telegram_user_id: int, telegram_group_id, session: Session = Depends(get_session)):
    """Fetches user details."""
    user = crud.get_user(session, telegram_user_id, telegram_group_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user
