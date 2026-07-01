import unittest

from agents.planner import planner
from agents.executor import executor
from tools.fees import get_fees_response
from tools.homework import get_homework_response
from tools.timetable import get_timetable_response


class ERPModuleTests(unittest.TestCase):
    def test_planner_detects_attendance(self) -> None:
        plan = planner.plan("show my attendance")
        self.assertIn("attendance", plan.tools)

    def test_executor_runs_multiple_tools(self) -> None:
        result = executor.execute("STU001", "attendance and marks", ["attendance", "marks"])
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["results"]), 2)

    def test_fee_tool(self) -> None:
        data = get_fees_response("STU001", "pending fees")
        self.assertIn("pending", data)

    def test_homework_tool(self) -> None:
        data = get_homework_response("STU001", "today homework")
        self.assertGreaterEqual(data["count"], 1)

    def test_timetable_tool(self) -> None:
        data = get_timetable_response("STU001", "today timetable")
        self.assertIn("today_timetable", data)


if __name__ == "__main__":
    unittest.main()
