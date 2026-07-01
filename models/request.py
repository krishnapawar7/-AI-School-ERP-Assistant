from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):
    """Incoming chat request model."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    session_id: str = Field(default="default", min_length=1, max_length=64)
    student_id: Optional[str] = Field(default=None, description="Student ID (e.g. STU001).")
    use_gemini: bool = Field(default=False, description="If true, generate an enriched response using Gemini when configured.")
    query: str = Field(..., min_length=1, max_length=500, description="Natural language user query.")

    @field_validator("student_id")
    @classmethod
    def normalize_student_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return value.upper()

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Query cannot be empty.")
        return value.strip()
