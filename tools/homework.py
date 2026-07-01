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

    records = [
        record for record in _load_data()
        if str(record.get("student_id", "")).strip().upper() == str(student_id).strip().upper()
    ]
    if not records:
        raise HomeworkError("Missing homework data")

    pending = [record for record in records if record.get("status", "").lower() != "completed"]
    response = {
        "student_id": str(student_id).strip().upper(),
        "total_homework": len(records),
        "pending_count": len(pending),
        "pending_homework": pending,
        "query": query,
    }

    if "pending" in query.lower():
        return {"student_id": response["student_id"], "pending_homework": pending, "pending_count": len(pending)}

    return response
