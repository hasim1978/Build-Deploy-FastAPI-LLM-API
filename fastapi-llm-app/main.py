"""Simple FastAPI app with placeholder LLM call hooks."""

import os
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Simple LLM API", version="0.1.0")


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Prompt text to send to the LLM.")
    provider: str = Field(
        default_factory=lambda: os.getenv("LLM_PROVIDER", "openai"),
        description="LLM provider: 'openai' or 'anthropic'.",
    )
    model: Optional[str] = Field(
        default=None, description="Optional model override for the selected provider."
    )


class GenerateResponse(BaseModel):
    provider: str
    model: str
    output: str


def call_openai(prompt: str, model: str) -> str:
    """
    Placeholder for an OpenAI API call.
    Replace this body with your OpenAI SDK integration.
    """
    # Example shape:
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # response = client.chat.completions.create(
    #     model=model,
    #     messages=[{"role": "user", "content": prompt}],
    # )
    # return response.choices[0].message.content or ""
    return f"[openai placeholder] model={model} prompt={prompt}"


def call_anthropic(prompt: str, model: str) -> str:
    """
    Placeholder for an Anthropic API call.
    Replace this body with your Anthropic SDK integration.
    """
    # Example shape:
    # client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    # response = client.messages.create(
    #     model=model,
    #     max_tokens=300,
    #     messages=[{"role": "user", "content": prompt}],
    # )
    # return response.content[0].text
    return f"[anthropic placeholder] model={model} prompt={prompt}"


@app.get("/")
def health() -> Dict[str, str]:
    return {"status": "ok", "message": "Simple LLM API is running"}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    provider = req.provider.lower().strip()

    if provider == "openai":
        model = req.model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        output = call_openai(req.prompt, model)
        return GenerateResponse(provider=provider, model=model, output=output)

    if provider == "anthropic":
        model = req.model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
        output = call_anthropic(req.prompt, model)
        return GenerateResponse(provider=provider, model=model, output=output)

    raise HTTPException(
        status_code=400,
        detail="Unsupported provider. Use 'openai' or 'anthropic'.",
    )
