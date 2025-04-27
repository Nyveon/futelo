import os
from sqlmodel import SQLModel, create_engine, Session, Field
from typing import Optional, Dict, Any
import json

# Define the database URL
DATABASE_FILE = "bot_database.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# Create the database engine.
# connect_args is specific to SQLite to allow same thread usage, useful for simple scripts/FastAPI.
# For production with more complex async needs, consider asyncpg/aiosqlite engines.
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

# Dependency function to get a database session for FastAPI routes
def get_session():
    with Session(engine) as session:
        yield session

# Helper to generate default limits
def get_default_limits() -> str:
    limits = {chr(ord('A') + i): 0 for i in range(26)} # A-Z limit 7
    limits['9'] = 0 # For numbers, if needed
    limits['Ñ'] = 0
    limits['*'] = 0 # For special characters

    limits['H'] = 1
    limits['O'] = 1
    limits['L'] = 1
    limits['A'] = 1

    return json.dumps(limits)