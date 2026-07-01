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

    records = [record for record in _load_data() if str(record.get("student_id", "")).upper() == str(student_id).strip().upper()]
    if not records:
        raise TimetableError("Missing timetable data")

    q = query.lower()
    today = [record for record in records if str(record.get("day", "")).lower() == "today"]
    tomorrow = [record for record in records if str(record.get("day", "")).lower() == "tomorrow"]

    if "tomorrow" in q:
        return {"student_id": str(student_id).strip().upper(), "tomorrow_timetable": tomorrow}
    if "next class" in q:
        return {"student_id": str(student_id).strip().upper(), "next_class": today[0] if today else tomorrow[0] if tomorrow else None}
    return {"student_id": str(student_id).strip().upper(), "today_timetable": today, "tomorrow_timetable": tomorrow}
