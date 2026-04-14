import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(
    title="FastAPI LLM App",
    description="A lightweight FastAPI starter for prompt experiments.",
    version="0.1.0",
)


class PromptRequest(BaseModel):
    prompt: str = Field(..., description="The prompt text to send to the model.")
    provider: str = Field(
        default_factory=lambda: os.getenv("LLM_PROVIDER", "openai"),
        description="LLM provider to use: 'openai' or 'huggingface'.",
    )
    model: Optional[str] = Field(
        default=None,
        description="Optional model name override for the selected provider.",
    )
    max_tokens: int = Field(default=300, ge=1, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class PromptResponse(BaseModel):
    provider: str
    model: str
    output: str
    raw: Dict[str, Any]


@app.get("/")
def health() -> Dict[str, str]:
    return {"status": "ok", "message": "FastAPI LLM App is running"}


@app.get("/health")
def health_alias() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/providers")
def providers() -> Dict[str, List[str]]:
    return {"providers": ["openai", "huggingface"]}


def _generate_openai(req: PromptRequest) -> PromptResponse:
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

    model = req.model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": req.prompt}],
        temperature=req.temperature,
        max_tokens=req.max_tokens,
    )

    output = completion.choices[0].message.content or ""
    return PromptResponse(
        provider="openai",
        model=model,
        output=output,
        raw=completion.model_dump(),
    )


def _generate_huggingface(req: PromptRequest) -> PromptResponse:
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400, detail="HUGGINGFACE_API_KEY is not configured."
        )

    try:
        from huggingface_hub import InferenceClient
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="huggingface_hub package is missing. Install dependencies from requirements.txt.",
        ) from exc

    model = req.model or os.getenv("HUGGINGFACE_MODEL", "HuggingFaceH4/zephyr-7b-beta")
    client = InferenceClient(model=model, token=api_key)

    generated = client.text_generation(
        prompt=req.prompt,
        max_new_tokens=req.max_tokens,
        temperature=req.temperature,
    )

    return PromptResponse(
        provider="huggingface",
        model=model,
        output=generated,
        raw={"text_generation": generated},
    )


@app.post("/generate", response_model=PromptResponse)
def generate(req: PromptRequest) -> PromptResponse:
    provider = req.provider.lower().strip()

    if provider == "openai":
        return _generate_openai(req)
    if provider == "huggingface":
        return _generate_huggingface(req)

    raise HTTPException(
        status_code=400,
        detail="Unsupported provider. Use 'openai' or 'huggingface'.",
    )
