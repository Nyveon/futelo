from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
import random

from database import get_session
import crud # Import CRUD functions
from models import (
    UserRead,
    MessageProcessRequest, ProcessResponse, LootboxBuyRequest, LootboxBuyResponse
)
from utils import check_letter_limits

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
    is_valid_letters, reason, counts = crud.check_letter_limits(request.text, user.letter_limits)
    if not is_valid_letters:
        # Update stats but mark as invalid message maybe? Or just fail? Let's fail.
        # crud.update_user_message_stats(session, user, is_valid_message=False) # Optional: track invalid attempts
        return ProcessResponse(
            success=False,
            message=f"Message failed letter limit check: {reason}.",
        )
    
    last_user_message = crud.get_or_create_last_user_message(session, request.telegram_group_id)

    consecutive_count = crud.calculate_consecutive_messages(user, last_user_message)

    currency_change = 0
    if consequence_type == "earn":
        currency_change = amount
    elif consequence_type == "cost":
        if user.currency_balance < amount:
            # Update stats indicating an attempt but failure due to cost
            # crud.update_user_message_stats(session, user, is_valid_message=False, consecutive_count_override=next_consecutive_count) # Mark attempt?
            raise HTTPException(status_code=402, detail=f"Insufficient currency ({user.currency_balance}) to send message (cost: {amount}).")
        else:
            currency_change = -amount

    # 3. Apply changes and update stats
    if currency_change != 0:
        user = crud.update_user_currency(session, user, currency_change)

    # Update timestamp, consecutive count, total valid count, and potentially increase limits
    user = crud.update_user_message_stats(session, user, is_valid_message=True, consecutive_count_override=next_consecutive_count)

    # Prepare response
    updated_status = UserRead(
         telegram_user_id=user.telegram_user_id,
         currency_balance=user.currency_balance,
         letter_limits=user.letter_limits,
         total_valid_messages_sent=user.total_valid_messages_sent,
         last_message_timestamp=user.last_message_timestamp,
         consecutive_message_count=user.consecutive_message_count
    )
    
    msg = f"Message processed. Currency change: {currency_change}."
    if consequence_type == "cost":
        msg += f" Spam penalty applied: -{amount} currency."
    elif consequence_type == "earn":
         msg += f" Currency earned: +{amount}."


    return ProcessResponse(success=True, message=msg, updated_user_status=updated_status)

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

@router.get("/users/{telegram_user_id}", response_model=UserRead)
def get_user(telegram_user_id: int, session: Session = Depends(get_session)):
    """Fetches user details."""
    user = crud.get_user(session, telegram_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user
