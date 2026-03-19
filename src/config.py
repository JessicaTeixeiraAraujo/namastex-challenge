import os

from dotenv import load_dotenv


load_dotenv()


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}

OMNI_BASE_URL = os.getenv("OMNI_BASE_URL", "http://localhost:8882").rstrip("/")
OMNI_API_KEY = os.getenv("OMNI_API_KEY", "")
OMNI_INSTANCE_ID = os.getenv("OMNI_INSTANCE_ID", "")

PORT = int(os.getenv("PORT", "8080"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "logs/triage.log")

SEND_VIA_OMNI = env_bool("SEND_VIA_OMNI", True)
IGNORE_HISTORY_SYNC = env_bool("IGNORE_HISTORY_SYNC", True)
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "1000"))

GENIE_ENABLED = env_bool("GENIE_ENABLED", False)
GENIE_TEAM = os.getenv("GENIE_TEAM", "omni-whatsapp")
GENIE_AGENT = os.getenv("GENIE_AGENT", "team-lead")
GENIE_REPLY_PREFIX = os.getenv("GENIE_REPLY_PREFIX", "GENIE_JSON:")
GENIE_RESPONSE_TIMEOUT_SECONDS = int(os.getenv("GENIE_RESPONSE_TIMEOUT_SECONDS", "20"))

OPENAI_FALLBACK_ENABLED = env_bool("OPENAI_FALLBACK_ENABLED", False)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TIMEOUT_SECONDS = int(os.getenv("OPENAI_TIMEOUT_SECONDS", "20"))

