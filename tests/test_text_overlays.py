import os
import unittest
from unittest.mock import patch, MagicMock
from PIL import Image
from fastapi.testclient import TestClient

from app.merger import (
    parse_color_rgba,
    render_text_overlays_image,
    merge_audio_segments_to_video
)
from app.main import app, ProjectRenderRequest


class TestTextOverlays(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join("tests", "temp_test_text")
        os.makedirs(self.test_dir, exist_ok=True)
        self.output_png = os.path.join(self.test_dir, "test_overlay.png")
        self.dummy_video = os.path.join(self.test_dir, "dummy_video.mp4")
        self.dummy_output = os.path.join(self.test_dir, "dummy_out.mp4")

        with open(self.dummy_video, "w") as f:
            f.write("dummy video data")

        self.client = TestClient(app)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            for f in os.listdir(self.test_dir):
                try:
                    os.remove(os.path.join(self.test_dir, f))
                except Exception:
                    pass
            try:
                os.rmdir(self.test_dir)
            except Exception:
                pass

    def test_parse_color_rgba(self):
        self.assertEqual(parse_color_rgba("#ffffff", 1.0), (255, 255, 255, 255))
        self.assertEqual(parse_color_rgba("#000000", 0.5), (0, 0, 0, 128))
        self.assertEqual(parse_color_rgba("#fff", 1.0), (255, 255, 255, 255))

    def test_render_text_overlays_image_success(self):
        items = [
            {
                "id": "text_1",
                "enabled": True,
                "text": "Đăng ký để không bỏ lỡ video mới",
                "x": 2.0,
                "y": 3.0,
                "font_size": 20,
                "color": "#000000",
                "bold": True,
                "italic": False,
                "shadow": False,
                "bg_enabled": True,
                "bg_color": "#FFFFFF",
                "bg_opacity": 1.0,
                "bg_radius": 6
            },
            {
                "id": "text_2",
                "enabled": True,
                "text": "Hạt Tiêu Vietsub",
                "x": 72.0,
                "y": 74.0,
                "font_size": 22,
                "color": "#FFFFFF",
                "bold": False,
                "italic": True,
                "shadow": True,
                "bg_enabled": False
            }
        ]

        result_path = render_text_overlays_image(items, 1280, 720, self.output_png)
        self.assertIsNotNone(result_path)
        self.assertTrue(os.path.exists(result_path))

        with Image.open(result_path) as img:
            self.assertEqual(img.size, (1280, 720))
            self.assertEqual(img.mode, "RGBA")
            # Verify non-empty alpha content
            extrema = img.getextrema()
            alpha_extrema = extrema[3]
            self.assertGreater(alpha_extrema[1], 0)

    def test_render_text_overlays_empty_or_disabled(self):
        # Empty list
        self.assertIsNone(render_text_overlays_image([], 1280, 720, self.output_png))
        # All disabled
        items = [{"enabled": False, "text": "Hello"}]
        self.assertIsNone(render_text_overlays_image(items, 1280, 720, self.output_png))
        # All blank text
        items = [{"enabled": True, "text": "   "}]
        self.assertIsNone(render_text_overlays_image(items, 1280, 720, self.output_png))

    @patch("app.merger.get_video_dimensions", return_value=(1280, 720))
    @patch("app.merger.get_video_duration", return_value=15.0)
    @patch("app.merger.check_video_has_audio", return_value=True)
    @patch("subprocess.run")
    def test_merge_with_text_overlays(self, mock_run, mock_has_audio, mock_dur, mock_dims):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc

        items = [
            {
                "id": "text_1",
                "enabled": True,
                "text": "Đăng ký để không bỏ lỡ video mới",
                "x": 2.0,
                "y": 3.0,
                "font_size": 20,
                "color": "#000000",
                "bg_enabled": True
            }
        ]

        merge_audio_segments_to_video(
            original_video_path=self.dummy_video,
            segments=[],
            output_video_path=self.dummy_output,
            burn_subtitles=False,
            text_overlays=items
        )

        self.assertTrue(mock_run.called)
        cmd = mock_run.call_args[0][0]

        # Verify that an overlay png was passed as an input
        has_png_input = any(arg.endswith("text_overlays.png") for arg in cmd)
        self.assertTrue(has_png_input, "text_overlays.png should be added as an input in cmd")

        # Verify filter_complex contains overlay=0:0
        filter_idx = cmd.index("-filter_complex")
        filter_str = cmd[filter_idx + 1]
        self.assertIn("overlay=0:0", filter_str)
        self.assertIn("libx264", cmd)

    def test_project_render_request_model(self):
        req = ProjectRenderRequest(
            voice="female_hoaimy",
            text_overlays=[
                {"id": "t1", "enabled": True, "text": "Test"}
            ]
        )
        self.assertIsNotNone(req.text_overlays)
        self.assertEqual(len(req.text_overlays), 1)
        self.assertEqual(req.text_overlays[0]["text"], "Test")


if __name__ == "__main__":
    unittest.main()
