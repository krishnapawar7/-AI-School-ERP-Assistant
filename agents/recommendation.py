from __future__ import annotations

from typing import Any, Dict, List

from tools.attendance import get_attendance_response
from tools.marks import get_marks_response
from tools.homework import get_homework_response
from tools.timetable import get_timetable_response


class RecommendationEngine:
    """Generate simple study recommendations from ERP data."""

    ATTENDANCE_LIMIT = 75
    MARK_LIMIT = 60

    def generate(self, student_id: str) -> Dict[str, Any]:
        attendance = get_attendance_response(student_id, "attendance percentage")
        marks = get_marks_response(student_id, "marks")
        homework = get_homework_response(student_id, "pending homework")
        timetable = get_timetable_response(student_id, "today timetable")

        percentage = attendance.get("attendance_percentage", 100)
        subjects = marks.get("subject_marks", [])
        recommendations: List[Dict[str, str]] = []

        if percentage < self.ATTENDANCE_LIMIT:
            recommendations.append({"title": "Attendance", "message": "Attend more classes to improve consistency."})
        if subjects and any(item.get("percentage", 0) < self.MARK_LIMIT for item in subjects):
            recommendations.append({"title": "Marks", "message": "Focus on weak subjects to raise overall performance."})
        if homework.get("count", 0) > 0:
            recommendations.append({"title": "Homework", "message": "Complete pending homework before the next class."})
        if timetable.get("today_timetable"):
            recommendations.append({"title": "Timetable", "message": "Follow the schedule closely for better preparation."})

        return {"student_id": student_id, "recommendations": recommendations}


recommendation_engine = RecommendationEngine()
