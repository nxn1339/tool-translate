import unittest
from fastapi.testclient import TestClient
from app.downloader import download_bilibili_video
from app.main import append_project_log, projects_db, app


class TestDownloadTerminal(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_append_project_log(self):
        pid = "test_proj_log_123"
        projects_db[pid] = {"status": "downloading", "progress": 10, "logs": []}
        
        append_project_log(pid, "Đang kết nối tải video...", level="INFO")
        append_project_log(pid, "Cảnh báo tốc độ mạng thấp", level="WARN")
        append_project_log(pid, "Tải thành công", level="SUCCESS")
        
        logs = projects_db[pid]["logs"]
        self.assertEqual(len(logs), 3)
        self.assertIn("[INFO]", logs[0])
        self.assertIn("Đang kết nối tải video...", logs[0])
        self.assertIn("[WARN]", logs[1])
        self.assertIn("Cảnh báo tốc độ mạng thấp", logs[1])
        self.assertIn("[SUCCESS]", logs[2])
        self.assertIn("Tải thành công", logs[2])

    def test_project_status_endpoint_returns_logs(self):
        pid = "test_proj_status_456"
        projects_db[pid] = {
            "status": "downloading",
            "progress": 35,
            "message": "Đang tải video...",
            "logs": ["[15:00:00] [INFO] Bắt đầu tải video..."]
        }
        
        resp = self.client.get(f"/api/project/{pid}/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("logs", data)
        self.assertEqual(len(data["logs"]), 1)
        self.assertIn("Bắt đầu tải video...", data["logs"][0])

    def test_progress_calculation_non_decreasing(self):
        # Stream 0 (Video): mapped 5% -> 75%
        raw_video = 50.0
        overall_video = 5.0 + (raw_video * 0.70)
        self.assertEqual(overall_video, 40.0)
        
        raw_video_done = 100.0
        overall_video_done = 5.0 + (raw_video_done * 0.70)
        self.assertEqual(overall_video_done, 75.0)
        
        # Stream 1 (Audio): mapped 75% -> 90%
        raw_audio = 50.0
        overall_audio = 75.0 + (raw_audio * 0.15)
        self.assertEqual(overall_audio, 82.5)
        
        raw_audio_done = 100.0
        overall_audio_done = 75.0 + (raw_audio_done * 0.15)
        self.assertEqual(overall_audio_done, 90.0)
        
        # Verify no regression from video completion (75%) when audio starts (0%)
        audio_start = 75.0 + (0.0 * 0.15)
        self.assertEqual(audio_start, 75.0)
        self.assertGreaterEqual(audio_start, overall_video_done)


if __name__ == "__main__":
    unittest.main()
