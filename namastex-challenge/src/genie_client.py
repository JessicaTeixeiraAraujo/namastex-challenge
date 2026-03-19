import json
import shutil
import subprocess
import time
from typing import Any, Dict, Optional

from .config import GENIE_AGENT, GENIE_REPLY_PREFIX, GENIE_RESPONSE_TIMEOUT_SECONDS, GENIE_TEAM


class GenieError(RuntimeError):
    pass


def _require_genie() -> str:
    genie_path = shutil.which("genie")
    if not genie_path:
        raise GenieError("genie CLI not found in PATH")
    return genie_path


def _run(cmd: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)


def send_to_genie(payload: Dict[str, Any]) -> None:
    message = json.dumps(payload, ensure_ascii=False)
    target = f"{GENIE_AGENT}@{GENIE_TEAM}"
    result = _run([_require_genie(), "send", message, "--to", target], timeout=20)
    if result.returncode != 0:
        raise GenieError(result.stderr.strip() or result.stdout.strip() or "genie send failed")


def _extract_reply(text: str) -> Optional[Dict[str, Any]]:
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line.startswith(GENIE_REPLY_PREFIX):
            continue
        raw = line[len(GENIE_REPLY_PREFIX) :].strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            continue
    return None


def wait_genie_reply(conversation_id: str) -> Dict[str, Any]:
    target = f"{GENIE_AGENT}@{GENIE_TEAM}"
    deadline = time.time() + GENIE_RESPONSE_TIMEOUT_SECONDS

    while time.time() < deadline:
        result = _run([_require_genie(), "read", target], timeout=20)
        if result.returncode == 0:
            payload = _extract_reply(result.stdout)
            if payload and payload.get("conversation_id") == conversation_id:
                return payload
        time.sleep(1)

    raise GenieError("timeout waiting for genie reply")
