from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "timetable.json"


class TimetableError(ValueError):
    """Raised when timetable data is unavailable."""


def _load_data() -> List[Dict[str, Any]]:
    try:
        with DATA_FILE.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise TimetableError("Missing timetable data") from exc
    except json.JSONDecodeError as exc:
        raise TimetableError("Corrupted JSON") from exc

    if not isinstance(data, list):
        raise TimetableError("Missing timetable data")
    return data


def get_timetable_response(student_id: Optional[str], query: str) -> Dict[str, Any]:
    if not student_id:
        raise TimetableError("Invalid student ID")

    records = [
        record for record in _load_data()
        if str(record.get("student_id", "")).strip().upper() == str(student_id).strip().upper()
    ]
    if not records:
        raise TimetableError("Missing timetable data")

    q = query.lower()
    if "monday" in q or "tuesday" in q or "wednesday" in q or "thursday" in q or "friday" in q or "saturday" in q or "sunday" in q:
        day = next((word for word in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"] if word in q), None)
        return {"student_id": str(student_id).strip().upper(), "day": day.title() if day else None, "timetable": [record for record in records if record.get("day", "").strip().lower() == day]}

    return {"student_id": str(student_id).strip().upper(), "timetable": records}
