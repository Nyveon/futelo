from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import load, create_user
from utils import current_level
from config import LEVELS, MIN_MESSAGES_FOR_LEVEL
from private_info import FRONTEND_URL

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_URL])

@app.get("/stats")
async def stats(user_id:int):
    user = load(user_id)
    if not user:
        user = create_user(user_id)
    
    user_level = current_level(user.messages_sent)

    if user_level == LEVELS - 1:
        next_level = 0
    else:
        next_level = MIN_MESSAGES_FOR_LEVEL[user_level+1] - user.messages_sent

    return {
        "messages_sent": user.messages_sent,
        "letter_limits_list": user.letter_limits_list,
        "current_level": user_level,
        "messages_next_level": next_level,
    }