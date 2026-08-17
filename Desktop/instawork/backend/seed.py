"""
Pre-ingest all 10 Instawork sample videos.
Run once before the demo: python seed.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.database import engine, Base, SessionLocal
from app.models import Video
from app.services.pipeline import run_pipeline

Base.metadata.create_all(bind=engine)

BASE_URL = "https://raw.githubusercontent.com/Instawork/video-data/main"
VIDEO_COUNT = 10


def seed():
    db = SessionLocal()
    try:
        existing = db.query(Video).count()
        if existing > 0:
            print(f"DB already has {existing} videos. Skipping seed.")
            return

        print(f"Seeding {VIDEO_COUNT} videos...")
        for i in range(1, VIDEO_COUNT + 1):
            url = f"{BASE_URL}/{i}.mp4"
            video = Video(url=url, status="processing")
            db.add(video)
            db.commit()
            db.refresh(video)
            print(f"[{i}/{VIDEO_COUNT}] Queued video id={video.id} — {url}")
            run_pipeline(video.id, url, SessionLocal)
            v = db.query(Video).filter(Video.id == video.id).first()
            db.refresh(v)
            print(f"         status={v.status} tags={v.tags}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
