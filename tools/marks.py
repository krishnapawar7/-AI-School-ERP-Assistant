from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "marks.json"


class MarksError(ValueError):
    """Raised when marks data is invalid or unavailable."""


def _load_marks_data() -> List[Dict[str, Any]]:
    """Load marks records from the mock JSON file."""
    try:
        with DATA_FILE.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError as exc:
        raise MarksError("Missing marks data") from exc
    except json.JSONDecodeError as exc:
        raise MarksError("Corrupted JSON") from exc

    if not isinstance(payload, list):
        raise MarksError("Missing marks data")
    return payload


def _normalize_student_id(student_id: Optional[str]) -> str:
    """Validate and normalize student identifiers."""
    if not student_id or not str(student_id).strip():
        raise MarksError("Invalid student ID")
    return str(student_id).strip().upper()


def _detect_query_type(query: str) -> str:
    """Classify the user query into a supported marks request."""
    lower_query = query.lower()
    if "highest" in lower_query or "top" in lower_query:
        return "highest"
    if "average" in lower_query or "avg" in lower_query:
        return "average"
    if "percentage" in lower_query or "percent" in lower_query:
        return "percentage"
    if "subject" in lower_query or "for" in lower_query:
        return "subject"
    return "summary"


def _detect_subject(query: str, records: List[Dict[str, Any]]) -> Optional[str]:
    """Try to identify a subject mentioned in the query."""
    lower_query = query.lower()
    for record in records:
        subject = str(record.get("subject", "")).lower()
        if subject and subject in lower_query:
            return str(record.get("subject", ""))
    return None


def _filter_records(records: List[Dict[str, Any]], student_id: str, subject: Optional[str]) -> List[Dict[str, Any]]:
    """Return marks records matching a student and optional subject."""
    student_records = [record for record in records if str(record.get("student_id", "")).strip().upper() == student_id]
    if not student_records:
        raise MarksError("Missing marks data")
    if subject:
        filtered = [record for record in student_records if str(record.get("subject", "")).strip().lower() == subject.lower()]
        if not filtered:
            raise MarksError("Missing marks data")
        return filtered
    return student_records


def get_marks_response(student_id: Optional[str], query: str) -> Dict[str, Any]:
    """Build a structured marks response for chat requests."""
    normalized_student_id = _normalize_student_id(student_id)
    records = _load_marks_data()
    query_type = _detect_query_type(query)

    matching = [item for item in records if str(item.get("student_id", "")).strip().upper() == normalized_student_id]
    if not matching:
        raise MarksError("Missing marks data")

    subjects = matching[0].get("subjects") if matching else None
    if not isinstance(subjects, list):
        raise MarksError("Missing marks data")

    if query_type == "highest":
        best_record = max(subjects, key=lambda item: float(item.get("marks", 0)))
        return {
            "student_id": normalized_student_id,
            "query_type": query_type,
            "subject": best_record.get("subject"),
            "marks": int(best_record.get("marks", 0)),
        }

    if query_type == "average":
        average_marks = round(sum(float(item.get("marks", 0)) for item in subjects) / len(subjects), 2) if subjects else 0.0
        return {
            "student_id": normalized_student_id,
            "query_type": query_type,
            "average_marks": average_marks,
            "subject_count": len(subjects),
            "subjects": [
                {"subject": item.get("subject"), "marks": int(item.get("marks", 0))}
                for item in subjects
            ],
        }

    if query_type == "percentage":
        total_marks = sum(float(item.get("marks", 0)) for item in subjects)
        percentage = round((total_marks / (len(subjects) * 100)) * 100, 2) if subjects else 0.0
        return {
            "student_id": normalized_student_id,
            "query_type": query_type,
            "percentage": percentage,
            "obtained_marks": round(total_marks, 2),
            "total_marks": len(subjects) * 100,
        }

    return {
        "student_id": normalized_student_id,
        "query_type": query_type,
        "subjects": [
            {"subject": item.get("subject"), "marks": int(item.get("marks", 0))}
            for item in subjects
        ],
        "summary": {
            "total_subjects": len(subjects),
            "average_marks": round(sum(float(item.get("marks", 0)) for item in subjects) / len(subjects), 2) if subjects else 0.0,
        },
    }
