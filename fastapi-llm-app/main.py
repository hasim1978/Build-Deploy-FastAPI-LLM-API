import json
import os
from datetime import datetime
from typing import Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError

load_dotenv()

app = FastAPI(title="LLM Utility API")


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Input text to summarize.")
    max_length: int = Field(default=100, ge=20, le=1000)


class SummaryResponse(BaseModel):
    summary: str
    model: str


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Input text to analyze.")


class SentimentResponse(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    model: str


def _openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not configured.")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="openai package is missing. Install dependencies from requirements.txt.",
        ) from exc

    return OpenAI(api_key=api_key)


def _model_name() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/summarize", response_model=SummaryResponse)
async def summarize(request: SummarizeRequest) -> SummaryResponse:
    client = _openai_client()
    model = _model_name()

    prompt = (
        "You are a concise summarization assistant.\n"
        f"Summarize the following text in no more than {request.max_length} words.\n"
        "Keep the summary factual and readable.\n\n"
        f"Text:\n{request.text}"
    )

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You produce concise, faithful summaries.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=300,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI request failed: {exc}") from exc

    summary_text = (completion.choices[0].message.content or "").strip()
    if not summary_text:
        raise HTTPException(status_code=502, detail="OpenAI returned an empty summary.")

    return SummaryResponse(summary=summary_text, model=model)


@app.post("/analyze-sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest) -> SentimentResponse:
    client = _openai_client()
    model = _model_name()

    prompt = (
        "Analyze the sentiment of the user text.\n"
        "Return ONLY valid JSON with this schema:\n"
        '{'
        '"sentiment":"positive|negative|neutral",'
        '"confidence_score":0.0,'
        '"explanation":"brief explanation"'
        '}\n\n'
        f"Text:\n{request.text}"
    )

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise sentiment analysis assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
            max_tokens=200,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI request failed: {exc}") from exc

    raw_content = (completion.choices[0].message.content or "").strip()
    if not raw_content:
        raise HTTPException(status_code=502, detail="OpenAI returned empty sentiment data.")

    try:
        parsed = json.loads(raw_content)
        sentiment = SentimentResponse.model_validate({**parsed, "model": model})
    except (json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to parse sentiment response from OpenAI: {exc}",
        ) from exc

    return sentiment
