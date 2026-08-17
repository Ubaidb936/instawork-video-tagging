import logging
import os
import shutil
import tempfile
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.utils.models import Video
from app.utils.schemas import VideoResponse
from app.services.pipeline import run_pipeline_from_path

logger = logging.getLogger(__name__)

UPLOADS_DIR = "/app/uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("", response_model=VideoResponse, status_code=200)
async def ingest_video(
    file: UploadFile = File(...),
    tagger: str = Form("gpt4o"),
    db: Session = Depends(get_db),
):
    logger.info("Ingest request — filename=%s tagger=%s size=%s", file.filename, tagger, file.size)

    suffix = os.path.splitext(file.filename)[1] or ".mp4"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    video = Video(url=file.filename, status="processing", tagger=tagger)
    db.add(video)
    db.commit()
    db.refresh(video)
    logger.info("Video record created — id=%s", video.id)

    permanent_path = os.path.join(UPLOADS_DIR, f"{video.id}{suffix}")
    shutil.move(tmp_path, permanent_path)

    video.file_path = permanent_path
    db.commit()

    run_pipeline_from_path(video.id, permanent_path, SessionLocal, tagger=tagger)

    db.refresh(video)
    logger.info("Ingest complete — id=%s status=%s", video.id, video.status)
    return VideoResponse.from_orm(video)


@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoResponse.from_orm(video)


@router.get("/{video_id}/stream")
def stream_video(video_id: int, db: Session = Depends(get_db)):
    logger.info("Stream request — video_id=%s", video_id)
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or not video.file_path or not os.path.exists(video.file_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    return FileResponse(video.file_path, media_type="video/mp4")
