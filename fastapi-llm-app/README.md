# FastAPI LLM App

A minimal FastAPI starter for utility tasks powered by the OpenAI Chat Completions API.

## Project Structure

```text
fastapi-llm-app/
├── main.py              # Application entry point
├── requirements.txt     # Dependencies (FastAPI, Uvicorn, OpenAI/HuggingFace)
├── .env                 # API Keys (do not commit to GitHub)
├── .python-version      # For Render (e.g., 3.11.0)
└── README.md            # Prompt experiment documentation
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

3. Add your key to `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

4. Run the app:

```bash
uvicorn main:app --reload --port 8000
```

## Endpoints

- `GET /health` - API health and UTC timestamp
- `POST /summarize` - summarize input text
- `POST /analyze-sentiment` - return sentiment, confidence score, and explanation

### Example: Summarize

```bash
curl -X POST "http://127.0.0.1:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "FastAPI is a modern web framework for building APIs with Python.",
    "max_length": 80
  }'
```

### Example: Analyze Sentiment

```bash
curl -X POST "http://127.0.0.1:8000/analyze-sentiment" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I love how fast and easy this API is to use."
  }'
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
| YYYY-MM-DD | openai | gpt-4o-mini | "Summarize this..." | max_length=100 | "..." | "..." |

