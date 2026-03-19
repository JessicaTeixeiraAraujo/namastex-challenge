import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests
from fastapi import FastAPI, HTTPException, Request

from .config import (
    IGNORE_HISTORY_SYNC,
    MAX_MESSAGE_LENGTH,
    GENIE_ENABLED,
    OMNI_API_KEY,
    OMNI_BASE_URL,
    OMNI_INSTANCE_ID,
    OPENAI_FALLBACK_ENABLED,
    SEND_VIA_OMNI,
)
from .logging_utils import log_event, setup_logger
from .models import CanonicalIncoming, CanonicalReply, OmniEvent
from .genie_client import GenieError, send_to_genie, wait_genie_reply
from .openai_client import OpenAIError, run_openai_triage
from .triage import run_triage


app = FastAPI()
logger = setup_logger()

RECENT_EXTERNAL_IDS: Dict[str, float] = {}
RECENT_TTL_SECONDS = 300
RECENT_MAX = 5000


def build_reply_tags(canonical: CanonicalIncoming, result: Dict[str, Any], extra_tags: Optional[list[str]] = None) -> list[str]:
    tags = [canonical.channel, "triage"]
    screening = result.get("screening") if isinstance(result, dict) else None
    if isinstance(screening, dict):
        decision = screening.get("decision")
        if decision:
            tags.append(str(decision).lower())
    action_finish = result.get("action_finish", "") if isinstance(result, dict) else ""
    if action_finish:
        action_tag = str(action_finish).lower()
        if action_tag not in tags:
            tags.append(action_tag)
    for tag in extra_tags or []:
        if tag not in tags:
            tags.append(tag)
    return tags


def _prune_recent(now: float) -> None:
    if len(RECENT_EXTERNAL_IDS) < RECENT_MAX:
        return
    expired = [k for k, v in RECENT_EXTERNAL_IDS.items() if now - v > RECENT_TTL_SECONDS]
    for k in expired:
        RECENT_EXTERNAL_IDS.pop(k, None)


def _is_duplicate(external_id: Optional[str]) -> bool:
    if not external_id:
        return False
    now = time.time()
    _prune_recent(now)
    if external_id in RECENT_EXTERNAL_IDS:
        return True
    RECENT_EXTERNAL_IDS[external_id] = now
    return False


def normalize_payload(payload: Dict[str, Any]) -> CanonicalIncoming:
    if "conversation_id" in payload and "text" in payload:
        return CanonicalIncoming(**payload)

    event = OmniEvent(**payload)
    if event.type != "message.received":
        raise ValueError("Unsupported event type")

    if IGNORE_HISTORY_SYNC and event.metadata.get("ingestMode") == "history-sync":
        raise ValueError("History sync event ignored")

    msg = event.payload
    content = msg.get("content", {}) if isinstance(msg, dict) else {}
    text = content.get("text") or ""
    text = text[:MAX_MESSAGE_LENGTH]

    conversation_id = msg.get("chatId") or event.metadata.get("correlationId") or event.id
    timestamp = datetime.fromtimestamp(event.timestamp / 1000, tz=timezone.utc).isoformat()
    channel = event.metadata.get("channelType") or "whatsapp"
    from_number = msg.get("from") or "unknown"

    return CanonicalIncoming(
        conversation_id=conversation_id,
        channel=channel,
        from_number=from_number,
        text=text,
        timestamp=timestamp,
        metadata={
            "instance_id": event.metadata.get("instanceId"),
            "external_id": msg.get("externalId"),
            "chat_id": msg.get("chatId"),
            "raw": msg.get("rawPayload") if isinstance(msg, dict) else None,
        },
    )


