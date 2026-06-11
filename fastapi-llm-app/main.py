import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(
    title="ChatOps Incident Triage Bot",
    description="AI-assisted incident triage and RCA drafting",
    version="0.1.0",
)

APP_DIR = Path(__file__).resolve().parent
DEFAULT_INCIDENTS_FILE = APP_DIR / "incidents.json"


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


class IncidentRequest(BaseModel):
    """Body for /triage and /rca - just the incident ID."""

    incident_id: str


@app.get("/")
def health() -> Dict[str, str]:
    return {"status": "ok", "message": "ChatOps Incident Triage Bot is running"}


@app.get("/health")
def health_alias() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/providers")
def providers() -> Dict[str, List[str]]:
    return {"providers": ["openai", "huggingface"]}


def _incidents_file_path() -> Path:
    configured_path = os.getenv("INCIDENTS_FILE")
    if configured_path:
        return Path(configured_path).expanduser().resolve()

    return DEFAULT_INCIDENTS_FILE


def _load_incidents() -> List[Dict[str, Any]]:
    incidents_file = _incidents_file_path()
    if not incidents_file.is_file():
        raise HTTPException(
            status_code=500,
            detail=(
                f"Incidents file not found: {incidents_file}. "
                "Create fastapi-llm-app/incidents.json or set INCIDENTS_FILE."
            ),
        )

    try:
        with incidents_file.open(encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Incidents file contains invalid JSON: {incidents_file}",
        ) from exc

    if isinstance(data, dict) and isinstance(data.get("incidents"), list):
        data = data["incidents"]

    if not isinstance(data, list):
        raise HTTPException(
            status_code=500,
            detail="Incidents file must be a JSON array or an object with an 'incidents' array.",
        )

    return data


def _find_incident(incident_id: str) -> Dict[str, Any]:
    requested_id = incident_id.strip()
    for incident in _load_incidents():
        if str(incident.get("incident_id") or incident.get("id")) == requested_id:
            return incident

    raise HTTPException(
        status_code=404,
        detail=f"Incident not found: {requested_id}",
    )


def _incident_text(incident: Dict[str, Any]) -> str:
    return json.dumps(incident, indent=2, sort_keys=True)


def _generate_claude_json(prompt: str) -> Dict[str, Any]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="ANTHROPIC_API_KEY is not configured.",
        )

    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="anthropic package is missing. Install dependencies from requirements.txt.",
        ) from exc

    model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=0.2,
        system="Return only valid JSON. Do not wrap the response in markdown.",
        messages=[{"role": "user", "content": prompt}],
    )

    text = "".join(
        block.text for block in message.content if getattr(block, "type", None) == "text"
    )
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail="Claude returned a response that was not valid JSON.",
        ) from exc


@app.post("/triage")
def triage(req: IncidentRequest) -> Dict[str, Any]:
    """Triage an incident using Claude."""

    incident = _find_incident(req.incident_id)
    prompt = (
        "Classify this incident for ChatOps triage. Return JSON with keys: "
        "severity, category, assigned_team, suggested_action_items.\n\n"
        f"Incident:\n{_incident_text(incident)}"
    )
    return _generate_claude_json(prompt)


@app.post("/rca")
def rca(req: IncidentRequest) -> Dict[str, Any]:
    """Draft a root-cause analysis (RCA) for an incident using Claude."""

    incident = _find_incident(req.incident_id)
    prompt = (
        "Draft a root-cause analysis for this incident. Return JSON with keys: "
        "summary, impact, timeline, root_cause, contributing_factors, "
        "corrective_actions, prevention_plan.\n\n"
        f"Incident:\n{_incident_text(incident)}"
    )
    return _generate_claude_json(prompt)


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
