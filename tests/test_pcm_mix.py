import os
import time
import wave
import array
import json
import unittest
from app.merger import compute_elastic_timeline

class TestPCMMix(unittest.TestCase):
    def test_pcm_mix_benchmark(self):
        p_dir = "app/projects/a98c6f85-5df1-400f-b634-7b28f5ff4f04"
        seg_file = os.path.join(p_dir, "segments.json")
        if not os.path.exists(seg_file):
            self.skipTest("No test project found")

        with open(seg_file, "r", encoding="utf-8") as f:
            segs = json.load(f)

        for i, s in enumerate(segs):
            idx = s.get("index", s.get("id", i))
            candidate = os.path.join(p_dir, f"seg_{idx}_trimmed.wav")
            if os.path.exists(candidate):
                s["audio_path"] = candidate
            else:
                raw_candidate = os.path.join(p_dir, f"seg_{idx}_raw.mp3")
                if os.path.exists(raw_candidate):
                    s["audio_path"] = raw_candidate

        t0 = time.time()
        aligned = compute_elastic_timeline(segs)
        active = [s for s in aligned if os.path.exists(s.get("audio_path", "")) and s["audio_path"].endswith(".wav")]
        print(f"\nActive WAV segments: {len(active)} / {len(segs)}")

        max_end = max((float(s.get("play_end", 0.0)) for s in active), default=0.0)
        sample_rate = 24000
        total_samples = int((max_end + 2.0) * sample_rate)
        print(f"Total timeline duration: {max_end:.2f}s, buffer size: {total_samples * 4 / (1024*1024):.2f} MB")

        from app.merger import mix_timeline_audio_fast
        out_wav = os.path.join(p_dir, "test_mixed_output.wav")
        t0 = time.time()
        mix_timeline_audio_fast(p_dir, active, out_wav)
        t1 = time.time()
        print(f"PCM Mix time for {len(active)} segments: {t1 - t0:.2f}s")
        self.assertTrue(os.path.exists(out_wav))
        self.assertLess(t1 - t0, 5.0)

if __name__ == "__main__":
    unittest.main()

