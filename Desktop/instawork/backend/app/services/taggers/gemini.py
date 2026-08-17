import json
import os
import google.genai as genai
from google.genai import types
from app.services.taggers.base import BaseTagger, TagResult

TAGGING_PROMPT = """You are analyzing a workplace training or demonstration video for Instawork,
a staffing platform connecting businesses (restaurants, warehouses, events) with workers.

Watch the full video including audio/narration.

Return a JSON object with exactly two fields:

1. "description": A rich 2-4 sentence natural language description of what is happening in the video.
   Capture the full context — what tasks are being performed, what equipment is used, what skills
   are demonstrated, what the environment looks like, and any safety practices shown.

2. "tags": A flat array of lowercase short labels for filtering.
   Focus on job tasks, skills, tools/equipment, industry, and environment.

Example output:
{
  "description": "A kitchen worker demonstrates proper deep frying technique in a commercial kitchen. They heat oil to 350°F in a deep fryer, carefully lower breaded chicken pieces to avoid splatter, and monitor cooking time for food safety.",
  "tags": ["frying", "deep fryer", "kitchen", "food safety", "oil temperature", "food service"]
}

Return ONLY the JSON object. No extra text."""


class GeminiVideoTagger(BaseTagger):
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def tag(self, video_path: str) -> TagResult:
        with open(video_path, "rb") as f:
            video_bytes = f.read()

        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                types.Part.from_bytes(data=video_bytes, mime_type="video/mp4"),
                TAGGING_PROMPT,
            ],
        )
        return self._parse(response.text.strip())

    def _parse(self, raw: str) -> TagResult:
        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            data = json.loads(raw[start:end])
            return TagResult(description=data["description"], tags=data["tags"])
        except Exception:
            return TagResult(description=raw, tags=[])
