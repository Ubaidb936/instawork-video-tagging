import logging
import os
import openai
from sqlalchemy.orm import Session
from app.tools.base import BaseTool
from app.utils.models import Video

logger = logging.getLogger(__name__)

SEMANTIC_POOL = 20
FINAL_TOP_K = 10
TAG_BOOST_WEIGHT = 0.3
SEMANTIC_WEIGHT = 0.7


class VideoSearchTool(BaseTool):
    name = "video_search"
    description = "Searches the video database using semantic similarity and soft tag boosting."

    def run(self, query: str, soft_tags: list[str], db: Session) -> list[Video]:
        logger.info("Search tool — query=%r soft_tags=%s", query, soft_tags)
        query_embedding = self._embed(query)

        pool = (
            db.query(Video)
            .filter(Video.status == "ready", Video.embedding.isnot(None))
            .order_by(Video.embedding.cosine_distance(query_embedding))
            .limit(SEMANTIC_POOL)
            .all()
        )
        logger.info("Semantic pool size: %d", len(pool))

        if not pool:
            return []

        soft_tags_lower = [t.lower() for t in soft_tags]
        ranked = []
        for i, video in enumerate(pool):
            semantic_score = 1.0 - (i / SEMANTIC_POOL)
            video_tags_lower = [t.lower() for t in video.tags]
            if soft_tags_lower:
                matches = sum(1 for t in soft_tags_lower if t in video_tags_lower)
                tag_score = matches / len(soft_tags_lower)
            else:
                tag_score = 0.0
            combined = SEMANTIC_WEIGHT * semantic_score + TAG_BOOST_WEIGHT * tag_score
            ranked.append((combined, video))

        ranked.sort(key=lambda x: x[0], reverse=True)
        top = [v for _, v in ranked[:FINAL_TOP_K]]
        logger.info("Returning %d results after re-ranking", len(top))
        return top

    def _embed(self, text: str) -> list[float]:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.embeddings.create(input=text, model="text-embedding-3-small")
        return response.data[0].embedding
