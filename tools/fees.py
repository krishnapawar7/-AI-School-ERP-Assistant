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

    cumulative = [record for record in _load_data() if str(record.get("student_id", "")).strip().upper() == str(student_id).strip().upper()]
    if not cumulative:
        raise FeesError("Missing fee records")

    if len(cumulative) == 1 and {"total_fee", "paid", "pending", "status"}.issubset(cumulative[0].keys()):
        record = cumulative[0]
        total = float(record.get("total_fee", 0))
        paid = float(record.get("paid", 0))
        pending = float(record.get("pending", 0))
        response = {
            "student_id": student_id.upper(),
            "total_fee": total,
            "paid": paid,
            "pending": pending,
            "status": record.get("status", "Pending"),
        }
    else:
        total = sum(float(record.get("amount", 0)) for record in cumulative)
        paid = sum(float(record.get("amount", 0)) for record in cumulative if record.get("status") == "Paid")
        pending = total - paid
        response = {
            "student_id": student_id.upper(),
            "total_fee": total,
            "paid": paid,
            "pending": pending,
            "records": cumulative,
        }

    if "pending" in query.lower():
        return response
    if "history" in query.lower() or "paid" in query.lower():
        response["paid_records"] = [record for record in cumulative if record.get("status") == "Paid"]
        return response
    return response
