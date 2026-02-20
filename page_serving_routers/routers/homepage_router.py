import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

# Resolve the path to the templates directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "static", "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/", tags=["Pages"])
async def serve_homepage(request: Request):
    """
    Serves the static homepage HTML page.
    """
    return templates.TemplateResponse("homepage.html", {"request": request})
