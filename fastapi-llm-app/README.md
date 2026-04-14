# FastAPI LLM App

A minimal FastAPI starter for prompt experiments with:
- OpenAI Chat Completions API
- Hugging Face Inference API

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

3. Add your keys to `.env`:

```env
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

- `GET /` - basic health response
- `GET /providers` - supported LLM providers
- `POST /generate` - generate text from a prompt

Example request:

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

