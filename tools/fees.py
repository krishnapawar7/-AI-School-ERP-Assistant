from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "fees.json"


class FeesError(ValueError):
    """Raised when fee data cannot be processed."""


def _load_data() -> List[Dict[str, Any]]:
    try:
        with DATA_FILE.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise FeesError("Missing fee records") from exc
    except json.JSONDecodeError as exc:
        raise FeesError("Corrupted JSON") from exc

    if not isinstance(data, list):
        raise FeesError("Missing fee records")
    return data


def _student(records: List[Dict[str, Any]], student_id: str) -> List[Dict[str, Any]]:
    sid = student_id.strip().upper()
    result = [record for record in records if str(record.get("student_id", "")).upper() == sid]
    if not result:
        raise FeesError("Missing fee records")
    return result


def get_fees_response(student_id: Optional[str], query: str) -> Dict[str, Any]:
    if not student_id:
        raise FeesError("Invalid student ID")

    records = _student(_load_data(), student_id)
    q = query.lower()
    total = sum(float(record["amount"]) for record in records)
    paid = sum(float(record["amount"]) for record in records if record["status"] == "Paid")
    pending = total - paid

    if "pending" in q:
        return {
            "student_id": student_id.upper(),
            "pending": pending,
            "currency": "INR",
            "records": records,
        }

    if "history" in q or "paid" in q:
        return {"student_id": student_id.upper(), "paid_records": [record for record in records if record["status"] == "Paid"], "records": records}

    return {"student_id": student_id.upper(), "total_fee": total, "paid": paid, "pending": pending, "records": records}
