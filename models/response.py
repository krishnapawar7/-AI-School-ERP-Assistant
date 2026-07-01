from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


class APIError(BaseModel):
    model_config = ConfigDict(extra="ignore")

    tool: str
    error: str


class ChatResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    intent: str
    confidence: float
    plan: List[str]
    entities: Dict[str, str]
    tool: List[str] = Field(default_factory=list)
    status: str
    response: Dict[str, Any]
    errors: List[APIError] = Field(default_factory=list)


class HistoryResponse(BaseModel):
    session_id: str
    history: List[Dict[str, Any]]


class LogsResponse(BaseModel):
    logs: List[Dict[str, Any]]
