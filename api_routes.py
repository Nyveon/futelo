from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
import random

from database import get_session
import crud # Import CRUD functions
from models import (
    UserRead, MessageProcessRequest, ProcessResponse, LootboxBuyRequest, LootboxBuyResponse, LootboxOpenRequest, LootboxOpenResponse
)
from utils import check_letter_limits, check_user_concurrent_message_count, choose_letters
from numpy import random
import config

# Create an API router
router = APIRouter()

@router.post("/messages/process", response_model=ProcessResponse)
def process_message(request: MessageProcessRequest, session: Session = Depends(get_session)):
    """
    Processes a message: validates limits, applies spam rules (currency changes),
    updates counts, potentially increases limits.
    Assumes the bot might call this *after* a basic check or directly.
    """
    user = crud.get_or_create_user(session, request.telegram_user_id, request.telegram_group_id)

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

    return ProcessResponse(success=True, message=None)

@router.post("/lootbox/buy", response_model=LootboxBuyResponse)
def buy_lootbox(request: LootboxBuyRequest, session: Session = Depends(get_session)):
    """Allows a user to buy a letter lootbox."""
    LOOTBOX_COST = config.lootbox_cost
    with session.begin():
        user = crud.get_or_create_user(session, request.telegram_user_id, request.telegram_group_id)

        if user.currency_balance < LOOTBOX_COST:
            return LootboxBuyResponse(
                success=False,
                message=f"Insufficient currency to buy lootbox. Needed: {LOOTBOX_COST}, Available: {user.currency_balance}.",
                lootbox_id=None,
                rarity=None,
            )

        # Deduct cost
        user = crud.update_user_currency(session, user, -LOOTBOX_COST)
        
        rarity = str(random.choice([lootbox["rarity"] for lootbox in config.lootboxes], p=[lootbox["probability"] for lootbox in config.lootboxes]))

        lootbox = crud.create_lootbox(session, request.telegram_user_id, request.telegram_group_id, rarity)

        return LootboxBuyResponse(success=True, message=None, lootbox_id=lootbox.id, rarity=rarity)


@router.post("/lootbox/open", response_model=LootboxOpenResponse)
def open_lootbox(request: LootboxOpenRequest, session: Session = Depends(get_session)):
    """Allows a user to open a letter lootbox."""
    with session.begin():
        lootbox = crud.get_lootbox(session, request.lootbox_id)

        if not lootbox:
            return LootboxOpenResponse(
                success=False,
                message="Lootbox not found.",
                new_letters=None,
            )
        
        if lootbox.telegram_user_id != request.telegram_user_id or lootbox.telegram_group_id != request.telegram_group_id:
            return LootboxOpenResponse(
                success=False,
                message="Lootbox does not belong to this user or group.",
                new_letters=None,
            )

        if lootbox.opened:
            return LootboxOpenResponse(
                success=False,
                message="Lootbox already opened.",
                new_letters=None,
            )

        
        
        lootbox.opened = True
        session.add(lootbox)
        session.commit()

        rarity = lootbox.rarity
        lootbox_config = next((lootbox for lootbox in config.lootboxes if lootbox["rarity"] == rarity), None)
        if lootbox_config is None:
            return LootboxOpenResponse(
                success=False,
                message="Lootbox rarity not found in configuration.",
                new_letters=None,
            )
        new_letter_count = lootbox_config["reward"]

        user = crud.get_or_create_user(session, lootbox.telegram_user_id, lootbox.telegram_group_id)
        new_letters = choose_letters(new_letter_count, user)

        if len(new_letters) == 0:
            return LootboxOpenResponse(
                success=False,
                message="No letters available to choose from.",
                new_letters=None,
            )

        user = crud.add_letters_to_user(session, user, new_letters)

        if len(new_letters) != new_letter_count:
            return LootboxOpenResponse(
                success=True,
                message="User has reached letter limits, some letters were not added.",
                new_letters=new_letters,
            )
        
        return LootboxOpenResponse(
            success=True,
            message="Lootbox opened successfully.",
            new_letters=new_letters,
        )

@router.get("/users/{telegram_group_id}/{telegram_user_id}", response_model=UserRead)
def get_user(telegram_user_id: int, telegram_group_id, session: Session = Depends(get_session)):
    """Fetches user details."""
    user = crud.get_user(session, telegram_user_id, telegram_group_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user
