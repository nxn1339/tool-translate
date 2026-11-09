import os
import sys
import unittest
import asyncio

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.capcut_tts import CAPCUT_VOICES
from app.tts import VOICE_PRESETS
from app.story_tts import (
    split_story_sentences,
    format_srt_timestamp,
    synthesize_story_session,
    rewrite_story_content
)


class TestStoryTTSStudio(unittest.TestCase):

    def test_voice_presets_pure_tiktok(self):
        """Ensure 100% of voices are CapCut/TikTok voices and Microsoft voices are purged."""
        self.assertNotIn("female_hoaimy", VOICE_PRESETS)
        self.assertNotIn("male_namminh", VOICE_PRESETS)
        self.assertNotIn("vi-VN-HoaiMyNeural", VOICE_PRESETS)
        self.assertNotIn("vi-VN-NamMinhNeural", VOICE_PRESETS)
        
        # Check all entries use capcut engine
        for k, v in VOICE_PRESETS.items():
            self.assertEqual(v.get("engine"), "capcut", f"Voice {k} is not capcut engine!")

        # Verify we have at least 15 female voices
        female_count = sum(1 for v in VOICE_PRESETS.values() if v.get("gender") == "female")
        self.assertGreaterEqual(female_count, 15, f"Expected at least 15 female voices, got {female_count}")
        print(f"Verified {len(VOICE_PRESETS)} TikTok voices ({female_count} female voices).")

    def test_split_story_sentences(self):
        """Test sentence splitting and chunking logic."""
        sample_story = (
            "Ngày xửa ngày xưa, ở một ngôi làng nhỏ ven sông Đáy, có một người phụ nữ tên là Mai.\n"
            "Bà sống một mình trong căn nhà gỗ đơn sơ, ngày ngày thêu thùa kiếm sống qua ngày! "
            "Một hôm nọ, trời đổ một cơn mưa rất to... Tiếng sấm chớp rền vang khắp cả bầu trời."
        )
        sentences = split_story_sentences(sample_story)
        self.assertGreaterEqual(len(sentences), 3)
        for s in sentences:
            self.assertIn("id", s)
            self.assertIn("text", s)
            self.assertIn("pause_after_ms", s)
            self.assertGreater(len(s["text"]), 0)
        print(f"Split test passed: produced {len(sentences)} coherent sentence chunks.")

    def test_format_srt_timestamp(self):
        """Test SRT timestamp formatting (00:00:00,000)."""
        self.assertEqual(format_srt_timestamp(0.0), "00:00:00,000")
        self.assertEqual(format_srt_timestamp(65.432), "00:01:05,432")
        self.assertEqual(format_srt_timestamp(3661.050), "01:01:01,050")

    def test_end_to_end_synthesize(self):
        """Test generating full audio and SRT file."""
        sample_story = (
            "Xin chào các bạn. Đây là chương trình đọc truyện tự động. "
            "Chúc các bạn có một buổi tối thật thư giãn và vui vẻ!"
        )
        result = asyncio.run(synthesize_story_session(
            text=sample_story,
            voice_key="capcut_cogaithoatngon",
            pause_ms=250,
            task_id="test_runner_session"
        ))
        
        self.assertEqual(result.get("status"), "ok")
        self.assertTrue(os.path.exists(result["mp3_path"]))
        self.assertTrue(os.path.exists(result["srt_path"]))
        self.assertGreater(os.path.getsize(result["mp3_path"]), 1000)
        self.assertGreater(os.path.getsize(result["srt_path"]), 50)
        
        with open(result["srt_path"], "r", encoding="utf-8") as f:
            srt_content = f.read()
            self.assertIn("-->", srt_content)
            self.assertIn("Xin chào các bạn", srt_content)
        
        print(f"E2E Synthesis passed! Duration: {result['total_duration_sec']}s, MP3 Size: {os.path.getsize(result['mp3_path'])} bytes.")


if __name__ == "__main__":
    unittest.main()

