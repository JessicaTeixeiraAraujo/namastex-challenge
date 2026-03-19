from typing import Dict, List

from .models import ScreeningOut
from .rag import question_policy_rag


SCREENING_PROMPT = (
    "You are a service desk triage agent for internal policies at Lanx Capital. "
    "Given the users message, return ONLY a JSON with:\n"
    "{\n"
    '  "decision": "HIGH_SCALABLE" | "REQUEST_INFORMATION" | "OPEN_TICKET",\n'
    '  "urgency": "LOW" | "MEDIUM" | "HIGH",\n'
    '  "missing_fields": ("..."),\n'
    "}\n"
    "Rules\n"
    ' - "HIGH_SCALABLE": Objective and clear questions about rules or procedures '
    'described in the policies (Ex: "I need a refund for my home office internet"), '
    '(Ex: "How does the food policy work when traveling?")\n'
    ' - "REQUEST_INFORMATION": User message that is vague or lacks information to '
    'identify the topic or context (Ex: "I need help with a policy"), '
    '(Ex: "I have a general question")\n'
    ' - "OPEN_TICKET": Requests for exception, release, approval, or special access. '
    'Or, when the user explicitly requests opening a ticket '
    '(Ex: "I want an exception to work remotely for 5 days")\n'
    "Analyze the message and decide on the most appropriate action."
)


KEYWORDS_OPEN_TICKET = [
    "exception",
    "release",
    "approval",
    "special access",
    "override",
    "authorization",
    "exemption",
    "permit",
    "clearance",
    "waiver",
    "exceptional request",
    "approval needed",
    "access request",
    "release request",
    "exception request",
    "manager approval",
    "special permission",
    "authorization request",
    "temporary access",
    "exception approval",
    "exception case",
    "override request",
    "exception handling",
    "access approval",
    "approval workflow",
    "exception policy",
    "urgent request",
    "special authorization",
    "release approval",
    "manual override",
]


POLICY_KEYWORDS = [
    "policy",
    "compliance",
    "risk",
    "internal controls",
    "anti-money laundering",
    "aml",
    "information security",
    "confidentiality",
    "personal investments",
    "order allotment",
    "training",
    "segregation of activities",
]


def screen_message(message: str) -> ScreeningOut:
    text = message.lower().strip()

    if any(k in text for k in KEYWORDS_OPEN_TICKET):
        urgency = "HIGH" if "urgent" in text else "MEDIUM"
        return ScreeningOut(decision="OPEN_TICKET", urgency=urgency, missing_fields=[])

    if len(text) < 10 or "help" in text or "general" in text:
        return ScreeningOut(
            decision="REQUEST_INFORMATION",
            urgency="LOW",
            missing_fields=["policy topic", "context"],
        )

    if not any(k in text for k in POLICY_KEYWORDS):
        return ScreeningOut(
            decision="REQUEST_INFORMATION",
            urgency="LOW",
            missing_fields=["policy topic"],
        )

    return ScreeningOut(decision="HIGH_SCALABLE", urgency="LOW", missing_fields=[])


def high_scalable_node(question: str) -> Dict[str, object]:
    response_rag = question_policy_rag(question)
    update: Dict[str, object] = {
        "response": response_rag["answer"],
        "quotes": response_rag.get("quotes", []),
        "rag_success": response_rag["context_found"],
    }
    if response_rag["context_found"]:
        update["action_finish"] = "HIGH_SCALABLE"
    return update


def request_information_node(screening: ScreeningOut) -> Dict[str, object]:
    falt = screening.missing_fields
    detail = ", ".join(falt) if falt else "specific theme and context"
    return {
        "response": f"Please provide more information about {detail}.",
        "quotes": [],
        "action_finish": "REQUEST_INFORMATION",
    }


def open_ticket_node(question: str, screening: ScreeningOut) -> Dict[str, object]:
    return {
        "response": (
            f"Open a ticket urgently {screening.urgency}. "
            f"Description: {question[:140]}."
        ),
        "quotes": [],
        "action_finish": "OPEN_TICKET",
    }


def decision_manager(question: str, screening: ScreeningOut) -> Dict[str, object]:
    decision = screening.decision
    if decision == "HIGH_SCALABLE":
        return high_scalable_node(question)
    if decision == "REQUEST_INFORMATION":
        return request_information_node(screening)
    if decision == "OPEN_TICKET":
        return open_ticket_node(question, screening)
    return {
        "response": "Unable to decide. Please clarify your request.",
        "quotes": [],
        "action_finish": "REQUEST_INFORMATION",
    }


def run_triage(question: str) -> Dict[str, object]:
    screening = screen_message(question)
    result = decision_manager(question, screening)
    result["screening"] = screening.model_dump()
    return result

