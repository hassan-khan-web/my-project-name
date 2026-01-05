from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
import redis.asyncio as redis
from app.utils import build_profile

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
# Accept multiple resume paths via comma-separated env var, or default to both files
RESUME_PATHS = os.getenv("RESUME_PATHS", "Hassan_Khan_resume.docx,Resume.docx")
CACHE_KEY = "resume_content"

redis_client = None


@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    try:
        await redis_client.ping()
    except Exception:
        pass


async def get_resume():
    if redis_client:
        try:
            cached = await redis_client.get(CACHE_KEY)
            if cached:
                return json.loads(cached)
        except Exception:
            pass

    # Build list of paths, ignore empty entries
    paths = [p.strip() for p in RESUME_PATHS.split(",") if p.strip()]
    existing = [p for p in paths if os.path.exists(p)]
    if not existing:
        existing = paths

    data = build_profile(existing)

    if redis_client:
        try:
            await redis_client.set(CACHE_KEY, json.dumps(data), ex=300)
        except Exception:
            pass
    return data


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = await get_resume()
    # choose photo if available in static, otherwise use placeholder
    local_photo_path = os.path.join(os.getcwd(), "static", "photo.jpg")
    if os.path.exists(local_photo_path):
        photo_url = "/static/photo.jpg"
    else:
        photo_url = "https://via.placeholder.com/160"

    return templates.TemplateResponse(
        "portfolio.html", {"request": request, "resume": data, "photo_url": photo_url}
    )


@app.get("/api/resume")
async def api_resume():
    return await get_resume()
