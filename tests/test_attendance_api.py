import unittest

from fastapi.testclient import TestClient

from main import app


class AttendanceApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_show_attendance(self) -> None:
        response = self.client.post(
            "/chat",
            json={"query": "Show my attendance", "student_id": "stu001"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["intent"], "Attendance")
        self.assertEqual(payload["status"], "success")
        self.assertIn("attendance_percentage", payload["response"])

    def test_percentage_query(self) -> None:
        response = self.client.post(
            "/chat",
            json={"query": "What is my attendance percentage?", "student_id": "stu001"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["tool"], ["attendance"])
        self.assertGreaterEqual(payload["response"]["attendance_percentage"], 0)

    def test_invalid_student_id(self) -> None:
        response = self.client.post(
            "/chat",
            json={"query": "Show my attendance", "student_id": "   "},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "error")


if __name__ == "__main__":
    unittest.main()
