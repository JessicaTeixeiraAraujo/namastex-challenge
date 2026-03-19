import json
from typing import Any, Dict

import requests

from .config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, OPENAI_TIMEOUT_SECONDS
from .models import ScreeningOut
from .triage import decision_manager


class OpenAIError(RuntimeError):
    pass


SCREENING_PROMPT = (
    "You are a service desk triage agent for internal policies at Lanx Capital. "
    "Given the users message, return ONLY a JSON with:\n"
    "{\n"
    '  "decision": "HIGH_SCALABLE" | "REQUEST_INFORMATION" | "OPEN_TICKET",\n'
    '  "urgency": "LOW" | "MEDIUM" | "HIGH",\n'
    '  "missing_fields": ["..."]\n'
    "}\n"
    "Rules\n"
    ' - "HIGH_SCALABLE": Objective and clear questions about rules or procedures described in the policies.\n'
    ' - "REQUEST_INFORMATION": User message that is vague or lacks information to identify the topic or context.\n'
    ' - "OPEN_TICKET": Requests for exception, release, approval, or special access.\n'
    "Analyze the message and decide on the most appropriate action."
)


def screen_with_openai(question: str) -> ScreeningOut:
    if not OPENAI_API_KEY:
        raise OpenAIError("OPENAI_API_KEY not configured")

    url = f"{OPENAI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    body: Dict[str, Any] = {
        "model": OPENAI_MODEL,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SCREENING_PROMPT},
            {"role": "user", "content": question},
        ],
        "response_format": {"type": "json_object"},
    }

    response = requests.post(url, headers=headers, json=body, timeout=OPENAI_TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()

    try:
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return ScreeningOut(**parsed)
    except Exception as exc:
        raise OpenAIError(f"invalid OpenAI screening response: {exc}") from exc


def run_openai_triage(question: str) -> Dict[str, Any]:
    screening = screen_with_openai(question)
    result = decision_manager(question, screening)
    result["screening"] = screening.model_dump()
    return result
