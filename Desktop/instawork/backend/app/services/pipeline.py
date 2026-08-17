import logging
import os
import openai
from app.services.taggers.base import BaseTagger
from app.services.taggers.gpt4o import GPT4oFrameTagger
from app.services.taggers.gemini import GeminiVideoTagger

logger = logging.getLogger(__name__)


def get_tagger(choice: str = None) -> BaseTagger:
    choice = (choice or os.getenv("TAGGER", "gpt4o")).lower()
    logger.info("Using tagger: %s", choice)
    if choice == "gemini":
        return GeminiVideoTagger()
    return GPT4oFrameTagger()


def generate_embedding(text: str) -> list[float]:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding


def run_pipeline_from_path(video_id: int, video_path: str, db_session_factory, tagger: str = None):
    from app.utils.models import Video

    logger.info("Pipeline started — video_id=%s tagger=%s path=%s", video_id, tagger or "default", video_path)
    db = db_session_factory()
    try:
        t = get_tagger(tagger)
        result = t.tag(video_path)
        logger.info("Tagging complete — video_id=%s tags=%s", video_id, result.tags)

        embedding = generate_embedding(result.description)
        logger.info("Embedding generated — video_id=%s", video_id)

        video = db.query(Video).filter(Video.id == video_id).first()
        video.description = result.description
        video.tags = result.tags
        video.embedding = embedding
        video.status = "ready"
        db.commit()
        logger.info("Pipeline complete — video_id=%s status=ready", video_id)

    except Exception as e:
        logger.error("Pipeline failed — video_id=%s error=%s", video_id, str(e), exc_info=True)
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = "failed"
            video.error = str(e)
            db.commit()
    finally:
        db.close()
