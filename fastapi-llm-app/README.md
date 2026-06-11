# ChatOps Incident Triage Bot

AI-assisted incident triage and root-cause analysis (RCA) drafting with Claude.
The app also keeps the starter `/generate` endpoint for OpenAI and Hugging Face
prompt experiments.

## Project Structure

```text
fastapi-llm-app/
├── incidents.json       # Sample incidents used by /triage and /rca
├── main.py              # Application entry point
├── requirements.txt     # Dependencies (FastAPI, Uvicorn, Anthropic, OpenAI/HuggingFace)
├── .env                 # API Keys (do not commit to GitHub)
├── .python-version      # For Render (e.g., 3.11.0)
└── README.md            # ChatOps bot documentation
```

## Quick Start

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your keys to `.env`:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_token_here
OPENAI_MODEL=gpt-4o-mini
HUGGINGFACE_MODEL=HuggingFaceH4/zephyr-7b-beta
```

4. Run the app:

```bash
uvicorn main:app --reload --port 8000
```

## Endpoints

- `GET /health` - basic health response
- `POST /triage` - classify an incident and suggest action items
- `POST /rca` - draft a structured root-cause analysis
- `GET /providers` - supported LLM providers
- `POST /generate` - generate text from a prompt with OpenAI or Hugging Face

Example triage request:

```bash
curl -X POST "http://127.0.0.1:8000/triage" \
  -H "Content-Type: application/json" \
  -d '{"incident_id": "INC001"}'
```

Example prompt request:

```bash
curl -X POST "http://127.0.0.1:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain FastAPI in two sentences.",
    "provider": "openai",
    "temperature": 0.7,
    "max_tokens": 200
  }'
```

## Incident Data

By default, `/triage` and `/rca` read incidents from `incidents.json` next to
`main.py`. This avoids absolute local paths such as
`C:\Users\...\chatops-incident-bot\incidents.json`, which break when the app is
started from another machine or working directory.

To use a different file, set `INCIDENTS_FILE`:

```env
INCIDENTS_FILE=/absolute/path/to/incidents.json
```

## Render Notes

- `.python-version` pins Python for deployment.
- Configure environment variables in the Render dashboard.
- Suggested start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Prompt Experiment Log

Use this table to track and compare prompt tests:

| Date | Provider | Model | Prompt | Settings | Result | Notes |
|------|----------|-------|--------|----------|--------|-------|
| YYYY-MM-DD | openai | gpt-4o-mini | "..." | temp=0.7,max_tokens=200 | "..." | "..." |

