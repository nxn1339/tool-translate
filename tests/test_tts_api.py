import os
import unittest
from fastapi.testclient import TestClient
from app.main import app, get_project_logs

class TestGenerateTTSEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.project_id = "a98c6f85-5df1-400f-b634-7b28f5ff4f04"

    def test_generate_tts_endpoint(self):
        res = self.client.post(
            f"/api/project/{self.project_id}/generate-tts",
            json={"voice": "female_hoaimy", "rvc_model": "none", "rvc_pitch": 0}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "started")
        self.assertEqual(data["voice"], "female_hoaimy")

        # Check status endpoint
        st_res = self.client.get(f"/api/project/{self.project_id}/status")
        self.assertEqual(st_res.status_code, 200)
        st_data = st_res.json()
        self.assertIn("logs", st_data)
        msg = str(st_data.get("message", "")).encode("ascii", "replace").decode("ascii")
        print("\nStatus data message:", msg)

if __name__ == "__main__":
    unittest.main()

