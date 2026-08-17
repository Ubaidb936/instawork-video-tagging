# Instawork Video Tagging

A full-stack app that auto-tags workplace training videos using AI. Upload a video, get back a description and searchable tags powered by GPT-4o or Gemini.

## Stack

- **Backend** — FastAPI + PostgreSQL (pgvector) + SQLAlchemy
- **Frontend** — React (Vite)
- **AI** — OpenAI GPT-4o or Google Gemini 3.6 Flash
- **Infra** — Docker Compose

## How to Run

1. Copy and fill in env vars:
   ```bash
   cp backend/.env.example backend/.env
   ```
   Set `OPENAI_API_KEY` and/or `GEMINI_API_KEY` in `backend/.env`.

2. Start everything:
   ```bash
   docker compose up --build
   ```

3. Open the app at `http://localhost:5173`

## API

- `POST /videos` — upload a video (form: `file`, `tagger=gpt4o|gemini`)
- `GET /videos/{id}` — get video status + tags
- `GET /videos/{id}/stream` — stream the video file
- `GET /search?q=...` — semantic search across tagged videos
