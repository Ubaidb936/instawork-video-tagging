import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.agents.search_agent import SearchAgent
from app.utils.schemas import VideoResponse, SearchResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search_videos(
    q: str = Query(..., description="Natural language search query"),
    db: Session = Depends(get_db),
):
    logger.info("Search request — query=%r", q)
    agent = SearchAgent()
    results, analysis = agent.run(query=q, db=db)
    logger.info("Search complete — query=%r rewritten=%r results=%d", q, analysis.rewritten_query, len(results))

    return SearchResponse(
        results=[VideoResponse.from_orm(v) for v in results],
        total=len(results),
        rewritten_query=analysis.rewritten_query,
        extracted_tags=analysis.tags,
    )
