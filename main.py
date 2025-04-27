from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# from database import engine # Import engine if needed elsewhere
# from api_routes import router as api_router # Import the router from api_routes.py

# Create the FastAPI app instance
app = FastAPI(title="Telegram Bot Backend API")

templates = Jinja2Templates(directory="templates")

# Include the API routes defined in api_routes.py
# app.include_router(api_router, prefix="/api") # Prefix all these routes with /api

# Basic root endpoint
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )
# Add other middleware, configurations etc. here if needed

# To run the app (from the terminal in the telegram_bot_backend directory):
# uvicorn main:app --reload