from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "attendance.json"


class AttendanceError(ValueError):
    """Raised when attendance data cannot be processed safely."""


def _load_attendance_data() -> List[Dict[str, Any]]:
    """Load attendance records from the mock JSON database."""
    try:
        with DATA_FILE.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError as exc:
        raise AttendanceError("Missing attendance data") from exc
    except json.JSONDecodeError as exc:
        raise AttendanceError("Corrupted JSON") from exc

    if not isinstance(payload, list):
        raise AttendanceError("Missing attendance data")
    return payload


def _normalize_student_id(student_id: Optional[str]) -> str:
    """Validate and normalize student identifiers."""
    if not student_id or not str(student_id).strip():
        raise AttendanceError("Invalid student ID")
    return str(student_id).strip().upper()


def _resolve_month(query: str, month: Optional[str] = None) -> str:
    """Resolve the target month for attendance queries."""
    if month:
        return month
    return datetime.utcnow().strftime("%Y-%m")


def _parse_query_type(query: str) -> str:
    """Classify a natural language query into a specific attendance action."""
    lower_query = query.lower()
    if "percentage" in lower_query or "percent" in lower_query:
        return "percentage"
    if "miss" in lower_query or "absent" in lower_query or "missed" in lower_query:
        return "missed"
    if "month" in lower_query or "this month" in lower_query:
        return "monthly"
    return "summary"


def _filter_records(records: List[Dict[str, Any]], student_id: str, month: Optional[str]) -> List[Dict[str, Any]]:
    """Return matching records for the student and optional month."""
    student_records = [record for record in records if str(record.get("student_id", "")).strip().upper() == student_id]
    if not student_records:
        raise AttendanceError("Missing attendance data")

    if month:
        month_records = [record for record in student_records if str(record.get("month", "")).strip() == month]
        if not month_records:
            raise AttendanceError("Missing attendance data")
        return month_records

    return student_records


def get_attendance_response(student_id: Optional[str], query: str) -> Dict[str, Any]:
    """Build a structured attendance response for chat requests."""
    normalized_student_id = _normalize_student_id(student_id)
    records = _load_attendance_data()
    month = _resolve_month(query)
    query_type = _parse_query_type(query)
    matching_records = _filter_records(records, normalized_student_id, month if query_type == "monthly" else None)

    if query_type == "monthly" and matching_records:
        record = matching_records[0]
    else:
        record = matching_records[-1]

    if not record:
        raise AttendanceError("Missing attendance data")

    payload = {
        "student_id": normalized_student_id,
        "month": record.get("month", month),
        "query_type": query_type,
        "attended": int(record.get("attended", 0)),
        "total": int(record.get("total", 0)),
        "missed": int(record.get("missed", 0)),
        "attendance_percentage": round(float(record.get("percentage", 0.0)), 2),
        "status": record.get("status", "regular"),
        "history": [
            {
                "month": item.get("month"),
                "attendance_percentage": round(float(item.get("percentage", 0.0)), 2),
                "attended": int(item.get("attended", 0)),
                "total": int(item.get("total", 0)),
                "missed": int(item.get("missed", 0)),
            }
            for item in _filter_records(records, normalized_student_id, None)[-4:]
        ],
    }

    if query_type == "missed":
        payload["response_hint"] = f"You missed {payload['missed']} classes in {payload['month']}."
    elif query_type == "percentage":
        payload["response_hint"] = f"Your attendance percentage for {payload['month']} is {payload['attendance_percentage']}%."
    else:
        payload["response_hint"] = f"Attendance summary for {payload['month']} is ready."

    return payload
