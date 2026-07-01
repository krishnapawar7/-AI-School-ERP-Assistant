from __future__ import annotations

from typing import Any, Dict

from agents.recommendation import recommendation_engine
from tools.attendance import get_attendance_response
from tools.fees import get_fees_response
from tools.homework import get_homework_response
from tools.marks import get_marks_response


class AcademicSummaryEngine:
    """Generate a compact academic overview for a student."""

    def generate(self, student_id: str) -> Dict[str, Any]:
        attendance = get_attendance_response(student_id, "attendance percentage")
        marks = get_marks_response(student_id, "marks")
        homework = get_homework_response(student_id, "pending homework")
        fees = get_fees_response(student_id, "fees")
        recommendations = recommendation_engine.generate(student_id)

        subject_marks = marks.get("subject_marks", [])
        average_score = sum(item.get("marks", 0) for item in subject_marks) / len(subject_marks) if subject_marks else 0
        highest = max(subject_marks, key=lambda item: item.get("marks", 0), default={}) if subject_marks else {}
        lowest = min(subject_marks, key=lambda item: item.get("marks", 0), default={}) if subject_marks else {}

        return {
            "student_id": student_id,
            "overall_performance": "Excellent" if attendance.get("attendance_percentage", 0) >= 90 else "Good",
            "attendance": attendance,
            "marks": {
                "average": round(average_score, 2),
                "highest": highest,
                "lowest": lowest,
            },
            "homework": {"pending": homework.get("count", 0)},
            "fees": fees,
            "recommendations": recommendations.get("recommendations", []),
            "summary": "Student performance is on track with the current attendance and marks trend.",
        }


academic_summary = AcademicSummaryEngine()
