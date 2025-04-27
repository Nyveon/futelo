from sqlmodel import SQLModel, Field, Session
from typing import Optional, Dict, Any
import json
import time
from database import get_default_limits # Import helper
from pydantic import BaseModel
import sqlalchemy as sa

# --- Database Model ---
# Represents the structure in the 'user' table
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) # Telegram User ID
    telegram_user_id: int = Field(index=True) # Make telegram ID searchable and unique
    telegram_group_id: int = Field(index=True)
    currency_balance: int = Field(default=0)
    letter_limits_json: str = Field(default_factory=get_default_limits) # Store limits as JSON string
    consecutive_message_count: int = Field(default=0)

    #index for user and group
    __table_args__ = (
        sa.UniqueConstraint('telegram_user_id', 'telegram_group_id', name='uq_user_group'),
    )

    # Property to easily get/set python dict for limits
    @property
    def letter_limits(self) -> Dict[str, int]:
        return json.loads(self.letter_limits_json)

    @letter_limits.setter
    def letter_limits(self, value: Dict[str, int]):
        self.letter_limits_json = json.dumps(value)

class last_user_message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) # Telegram User ID
    telegram_group_id: int = Field(index=True, unique=True)
    telegram_user_id: int = Field(default=-1) # Make telegram ID searchable and unique
    count: int = Field(default=0)

# --- API Request/Response Models (using Pydantic features of SQLModel) ---

# Model for reading user data via API (excludes internal JSON representation)
class UserRead(BaseModel):
    telegram_user_id: int
    currency_balance: int
    letter_limits: Dict[str, int] # Use the property for API output
    consecutive_message_count: int

# Model for processing a message (after validation maybe)
class MessageProcessRequest(BaseModel):
    telegram_user_id: int
    telegram_group_id: int
    text: str # Text might be needed to calculate rewards/check validity again if needed
    # timestamp: float # Could pass timestamp from bot if needed

class ProcessResponse(BaseModel):
    success: bool
    message: Optional[str] = None

# Model for buying a lootbox
class LootboxBuyRequest(BaseModel):
    telegram_user_id: int
    telegram_group_id: int

class LootboxBuyResponse(BaseModel):
    success: bool
    message: str
    