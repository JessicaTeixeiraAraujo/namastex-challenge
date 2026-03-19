import json
import os
from typing import Dict, List

import requests

BASE_URL = os.getenv("TRIAGE_BASE_URL", "http://localhost:8080")
WEBHOOK_URL = f"{BASE_URL.rstrip('/')}/omni/webhook"

TEST_CASES: List[Dict[str, str]] = [
    {
        "conversation_id": "demo-open-ticket",
        "text": "I want an exception to work remotely for 5 days",
        "expected": "OPEN_TICKET",
    },
    {
        "conversation_id": "demo-request-information",
        "text": "I need help with a policy",
        "expected": "REQUEST_INFORMATION",
    },
    {
        "conversation_id": "demo-high-scalable",
        "text": "How does the food policy work when traveling?",
        "expected": "HIGH_SCALABLE",
    },
]


def build_payload(conversation_id: str, text: str) -> Dict[str, object]:
    return {
        "conversation_id": conversation_id,
        "channel": "whatsapp",
        "from": "+5511999999999",
        "text": text,
        "timestamp": "2026-03-19T10:30:00Z",
        "metadata": {
            "customer_id": "cust-42",
            "locale": "pt-BR",
        },
    }


def main() -> None:
    print(f"Running evidence tests against {WEBHOOK_URL}")
    summary = []

    for case in TEST_CASES:
        payload = build_payload(case["conversation_id"], case["text"])
        response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        reply = data.get("reply", {})
        tags = reply.get("tags", [])
        passed = case["expected"].lower() in tags

        print("-" * 80)
        print(f"Conversation: {case['conversation_id']}")
        print(f"Input:        {case['text']}")
        print(f"Expected tag: {case['expected'].lower()}")
        print(f"Reply:        {reply.get('reply', '')}")
        print(f"Handoff:      {reply.get('handoff', False)}")
        print(f"Tags:         {tags}")
        print(f"Passed:       {passed}")

        summary.append(
            {
                "conversation_id": case["conversation_id"],
                "expected": case["expected"],
                "passed": passed,
                "reply": reply,
            }
        )

    print("=" * 80)
    print(json.dumps({"base_url": BASE_URL, "results": summary}, indent=2))


if __name__ == "__main__":
    main()
