import base64
import json
import os
import openai
from app.services.taggers.base import BaseTagger, TagResult
from app.utils.video import extract_frames, extract_audio

TAGGING_PROMPT = """You are analyzing a workplace training or demonstration video for Instawork,
a staffing platform connecting businesses (restaurants, warehouses, events) with workers.

You will be shown frames from the video in sequence, along with an audio transcript if available.

Return a JSON object with exactly two fields:

1. "description": A rich 2-4 sentence natural language description of what is happening in the video.
   Capture the full context — what tasks are being performed, what equipment is used, what skills
   are demonstrated, what the environment looks like, and any safety practices shown.

2. "tags": A flat array of lowercase short labels for filtering.
   Focus on job tasks, skills, tools/equipment, industry, and environment.

Example output:
{
  "description": "A kitchen worker demonstrates proper deep frying technique in a commercial kitchen. They heat oil to 350°F in a deep fryer, carefully lower breaded chicken pieces to avoid splatter, and monitor cooking time for food safety. The video emphasizes oil temperature control and safe handling of hot equipment.",
  "tags": ["frying", "deep fryer", "kitchen", "food safety", "oil temperature", "food prep", "food service"]
}

Return ONLY the JSON object. No extra text."""


class GPT4oFrameTagger(BaseTagger):
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def tag(self, video_path: str) -> TagResult:
        frames = extract_frames(video_path, num_frames=8)
        transcript = self._transcribe(video_path)

        content = []
        if transcript:
            content.append({
                "type": "text",
                "text": f"Audio transcript:\n\"{transcript}\"\n\nFrames from the video:"
            })
        for frame_path in frames:
            with open(frame_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "low"}
            })
        content.append({"type": "text", "text": TAGGING_PROMPT})

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": content}],
            max_tokens=600,
        )
        return self._parse(response.choices[0].message.content.strip())

    def _transcribe(self, video_path: str) -> str:
        try:
            audio_path = extract_audio(video_path)
            with open(audio_path, "rb") as f:
                result = self.client.audio.transcriptions.create(model="whisper-1", file=f)
            return result.text
        except Exception:
            return ""

    def _parse(self, raw: str) -> TagResult:
        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            data = json.loads(raw[start:end])
            return TagResult(description=data["description"], tags=data["tags"])
        except Exception:
            return TagResult(description=raw, tags=[])
