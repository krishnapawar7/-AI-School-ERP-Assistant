from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

LOG_FILE = Path(__file__).resolve().parent.parent / "data" / "logs.json"


class Logger:
    """Simple JSON logger for chat requests and tool execution."""

    def __init__(self) -> None:
        self.file = LOG_FILE
        self.file.parent.mkdir(parents=True, exist_ok=True)
        if not self.file.exists():
            self.file.write_text("[]", encoding="utf-8")

    def log(self, session_id: str, query: str, intent: str, tools: List[str], response: Dict[str, Any], execution_time: float, status: str, errors: List[str]) -> None:
        history = self._read()
        history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "query": query,
            "intent": intent,
            "tools": tools,
            "response": response,
            "execution_time_ms": round(execution_time * 1000, 2),
            "status": status,
            "errors": errors,
        })
        self.file.write_text(json.dumps(history, indent=2), encoding="utf-8")

    def history(self) -> List[Dict[str, Any]]:
        return self._read()

    def _read(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.file.read_text(encoding="utf-8"))
        except Exception:
            return []


logger = Logger()
