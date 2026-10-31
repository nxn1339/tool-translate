import os
import io
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.merger import merge_audio_segments_to_video
from app.main import app, get_project_dir, save_project_meta


class TestLogoOverlay(unittest.TestCase):
    def setUp(self):
        self.dummy_video = "dummy_video.mp4"
        self.dummy_logo = "dummy_logo.png"
        self.dummy_output = "dummy_out.mp4"

        # Create temporary dummy files
        with open(self.dummy_video, "w") as f:
            f.write("video")
        with open(self.dummy_logo, "w") as f:
            f.write("logo")

        self.client = TestClient(app)

    def tearDown(self):
        for f in [self.dummy_video, self.dummy_logo, self.dummy_output, "filter_script.txt", "subtitles.srt", "subtitles.ass"]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass

    @patch("app.merger.get_video_dimensions", return_value=(1920, 1080))
    @patch("app.merger.get_video_duration", return_value=10.0)
    @patch("app.merger.check_video_has_audio", return_value=True)
    @patch("subprocess.run")
    def test_merge_with_logo_overlay_enabled(self, mock_run, mock_has_audio, mock_dur, mock_dims):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc

        logo_config = {
            "enabled": True,
            "image_path": self.dummy_logo,
            "x": 80.0,
            "y": 5.0,
            "w": 15.0,
            "h": 10.0,
            "opacity": 0.85,
            "keep_aspect": True
        }

        merge_audio_segments_to_video(
            original_video_path=self.dummy_video,
            segments=[],
            output_video_path=self.dummy_output,
            burn_subtitles=False,
            logo_box=logo_config
        )

        self.assertTrue(mock_run.called)
        cmd = mock_run.call_args[0][0]

        # Verify logo input is passed as input
        self.assertIn("-i", cmd)
        self.assertIn(self.dummy_logo, cmd)

        # Verify filter_complex was generated with logo scaling and overlay
        self.assertIn("-filter_complex", cmd)
        fc_idx = cmd.index("-filter_complex")
        filter_str = cmd[fc_idx + 1]

        # 15% of 1920 is 288px
        self.assertIn("scale=288:-1", filter_str)
        # Opacity 0.85
        self.assertIn("colorchannelmixer=aa=0.85", filter_str)
        # X: 80% of 1920 = 1536, Y: 5% of 1080 = 54
        self.assertIn("overlay=x=1536:y=54", filter_str)
        self.assertIn("[v_logo_out]", filter_str)

        # Output video mapping should map v_logo_out
        self.assertIn("[v_logo_out]", cmd)

    @patch("app.merger.get_video_dimensions", return_value=(1920, 1080))
    @patch("app.merger.get_video_duration", return_value=10.0)
    @patch("app.merger.check_video_has_audio", return_value=True)
    @patch("subprocess.run")
    def test_merge_without_logo_overlay(self, mock_run, mock_has_audio, mock_dur, mock_dims):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc

        merge_audio_segments_to_video(
            original_video_path=self.dummy_video,
            segments=[],
            output_video_path=self.dummy_output,
            burn_subtitles=False,
            logo_box=None
        )

        self.assertTrue(mock_run.called)
        cmd = mock_run.call_args[0][0]

        # Verify logo is not in inputs
        self.assertNotIn(self.dummy_logo, cmd)

    def test_api_upload_and_get_logo(self):
        project_id = "test_logo_project"
        p_dir = get_project_dir(project_id)

        # Upload a dummy PNG
        fake_png = io.BytesIO(b"\x89PNG\r\n\x1a\nfakecontent")
        res = self.client.post(
            f"/api/project/{project_id}/logo",
            files={"file": ("watermark.png", fake_png, "image/png")}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["filename"], "watermark.png")
        self.assertTrue(data["logo_box"]["enabled"])

        # Fetch the uploaded logo
        get_res = self.client.get(f"/api/project/{project_id}/logo")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.content, b"\x89PNG\r\n\x1a\nfakecontent")

        # Clean up test project directory files
        for f in os.listdir(p_dir):
            try:
                os.remove(os.path.join(p_dir, f))
            except Exception:
                pass


if __name__ == "__main__":
    unittest.main()
