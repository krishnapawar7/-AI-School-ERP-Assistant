from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from agents.academic_summary import academic_summary


class ParentReportEngine:
    """Generate a parent-friendly report from the academic summary."""

    def generate(self, student_id: str) -> Dict[str, Any]:
        summary = academic_summary.generate(student_id)
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "student_id": student_id,
            "overall_performance": summary["overall_performance"],
            "attendance": summary["attendance"],
            "marks": {
                "average": summary["marks"]["average"],
                "highest": summary["marks"]["highest"],
                "lowest": summary["marks"]["lowest"],
            },
            "pending_homework": summary["homework"]["pending"],
            "fee_status": summary["fees"],
            "recommendations": summary["recommendations"],
            "message": self._message(summary),
        }

    @staticmethod
    def _message(summary: Dict[str, Any]) -> str:
        attendance = summary["attendance"].get("attendance_percentage", 0)
        average = summary["marks"]["average"]
        homework = summary["homework"]["pending"]
        pending_fee = summary["fees"].get("pending", 0)
        return f"Attendance is {attendance}% with an average score of {average}. Pending homework: {homework}; pending fee: {pending_fee}."


parent_report = ParentReportEngine()
