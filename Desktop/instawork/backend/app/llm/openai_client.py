import json
import os
import openai
from app.llm.base import BaseLLMClient, QueryAnalysis

SYSTEM_PROMPT = """You are a search assistant for Instawork, a staffing platform for restaurants,
warehouses, and events. Users search for workplace training videos.

Given a user search query, return a JSON object with:
1. "rewritten_query": A semantically richer version optimized for embedding-based search.
   Expand abbreviations, add relevant context, use professional terminology.
2. "tags": A list of lowercase tags representing the core intent.
   Focus on job tasks, equipment, industry, and environment.

Examples:
- "frying videos" → { "rewritten_query": "commercial kitchen deep frying technique food preparation cooking oil temperature", "tags": ["frying", "deep fryer", "kitchen", "food prep"] }
- "forklift" → { "rewritten_query": "forklift operation warehouse pallet stacking logistics safety", "tags": ["forklift", "warehouse", "logistics", "pallet"] }

Return ONLY the JSON object."""


class OpenAIClient(BaseLLMClient):
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def analyze_query(self, query: str) -> QueryAnalysis:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            max_tokens=200,
        )
        raw = response.choices[0].message.content.strip()
        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            data = json.loads(raw[start:end])
            return QueryAnalysis(
                rewritten_query=data.get("rewritten_query", query),
                tags=data.get("tags", []),
            )
        except Exception:
            return QueryAnalysis(rewritten_query=query, tags=[])
