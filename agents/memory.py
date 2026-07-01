from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import json

MEMORY_FILE = Path(__file__).resolve().parent.parent / "data" / "conversation_memory.json"


class ConversationMemory:
    """Persistent conversation memory for follow-up questions."""

    def __init__(self) -> None:
        self.file = MEMORY_FILE
        self.file.parent.mkdir(parents=True, exist_ok=True)
        if not self.file.exists():
            self._save({})

    def _load(self) -> Dict[str, List[Dict[str, str]]]:
        try:
            return json.loads(self.file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self, data: Dict[str, List[Dict[str, str]]]) -> None:
        self.file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add_message(self, session_id: str, role: str, content: str) -> None:
        history = self._load()
        history.setdefault(session_id, [])
        history[session_id].append({"role": role, "content": content})
        history[session_id] = history[session_id][-20:]
        self._save(history)

    def history(self, session_id: str) -> List[Dict[str, str]]:
        return self._load().get(session_id, [])

    def last_user_message(self, session_id: str) -> Optional[str]:
        for message in reversed(self.history(session_id)):
            if message.get("role") == "user":
                return message.get("content")
        return None

    def resolve_followup(self, session_id: str, query: str) -> str:
        lowered = query.lower().strip()
        if lowered.startswith("what about") or lowered.startswith("and"):
            previous = self.last_user_message(session_id)
            if previous:
                return f"{previous} {query}"
        return query


memory = ConversationMemory()
