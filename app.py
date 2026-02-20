from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Brands Out Loud Engine")

# Setup static files and templates
# Mount the static directory
app.mount("/static", StaticFiles(directory="page_serving_routers/static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="page_serving_routers/templates")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Brands Out Loud Engine is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
