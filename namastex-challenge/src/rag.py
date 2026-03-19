import json
import os
from typing import Dict, List


DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "policies.json")


def load_policies() -> List[Dict[str, object]]:
    with open(DATA_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def question_policy_rag(question: str) -> Dict[str, object]:
    question_norm = question.lower()
    policies = load_policies()

    for policy in policies:
        keywords = policy.get("keywords", [])
        if any(k in question_norm for k in keywords):
            return {
                "answer": policy.get("answer", ""),
                "quotes": policy.get("quotes", []),
                "context_found": True,
            }

    return {
        "answer": "I could not find a direct policy match. Please clarify the policy name or topic.",
        "quotes": [],
        "context_found": False,
    }
