from sqlmodel import SQLModel, Field, Session
from typing import Optional, Dict, Any
import json
import time
from database import get_default_limits # Import helper

# --- Database Model ---
# Represents the structure in the 'user' table
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) # Telegram User ID
    telegram_user_id: int = Field(index=True, unique=True) # Make telegram ID searchable and unique

    currency_balance: int = Field(default=0)
    letter_limits_json: str = Field(default_factory=get_default_limits) # Store limits as JSON string
    total_valid_messages_sent: int = Field(default=0)
    last_message_timestamp: Optional[float] = Field(default=None)
    consecutive_message_count: int = Field(default=0)

    # Property to easily get/set python dict for limits
    @property
    def letter_limits(self) -> Dict[str, int]:
        return json.loads(self.letter_limits_json)

    @letter_limits.setter
    def letter_limits(self, value: Dict[str, int]):
        self.letter_limits_json = json.dumps(value)

# --- API Request/Response Models (using Pydantic features of SQLModel) ---

# Model for reading user data via API (excludes internal JSON representation)
class UserRead(SQLModel):
    telegram_user_id: int
    currency_balance: int
    letter_limits: Dict[str, int] # Use the property for API output
    total_valid_messages_sent: int
    last_message_timestamp: Optional[float]
    consecutive_message_count: int

# Model for validating a message
class MessageValidateRequest(SQLModel):
    telegram_user_id: int
    text: str

class ValidationResponse(SQLModel):
    is_valid: bool
    reason: Optional[str] = None
    letter_counts: Optional[Dict[str, int]] = None
    required_currency: int = 0 # Cost if it's a 'cost' message in sequence

# Model for processing a message (after validation maybe)
class MessageProcessRequest(SQLModel):
    telegram_user_id: int
    text: str # Text might be needed to calculate rewards/check validity again if needed
    # timestamp: float # Could pass timestamp from bot if needed

class ProcessResponse(SQLModel):
    success: bool
    message: str
    updated_user_status: Optional[UserRead] = None # Return updated status

# Model for buying a lootbox
class LootboxBuyRequest(SQLModel):
    telegram_user_id: int

class LootboxBuyResponse(SQLModel):
    success: bool
    message: str
    reward_description: Optional[str] = None
    updated_user_status: Optional[UserRead] = None