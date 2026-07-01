from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ExecutionPlan:
    intent: str
    tools: List[str]
    entities: Dict[str, str]
    confidence: float


class AIPlanner:
    """Lightweight intent planner for ERP queries."""

    TOOL_KEYWORDS = {
        "attendance": ["attendance", "absent", "missed", "present", "class attended"],
        "marks": ["marks", "mark", "grade", "score", "percentage"],
        "fees": ["fees", "fee", "payment", "receipt"],
        "homework": ["homework", "assignment", "pending work"],
        "timetable": ["timetable", "class", "schedule", "next class"],
    }

    def plan(self, query: str) -> ExecutionPlan:
        normalized = query.lower().strip()
        tools: List[str] = []
        attendance_keywords = self.TOOL_KEYWORDS["attendance"]
        marks_keywords = self.TOOL_KEYWORDS["marks"]

        if any(keyword in normalized for keyword in attendance_keywords):
            tools.append("attendance")

        if any(keyword in normalized for keyword in marks_keywords) and "attendance" not in normalized:
            tools.append("marks")

        if not tools:
            tools = ["attendance"]

        intent = "general"
        if tools:
            intent = tools[0]

        entities = {}
        student_match = re.search(r"\b(stu\d{3})\b", normalized, flags=re.IGNORECASE)
        if student_match:
            entities["student_id"] = student_match.group(1).upper()

        return ExecutionPlan(intent=intent, tools=tools, entities=entities, confidence=self._confidence(tools))

    @staticmethod
    def _confidence(tools: List[str]) -> float:
        return 0.90 if len(tools) <= 2 else 0.85


planner = AIPlanner()
