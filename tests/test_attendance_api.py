import os
import unittest
from unittest.mock import patch

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

    def test_api_key_uses_environment_variable(self) -> None:
        with patch.dict(os.environ, {"API_KEY": "test-secret"}, clear=False):
            from main import get_gemini_api_key

            self.assertEqual(get_gemini_api_key(), "test-secret")

    def test_gemini_api_key_env_var(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "gemini-secret"}, clear=False):
            from main import get_gemini_api_key

            self.assertEqual(get_gemini_api_key(), "gemini-secret")

    def test_use_gemini_explicitly(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "gemini-secret"}, clear=False):
            with patch("api.routes.generate_gemini_text", return_value="Gemini enriched output"):
                response = self.client.post(
                    "/chat",
                    json={
                        "query": "Show my attendance",
                        "student_id": "stu001",
                        "use_gemini": True,
                    },
                )
                self.assertEqual(response.status_code, 200)
                payload = response.json()
                self.assertEqual(payload["status"], "success")
                self.assertEqual(payload["response"]["gemini_output"], "Gemini enriched output")


if __name__ == "__main__":
    unittest.main()
