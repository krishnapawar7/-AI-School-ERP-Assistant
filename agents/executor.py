from __future__ import annotations

from typing import Any, Dict, List

from tools.attendance import AttendanceError, get_attendance_response
from tools.marks import MarksError, get_marks_response
from tools.fees import FeesError, get_fees_response
from tools.homework import HomeworkError, get_homework_response
from tools.timetable import TimetableError, get_timetable_response


class ToolExecutor:
    """Executes one or more ERP tools selected by the AI planner."""

    TOOL_MAP = {
        "attendance": get_attendance_response,
        "marks": get_marks_response,
        "fees": get_fees_response,
        "homework": get_homework_response,
        "timetable": get_timetable_response,
    }

    def execute(self, student_id: str, query: str, tools: List[str]) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        errors: List[str] = []
        for tool_name in tools:
            try:
                handler = self.TOOL_MAP[tool_name]
                results[tool_name] = handler(student_id, query)
            except (AttendanceError, MarksError, FeesError, HomeworkError, TimetableError) as exc:
                errors.append(f"{tool_name}: {exc}")
        status = "success" if not errors else "partial_success"
        return {"status": status, "results": results, "errors": errors}


executor = ToolExecutor()
