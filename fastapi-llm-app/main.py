from datetime import datetime
import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="LLM Utility API")


# --- Models ---
class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 100


class SentimentRequest(BaseModel):
    text: str


# --- Endpoints ---
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/summarize")
async def summarize(request: SummarizeRequest):
    # logic for LLM call goes here
    # Use prompt variations discussed below
    return {"summary": "..."}


@app.post("/analyze-sentiment")
async def analyze_sentiment(request: SentimentRequest):
    # logic for LLM call goes here
    return {
        "sentiment": "positive",
        "confidence_score": 0.98,
        "explanation": "...",
    }
