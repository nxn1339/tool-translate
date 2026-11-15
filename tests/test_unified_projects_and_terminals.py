import unittest
import os
import json
import time
from fastapi.testclient import TestClient
from app.main import app, PROJECTS_DIR

class TestUnifiedProjectsAndTerminals(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.created_project_ids = []

    def tearDown(self):
        # Clean up test directories safely
        for pid in self.created_project_ids:
            p_dir = os.path.join(PROJECTS_DIR, pid)
            if os.path.isdir(p_dir):
                import shutil
                shutil.rmtree(p_dir, ignore_errors=True)

    def test_create_and_filter_projects(self):
        # 1. Create a story_tts project
        res_story = self.client.post("/api/projects", json={
            "type": "story_tts",
            "name": "Test Story Project #1",
            "data": {
                "story_text": "Ngày xửa ngày xưa, ở một ngôi làng nọ...",
                "channel_name": "Hạt Tiêu Vietsub",
                "voice": "capcut_cogaithoatngon"
            }
        })
        self.assertEqual(res_story.status_code, 200)
        story_data = res_story.json()
        story_id = story_data["id"]
        self.created_project_ids.append(story_id)
        self.assertEqual(story_data.get("type"), "story_tts")
        self.assertEqual(story_data.get("name"), "Test Story Project #1")

        # 2. Create a social_video project
        res_social = self.client.post("/api/projects", json={
            "type": "social_video",
            "name": "Test Social Threads #1",
            "data": {
                "platform": "threads",
                "author_name": "Review Phim Hay",
                "post_content": "Đây là bài viết threads chia sẻ góc nhìn.",
                "post_voice": "capcut_thanhnientutin"
            }
        })
        self.assertEqual(res_social.status_code, 200)
        social_data = res_social.json()
        social_id = social_data["id"]
        self.created_project_ids.append(social_id)
        self.assertEqual(social_data.get("type"), "social_video")

        # 3. Filter by type=story_tts
        res_list_story = self.client.get("/api/projects?type=story_tts")
        self.assertEqual(res_list_story.status_code, 200)
        stories = res_list_story.json()
        story_match = [p for p in stories if p["id"] == story_id]
        self.assertTrue(len(story_match) > 0)
        self.assertEqual(story_match[0]["type"], "story_tts")
        self.assertIn("Hạt Tiêu Vietsub", story_match[0].get("author_name", ""))

        # 4. Filter by type=social_video
        res_list_social = self.client.get("/api/projects?type=social_video")
        self.assertEqual(res_list_social.status_code, 200)
        socials = res_list_social.json()
        social_match = [p for p in socials if p["id"] == social_id]
        self.assertTrue(len(social_match) > 0)
        self.assertEqual(social_match[0]["type"], "social_video")
        self.assertEqual(social_match[0].get("author_name"), "Review Phim Hay")

    def test_save_and_load_full_project(self):
        # Create a new project
        res = self.client.post("/api/projects", json={
            "type": "story_tts",
            "name": "Story Project to Save"
        })
        self.assertEqual(res.status_code, 200)
        p_id = res.json()["id"]
        self.created_project_ids.append(p_id)

        # Save detailed project state via /api/projects/{id}/save
        payload = {
            "id": p_id,
            "name": "Story Project Saved Successfully",
            "type": "story_tts",
            "status": "ready",
            "data": {
                "story_text": "Nội dung truyện đã được chỉnh sửa và cập nhật.",
                "channel_name": "Audio Kể Chuyện Đêm Khuya",
                "intro_style": "dramatic",
                "intro_text": "Chào mừng bạn đến với kênh!",
                "voice": "capcut_thanhnientutin",
                "pause_ms": 400
            }
        }
        res_save = self.client.post(f"/api/projects/{p_id}/save", json=payload)
        self.assertEqual(res_save.status_code, 200)
        self.assertEqual(res_save.json().get("status"), "ok")

        # Load back via /api/projects/{id}
        res_load = self.client.get(f"/api/projects/{p_id}")
        self.assertEqual(res_load.status_code, 200)
        loaded = res_load.json()
        self.assertEqual(loaded["name"], "Story Project Saved Successfully")
        self.assertEqual(loaded["type"], "story_tts")
        self.assertEqual(loaded["data"]["channel_name"], "Audio Kể Chuyện Đêm Khuya")
        self.assertEqual(loaded["data"]["pause_ms"], 400)

    def test_story_tts_status_polling(self):
        # Test status endpoint for non-existent and simulated task
        res_none = self.client.get("/api/story-tts/status/non_existent_123")
        self.assertEqual(res_none.status_code, 200)
        data = res_none.json()
        self.assertIn(data.get("status"), ["not_found", "completed"])

        # Simulate a story synthesis task in story_tasks
        from app.story_tts import story_tasks, append_story_log
        mock_task_id = "test_mock_task_abc"
        story_tasks[mock_task_id] = {
            "task_id": mock_task_id,
            "status": "running",
            "progress": 45,
            "message": "Đang tổng hợp câu [3/10]...",
            "logs": []
        }
        append_story_log(mock_task_id, "[TTS] Đang gọi TikTok Voice cho câu 3")

        res_task = self.client.get(f"/api/story-tts/status/{mock_task_id}")
        self.assertEqual(res_task.status_code, 200)
        task_data = res_task.json()
        self.assertEqual(task_data["status"], "running")
        self.assertEqual(task_data["progress"], 45)
        self.assertTrue(any("TikTok Voice" in log for log in task_data["logs"]))

        # Clean up memory
        story_tasks.pop(mock_task_id, None)

    def test_social_video_status_polling(self):
        # Simulate social video task in social_tasks
        from app.social_router import social_tasks, append_social_log
        mock_social_id = "test_social_mock_xyz"
        social_tasks[mock_social_id] = {
            "task_id": mock_social_id,
            "status": "rendering",
            "progress": 72,
            "message": "Đang render video 9:16 bằng FFmpeg...",
            "logs": []
        }
        append_social_log(mock_social_id, "[FFmpeg] GPU acceleration nvenc initialized")

        res_social = self.client.get(f"/api/social/status/{mock_social_id}")
        self.assertEqual(res_social.status_code, 200)
        s_data = res_social.json()
        self.assertEqual(s_data["status"], "rendering")
        self.assertEqual(s_data["progress"], 72)
        self.assertTrue(any("GPU acceleration" in log for log in s_data["logs"]))

        # Clean up memory
        social_tasks.pop(mock_social_id, None)

if __name__ == "__main__":
    unittest.main()
