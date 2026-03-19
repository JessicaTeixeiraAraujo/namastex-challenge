from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


class ScreeningOut(BaseModel):
    decision: Literal["HIGH_SCALABLE", "REQUEST_INFORMATION", "OPEN_TICKET"]
    urgency: Literal["LOW", "MEDIUM", "HIGH"]
    missing_fields: List[str] = Field(default_factory=list)


class CanonicalIncoming(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    conversation_id: str
    channel: str
    from_number: str = Field(alias="from")
    text: str
    timestamp: str
    metadata: dict = Field(default_factory=dict)


class CanonicalReply(BaseModel):
    conversation_id: str
    reply: str
    handoff: bool = False
    tags: List[str] = Field(default_factory=list)


class OmniEvent(BaseModel):
    id: str
    type: str
    payload: dict
    metadata: dict
    timestamp: int


class OmniMessagePayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    externalId: str
    chatId: str
    from_number: str = Field(alias="from")
    content: dict
    replyToId: Optional[str] = None
    rawPayload: Optional[dict] = None
