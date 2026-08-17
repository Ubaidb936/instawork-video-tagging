import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

from app.database import engine, init_db
from app.utils.models import Base
from app.routes import videos, search

init_db()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Instawork Video Tagging API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(videos.router)
app.include_router(search.router)


@app.get("/health")
def health():
    return {"status": "ok"}
