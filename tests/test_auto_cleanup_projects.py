import unittest
import os
import json
import time
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app, PROJECTS_DIR, cleanup_expired_projects, projects_db


class TestAutoCleanupProjects(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_project_ids = []

    def tearDown(self):
        # Clean up any leftover test directories
        for pid in self.test_project_ids:
            p_dir = os.path.join(PROJECTS_DIR, pid)
            if os.path.isdir(p_dir):
                import shutil
                shutil.rmtree(p_dir, ignore_errors=True)
            if pid in projects_db:
                del projects_db[pid]

    def _create_mock_project(self, project_id: str, updated_days_ago: float, created_days_ago: float = None, status: str = "draft", write_json: bool = True):
        self.test_project_ids.append(project_id)
        p_dir = os.path.join(PROJECTS_DIR, project_id)
        os.makedirs(p_dir, exist_ok=True)

        now = datetime.now()
        updated_dt = now - timedelta(days=updated_days_ago)
        created_dt = now - timedelta(days=created_days_ago if created_days_ago is not None else updated_days_ago)

        if write_json:
            meta = {
                "id": project_id,
                "name": f"Mock Project {project_id}",
                "type": "dubber",
                "status": status,
                "created_at": created_dt.isoformat(),
                "updated_at": updated_dt.isoformat(),
                "data": {}
            }
            meta_path = os.path.join(p_dir, "project.json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f)

        # Update folder mtime on filesystem
        target_ts = updated_dt.timestamp()
        os.utime(p_dir, (target_ts, target_ts))
        return p_dir

    def test_active_recent_project_not_deleted(self):
        pid = "test_recent_project_001"
        p_dir = self._create_mock_project(pid, updated_days_ago=2.0)
        self.assertTrue(os.path.isdir(p_dir))

        deleted = cleanup_expired_projects(max_age_days=7)
        self.assertNotIn(pid, deleted)
        self.assertTrue(os.path.isdir(p_dir), "Dự án mới cập nhật 2 ngày trước không được phép bị xóa")

    def test_expired_project_deleted(self):
        pid = "test_expired_project_002"
        p_dir = self._create_mock_project(pid, updated_days_ago=8.0)
        self.assertTrue(os.path.isdir(p_dir))

        deleted = cleanup_expired_projects(max_age_days=7)
        self.assertIn(pid, deleted)
        self.assertFalse(os.path.exists(p_dir), "Dự án quá 7 ngày (8 ngày) phải bị xóa tự động")

    def test_project_created_long_ago_but_recently_updated(self):
        pid = "test_old_created_recent_updated_003"
        # Created 10 days ago, but updated 1 day ago
        p_dir = self._create_mock_project(pid, updated_days_ago=1.0, created_days_ago=10.0)
        self.assertTrue(os.path.isdir(p_dir))

        deleted = cleanup_expired_projects(max_age_days=7)
        self.assertNotIn(pid, deleted)
        self.assertTrue(os.path.isdir(p_dir), "Dự án vẫn được cập nhật 1 ngày trước không được phép bị xóa dù đã tạo 10 ngày trước")

    def test_corrupt_folder_without_json_deleted_by_mtime(self):
        pid = "test_corrupt_folder_004"
        # Folder without project.json, mtime 9 days ago
        p_dir = self._create_mock_project(pid, updated_days_ago=9.0, write_json=False)
        self.assertTrue(os.path.isdir(p_dir))

        deleted = cleanup_expired_projects(max_age_days=7)
        self.assertIn(pid, deleted)
        self.assertFalse(os.path.exists(p_dir), "Thư mục rác không có project.json mtime > 7 ngày phải bị xóa")

    def test_active_rendering_project_not_deleted(self):
        pid = "test_active_task_005"
        p_dir = self._create_mock_project(pid, updated_days_ago=9.0, status="rendering")
        projects_db[pid] = {"status": "rendering", "progress": 50}

        deleted = cleanup_expired_projects(max_age_days=7)
        self.assertNotIn(pid, deleted)
        self.assertTrue(os.path.isdir(p_dir), "Dự án đang render dù thời gian cũ cũng không được xóa")

    def test_cleanup_api_endpoint(self):
        pid = "test_api_cleanup_006"
        p_dir = self._create_mock_project(pid, updated_days_ago=10.0)

        res = self.client.post("/api/projects/cleanup?max_age_days=7")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertIn(pid, data.get("deleted_projects", []))
        self.assertFalse(os.path.exists(p_dir))

    def test_list_projects_triggers_cleanup(self):
        pid = "test_list_trigger_007"
        p_dir = self._create_mock_project(pid, updated_days_ago=12.0)

        res = self.client.get("/api/projects")
        self.assertEqual(res.status_code, 200)
        all_ids = [p["id"] for p in res.json()]
        self.assertNotIn(pid, all_ids)
        self.assertFalse(os.path.exists(p_dir), "Gọi GET /api/projects phải tự động dọn dẹp dự án hết hạn")


if __name__ == "__main__":
    unittest.main()

