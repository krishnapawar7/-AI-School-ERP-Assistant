from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "homework.json"


class HomeworkError(ValueError):
    """Raised when homework data is unavailable."""


def _load_data() -> List[Dict[str, Any]]:
    try:
        with DATA_FILE.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise HomeworkError("Missing homework data") from exc
    except json.JSONDecodeError as exc:
        raise HomeworkError("Corrupted JSON") from exc

    if not isinstance(data, list):
        raise HomeworkError("Missing homework data")
    return data


def get_homework_response(student_id: Optional[str], query: str) -> Dict[str, Any]:
    if not student_id:
        raise HomeworkError("Invalid student ID")

    records = [record for record in _load_data() if str(record.get("student_id", "")).upper() == str(student_id).strip().upper()]
    if not records:
        raise HomeworkError("Missing homework data")

    pending = [record for record in records if not record.get("completed", False)]
    today_homework = [record for record in records if str(record.get("day", "")).lower() == "today"]

    return {
        "student_id": str(student_id).strip().upper(),
        "count": len(pending),
        "today_homework": today_homework,
        "pending_homework": pending,
        "query": query,
    }
