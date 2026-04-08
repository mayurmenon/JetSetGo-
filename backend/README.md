# TinyFish Multi-Agent Scraping Backend

FastAPI backend for multi-agent web scraping with AG2 + TinyFish, including SSE progress streaming.

## 1) Setup

From the project root:

```bash
cd backend
python -m venv .venv
```

### Windows (PowerShell)

```bash
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS/Linux

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) API Keys

You need:

- `OPENAI_API_KEY`
- `TINYFISH_API_KEY`

How to get them:

- OpenAI key: create/manage keys in your OpenAI dashboard.
- TinyFish key: generate an API key from your TinyFish account/dashboard.

Create a `.env` file in `backend/`:

```env
OPENAI_API_KEY=your_openai_api_key_here
TINYFISH_API_KEY=your_tinyfish_api_key_here
LOG_LEVEL=INFO
```

You can copy from `.env.example` and replace values.

## 3) Run the Server

From `backend/`:

```bash
uvicorn main:app --reload --port 8000
```

Base URL:

- `http://127.0.0.1:8000`

API routes use `/api` prefix.

## 4) Test Endpoints (curl)

### Health check

```bash
curl http://127.0.0.1:8000/api/health
```

### Start scrape job

```bash
curl -X POST http://127.0.0.1:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://example.com\",\"research_goal\":\"Extract company overview and contact details\",\"specialist_types\":[\"GeneralExtractor\",\"ContactInfoSpecialist\"]}"
```

Example response:

```json
{"job_id":"<job-id>","status":"accepted","result":null}
```

### Stream progress (SSE)

Use the returned `job_id`:

```bash
curl -N http://127.0.0.1:8000/api/scrape/<job-id>/stream
```

Each event is sent as:

```text
data: {"agent_name":"SeedCrawler","status":"running","message":"Starting seed crawl."}
```

### Get final result

```bash
curl http://127.0.0.1:8000/api/scrape/<job-id>/result
```

## Notes

- The app uses in-memory job storage; restart clears all jobs.
- Logging is configured in `app/core/config.py` and includes agent lifecycle + API call logging.
