import os
import sys
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding='utf-8')

import json
from app.merger import merge_audio_segments_to_video

project_id = "a98c6f85-5df1-400f-b634-7b28f5ff4f04"
project_dir = os.path.join("app", "projects", project_id)
input_video = os.path.join(project_dir, "input_video.mp4")
test_output_video = os.path.join(project_dir, "test_render_out.mp4")
segments_path = os.path.join(project_dir, "segments.json")
meta_path = os.path.join(project_dir, "project.json")

with open(segments_path, "r", encoding="utf-8") as f:
    segments = json.load(f)

with open(meta_path, "r", encoding="utf-8") as f:
    meta = json.load(f)

# Let's inspect what filter_script.txt is written when merge_audio_segments_to_video is called!
# We can test by calling merge_audio_segments_to_video on the first 5 segments
test_segs = segments[:5]
test_out = os.path.join(project_dir, "test_5seg.mp4")

try:
    merge_audio_segments_to_video(
        original_video_path=input_video,
        segments=test_segs,
        output_video_path=test_out,
        bg_volume=0.1,
        tts_volume=1.0,
        mask_box=meta.get("mask_box"),
        sub_box=meta.get("sub_box"),
        sub_styling=meta.get("sub_styling"),
        burn_subtitles=True,
        auto_extend_video=False,
        logo_box=None
    )
    print("SUCCESS! Output video generated, size:", os.path.getsize(test_out))
except Exception as e:
    print("ERROR:", e)
finally:
    if os.path.exists(test_out):
        pass # keep or check
