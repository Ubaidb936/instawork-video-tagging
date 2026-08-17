import logging
from sqlalchemy.orm import Session
from app.agents.base import BaseAgent
from app.llm.openai_client import OpenAIClient
from app.tools.search_tool import VideoSearchTool

logger = logging.getLogger(__name__)


class SearchAgent(BaseAgent):
    def __init__(self):
        self.llm = OpenAIClient()
        self.search_tool = VideoSearchTool()

    def run(self, query: str, db: Session) -> list:
        logger.info("Agent analyzing query: %r", query)
        analysis = self.llm.analyze_query(query)
        logger.info("Query analysis — rewritten=%r tags=%s", analysis.rewritten_query, analysis.tags)

        results = self.search_tool.run(
            query=analysis.rewritten_query,
            soft_tags=analysis.tags,
            db=db,
        )
        logger.info("Tool returned %d results", len(results))
        return results, analysis