def send_omni_reply(canonical: CanonicalIncoming, reply: CanonicalReply) -> Dict[str, Any]:
    instance_id = canonical.metadata.get("instance_id") or OMNI_INSTANCE_ID
    if not instance_id:
        raise RuntimeError("OMNI_INSTANCE_ID not set and not provided in metadata")

    to_value = canonical.metadata.get("chat_id") or canonical.from_number
    url = f"{OMNI_BASE_URL}/api/v2/messages"
    headers = {"x-api-key": OMNI_API_KEY}
    body = {"instanceId": instance_id, "to": to_value, "text": reply.reply}

    response = requests.post(url, json=body, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()


@app.get("/healthz")
def healthz() -> Dict[str, Any]:
    return {
        "status": "ok",
        "genie_enabled": GENIE_ENABLED,
        "openai_fallback_enabled": OPENAI_FALLBACK_ENABLED,
        "omni_base_url": OMNI_BASE_URL,
    }


@app.post("/omni/webhook")
async def omni_webhook(request: Request) -> Dict[str, Any]:
    payload = await request.json()
    try:
        canonical = normalize_payload(payload)
    except Exception as exc:
        log_event(logger, "WARNING", "payload_invalid", error=str(exc))
        raise HTTPException(status_code=400, detail="invalid payload")

    external_id = canonical.metadata.get("external_id")
    if _is_duplicate(external_id):
        log_event(logger, "INFO", "duplicate_ignored", conversation_id=canonical.conversation_id)
        return {"status": "ignored", "reason": "duplicate"}

    log_event(
        logger,
        "INFO",
        "message_received",
        conversation_id=canonical.conversation_id,
        channel=canonical.channel,
        from_number=canonical.from_number,
    )

    try:
        if GENIE_ENABLED:
            send_to_genie(canonical.model_dump(by_alias=True))
            genie_reply = wait_genie_reply(canonical.conversation_id)
            reply = CanonicalReply(
                conversation_id=genie_reply.get("conversation_id", canonical.conversation_id),
                reply=genie_reply.get("reply", ""),
                handoff=bool(genie_reply.get("handoff", False)),
                tags=list(genie_reply.get("tags", [])),
            )
        else:
            result = run_triage(canonical.text)
            action_finish = result.get("action_finish", "")
            reply = CanonicalReply(
                conversation_id=canonical.conversation_id,
                reply=result["response"],
                handoff=action_finish == "OPEN_TICKET",
                tags=build_reply_tags(canonical, result),
            )
    except GenieError as exc:
        log_event(logger, "ERROR", "genie_failed", conversation_id=canonical.conversation_id, error=str(exc))
        if OPENAI_FALLBACK_ENABLED:
            try:
                result = run_openai_triage(canonical.text)
                action_finish = result.get("action_finish", "")
                reply = CanonicalReply(
                    conversation_id=canonical.conversation_id,
                    reply=result["response"],
                    handoff=action_finish == "OPEN_TICKET",
                    tags=build_reply_tags(canonical, result, ["openai-fallback"]),
                )
            except OpenAIError as openai_exc:
                log_event(
                    logger,
                    "ERROR",
                    "openai_fallback_failed",
                    conversation_id=canonical.conversation_id,
                    error=str(openai_exc),
                )
                reply = CanonicalReply(
                    conversation_id=canonical.conversation_id,
                    reply="Sorry, the Genie orchestrator is unavailable right now. Please try again.",
                    handoff=True,
                    tags=[canonical.channel, "triage", "genie-fallback"],
                )
        else:
            reply = CanonicalReply(
                conversation_id=canonical.conversation_id,
                reply="Sorry, the Genie orchestrator is unavailable right now. Please try again.",
                handoff=True,
                tags=[canonical.channel, "triage", "genie-fallback"],
            )
    except Exception as exc:
        log_event(logger, "ERROR", "triage_failed", conversation_id=canonical.conversation_id, error=str(exc))
        reply = CanonicalReply(
            conversation_id=canonical.conversation_id,
            reply="Sorry, I could not process your request right now. Please try again.",
            handoff=True,
            tags=[canonical.channel, "triage", "fallback"],
        )

    if SEND_VIA_OMNI:
        try:
            response = send_omni_reply(canonical, reply)
            log_event(logger, "INFO", "message_sent", conversation_id=canonical.conversation_id)
            return {"status": "ok", "reply": reply.model_dump(), "omni": response}
        except Exception as exc:
            log_event(logger, "ERROR", "omni_send_failed", conversation_id=canonical.conversation_id, error=str(exc))
            return {"status": "error", "reply": reply.model_dump(), "error": str(exc)}

    return {"status": "ok", "reply": reply.model_dump()}


