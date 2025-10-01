# ServiceNow + FastAPI (OpenRouter) Backend

Production-ready FastAPI backend that generates **Incident Summary**, **Work Notes**, and **Resolution Note**
using **OpenRouter** (OpenAI-compatible) models. Designed to be called from ServiceNow via an Outbound REST Message
(or any client).

## Features
- FastAPI with typed request/response models (Pydantic v2)
- Clean service layer for OpenRouter chat completions
- JSON Schema enforcement for Summary output (where the model supports it)
- CORS enabled & env-based config
- Dockerfile + `uvicorn` ready
- Minimal tests

## Endpoints
- `POST /api/v1/ai/summarize-incident` → returns `{ "summary": "..." , "key_facts": [...] }`
- `POST /api/v1/ai/work-notes` → returns plain text work notes
- `POST /api/v1/ai/resolution-note` → returns plain text resolution/close notes

## Quickstart

### 1) Configure
Create `.env` from example:
```bash
cp .env.example .env
# edit with your OpenRouter API key (no 'Bearer ' prefix)
```

### 2) Run locally
```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### 3) Docker
```bash
docker build -t sn-fastapi-openrouter .
docker run -p 8080:8080 --env-file .env sn-fastapi-openrouter
```

### 4) Test it
```bash
curl -X POST http://localhost:8080/api/v1/ai/summarize-incident \
  -H "Content-Type: application/json" -d '{
    "number":"INC0012345",
    "short_description":"Email outage for APAC",
    "description":"Users report IMAP timeouts since 09:30 IST",
    "latest_comments":[
      "Rebooted mx-apac-01. No change.",
      "Traffic spike observed on edge firewall.",
      "Failover to mx-apac-02 planned."
    ]
  }'
```

## ServiceNow wiring (Outbound REST Message)
- **Endpoint:** `http://<your-host>:8080/api/v1/ai/summarize-incident` (adjust for each endpoint)
- **Method:** POST
- **Headers:** `Content-Type: application/json`
- **Body (Summarize) Example:**
```json
{
  "number": "${number}",
  "short_description": "${short_description}",
  "description": "${description}",
  "latest_comments": ["${comment1}", "${comment2}", "${comment3}"]
}
```

## Notes
- Keep prompts factual, no PII, no hallucinations.
- Set `AI_MODEL` in `.env` (default: `openai/gpt-4o-mini`).
