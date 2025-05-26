from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.api_routes import router as api_router  # Import the router from api_routes.py

# Create the FastAPI app instance
app = FastAPI(title="Telegram Bot Backend API")

# Include the API routes defined in api_routes.py
app.include_router(api_router, prefix="/api")  # Prefix all these routes with /api

app.mount("/", StaticFiles(directory="static/webapp/dist", html=True), name="static")

# Add other middleware, configurations etc. here if needed

# To run the app (from the terminal in the telegram_bot_backend directory):
# uvicorn main:app --reload
