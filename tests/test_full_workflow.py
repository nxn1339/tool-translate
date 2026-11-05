import os
import json
import unittest
from app.merger import generate_preview_audio_track
from app.main import append_project_log, get_project_logs, project_get_status

class TestFullOptimization(unittest.TestCase):
    def test_preview_generation_and_logs(self):
        project_id = "a98c6f85-5df1-400f-b634-7b28f5ff4f04"
        project_dir = os.path.join("app", "projects", project_id)
        if not os.path.exists(project_dir):
            self.skipTest(f"Project {project_id} does not exist")

        segments_file = os.path.join(project_dir, "segments.json")
        self.assertTrue(os.path.exists(segments_file))
        with open(segments_file, "r", encoding="utf-8") as f:
            segments = json.load(f)

        # Test logging persistence
        append_project_log(project_id, "Bắt đầu kiểm thử preview audio track...", level="INFO")
        logs = get_project_logs(project_id)
        self.assertTrue(any("kiểm thử preview" in l for l in logs))

        # Test persistent file on disk
        logs_file = os.path.join(project_dir, "project_logs.json")
        self.assertTrue(os.path.exists(logs_file))

        # Test generate_preview_audio_track with fast NumPy mixer
        import time
        t0 = time.time()
        out_mp3 = generate_preview_audio_track(project_dir, segments, voice="female_hoaimy")
        elapsed = time.time() - t0

        print(f"\nGenerated preview audio in {elapsed:.2f}s: {out_mp3}")
        self.assertTrue(os.path.exists(out_mp3))
        self.assertGreater(os.path.getsize(out_mp3), 10000)

        # Verify status endpoint returns logs
        status_res = project_get_status(project_id)
        self.assertIn("logs", status_res)
        self.assertGreater(len(status_res["logs"]), 0)

if __name__ == "__main__":
    unittest.main()

